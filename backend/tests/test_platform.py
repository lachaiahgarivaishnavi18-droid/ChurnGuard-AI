import pytest
from app.ml.predict import predict, risk, artifact
from app.ml.preprocessing import load_data, FEATURES
from app.ml.explainability import explain
from app.agents.supervisor import analyze
from app.schemas import CustomerFeatures
from pathlib import Path

def create(client,auth,feature):
    r=client.post('/api/customers',headers=auth,json={'name':'Research customer','external_id':'test-1','features':feature})
    assert r.status_code==201,r.json
    return r.json['id']

def test_data_and_artifact():
    df=load_data(Path(__file__).resolve().parents[2]/'dataset/raw/Churn_Modelling.csv')
    assert len(df)==10000 and df.CustomerId.is_unique
    assert set(artifact()['features'])==set(FEATURES)
    assert 'Exited' not in artifact()['features'] and 'CustomerId' not in artifact()['features']

def test_prediction_and_thresholds(feature,monkeypatch):
    p=predict(feature)
    assert 0<=p['probability']<=1 and p['model_version']
    monkeypatch.setenv('RISK_MEDIUM','.3'); monkeypatch.setenv('RISK_HIGH','.6')
    assert [risk(x) for x in [0,.299,.3,.599,.6,1]]==['Low','Low','Medium','Medium','High','High']

def test_exact_model_explanation(feature):
    p=predict(feature); e=explain(feature)
    assert abs(e['baseline']+sum(f['contribution'] for f in e['factors'])-p['probability'])<1e-5
    assert e['model_version']==p['model_version']
    assert len(e['factors'])==len(FEATURES)

def test_auth_isolation_and_validation(client,auth,feature):
    cid=create(client,auth,feature)
    assert client.get('/api/customers').status_code==401
    assert client.get('/api/customers',headers={'Authorization':'Bearer invalid.token.value'}).status_code==401
    other=client.post('/api/auth/register',json={'email':'other@example.test','password':'test-password-5678'}).json
    headers={'Authorization':'Bearer '+other['access_token']}
    for method,path,data in [('get',f'/api/customers/{cid}',None),('put',f'/api/customers/{cid}',{'features':feature}),('delete',f'/api/customers/{cid}',None),('post',f'/api/agents/analyze/{cid}',{}),('post',f'/api/simulate/{cid}',{'Balance':0})]:
        assert getattr(client,method)(path,headers=headers,json=data).status_code==404
    assert client.get('/api/customers',headers=headers).json['total']==0
    assert client.get('/api/admin/audit',headers=auth).status_code==403
    bad={**feature,'Age':-1}
    assert client.post('/api/predict',headers=auth,json={'features':bad}).status_code==422
    assert client.post('/api/predict',headers=auth,json={'features':{**feature,'Balance':float('inf')}}).status_code==422
    assert client.post('/api/simulate/'+str(cid),headers=auth,json={'Gender':'Male'}).status_code==422
    assert client.post('/api/auth/logout',headers=auth).status_code==200
    assert client.get('/api/customers',headers=auth).status_code==401

def test_workflow_persistence_feedback_and_delete(client,auth,feature):
    cid=create(client,auth,feature)
    response=client.post(f'/api/agents/analyze/{cid}',headers=auth)
    assert response.status_code==200,response.json
    report=response.json['report']; eid=response.json['execution_id']
    assert len(report['agent_logs'])==6
    assert {x['agent'] for x in report['agent_logs']}=={'customer_analysis','prediction','explanation','segmentation','retention','reporting'}
    assert report['analysis']['active_membership'] is False
    assert report['segment']['id']>=0
    assert all(s['estimated_retention_impact'] is None and s['requires_human_review'] for s in report['strategies'])
    assert client.get('/api/agents/report/'+eid,headers=auth).json['status']=='completed'
    assert client.get('/api/predictions/'+str(cid),headers=auth).json['items']
    rec=client.get('/api/recommendations/'+str(cid),headers=auth).json['items'][0]
    assert client.post(f"/api/recommendations/{rec['id']}/feedback",headers=auth,json={'decision':'modified'}).status_code==422
    assert client.post(f"/api/recommendations/{rec['id']}/feedback",headers=auth,json={'decision':'approved','note':'Reviewed evidence'}).status_code==200
    simulation=client.post('/api/simulate/'+str(cid),headers=auth,json={'IsActiveMember':1})
    assert simulation.status_code==200 and 'difference' in simulation.json
    assert client.get('/api/customers/'+str(cid),headers=auth).json['features']['IsActiveMember']==0
    assert client.delete('/api/customers/'+str(cid),headers=auth).status_code==204
    assert client.get('/api/customers/'+str(cid),headers=auth).status_code==404

def test_demo_analytics_filters(client,auth):
    assert client.post('/api/customers/import-demo',headers=auth).json['imported']==300
    summary=client.get('/api/analytics/summary',headers=auth).json
    assert summary['total']==300 and sum(summary['risk'].values())==300
    assert summary['retention_rate'] is None
    subset=client.get('/api/customers?geography=France&age_min=40&balance_min=1',headers=auth).json
    assert all(c['features']['Geography']=='France' and c['features']['Age']>=40 and c['features']['Balance']>=1 for c in subset['items'])
    assert client.get('/api/customers?age_min=invalid',headers=auth).status_code==422

def test_preprocessing_train_only_imputation(tmp_path,feature):
    import pandas as pd
    import numpy as np
    from app.ml.preprocessing import preprocessor
    train=pd.DataFrame([feature,{**feature,'Balance':20000}])
    pipeline=preprocessor().fit(train)
    missing=pd.DataFrame([{**feature,'Balance':np.nan}])
    transformed=pipeline.transform(missing)
    assert np.isfinite(transformed).all()
    assert pipeline.named_transformers_['numeric'].named_steps['simpleimputer'].statistics_[3]==50000
    path=tmp_path/'invalid.csv'; pd.DataFrame([feature]).to_csv(path,index=False)
    with pytest.raises(ValueError): load_data(path)

def test_llm_failure_uses_grounded_fallback(feature,monkeypatch):
    import requests
    from app.agents import reporting_agent
    from app.agents.customer_analysis_agent import run as analysis
    from app.agents.churn_prediction_agent import run as prediction
    from app.agents.churn_explanation_agent import run as explanation
    from app.agents.segmentation_agent import run as segmentation
    from app.agents.retention_strategy_agent import run as retention
    state={'customer':feature}
    for function in [analysis,prediction,explanation,segmentation,retention]: state.update(function(state))
    monkeypatch.setenv('LLM_API_KEY','test-key-not-real')
    def fail(*args,**kwargs): raise requests.Timeout('simulated timeout')
    monkeypatch.setattr(reporting_agent.requests,'post',fail)
    report=reporting_agent.run(state)['report']
    assert report['narrative_mode'].startswith('deterministic fallback')
    assert report['prediction']==state['prediction'] and 'llm_draft' not in report
