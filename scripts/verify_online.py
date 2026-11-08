"""Exercise the live app with disposable, generated QA accounts and public sample data.

No real customer data, user passwords, signing secrets or access tokens are logged.
Set CHURNGUARD_URL to override the production frontend URL.
"""
import json
import os
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
import requests

BASE=os.getenv('CHURNGUARD_URL','https://churnguard-ai-omega.vercel.app').rstrip('/')
results=[]

def call(session,method,path,body=None,expected=200):
    response=session.request(method,BASE+'/api'+path,json=body,timeout=120)
    if response.status_code!=expected:
        raise AssertionError(f'{method} {path}: expected {expected}, got {response.status_code}: '+response.text[:500])
    return response.json() if response.status_code!=204 else None

def passed(name):
    results.append(name)
    print('PASS '+name,flush=True)

def main():
    primary=requests.Session()
    ready=call(primary,'GET','/health/ready')
    assert ready['database']=='postgresql' and ready['status']=='ready'
    passed('Frontend proxy, PostgreSQL and saved model readiness')
    email='qa-'+uuid.uuid4().hex+'@example.invalid'
    password=secrets.token_urlsafe(24)
    registration=call(primary,'POST','/auth/register',{'email':email,'password':password},201)
    assert registration['user']['role']=='analyst'
    login=call(primary,'POST','/auth/login',{'email':email,'password':password})
    primary.headers['Authorization']='Bearer '+login['access_token']
    passed('Registration and password login through frontend')
    assert call(primary,'POST','/customers/import-demo')['imported']==300
    summary=call(primary,'GET','/analytics/summary')
    assert summary['total']==300 and sum(summary['risk'].values())==300
    assert len(call(primary,'GET','/customers?geography=France&age_min=50')['items'])>0
    passed('PostgreSQL persistence, demo import, analytics and filters')
    customer=call(primary,'GET','/customers?risk=High')['items'][0]
    cid=customer['id']
    prediction=call(primary,'POST','/predict',{'customer_id':cid})
    assert 0<=prediction['probability']<=1
    passed('Real saved-model churn prediction and history persistence')
    execution=call(primary,'POST',f'/agents/analyze/{cid}')
    report=execution['report']
    assert len(report['agent_logs'])==6
    explanation=report['explanation']
    assert abs(explanation['baseline']+sum(f['contribution'] for f in explanation['factors'])-report['prediction']['probability'])<1e-5
    assert call(primary,'GET','/agents/report/'+execution['execution_id'])['status']=='completed'
    passed('All six LangGraph agents, exact-model SHAP and persisted reporting')
    simulation=call(primary,'POST',f'/simulate/{cid}',{'NumOfProducts':2,'IsActiveMember':1})
    assert 'difference' in simulation
    unchanged=call(primary,'GET',f'/customers/{cid}')
    assert unchanged['features']==customer['features']
    passed('What-if simulation without changing customer records')
    recommendation=call(primary,'GET',f'/recommendations/{cid}')['items'][0]
    rid=recommendation['id']
    call(primary,'POST',f'/recommendations/{rid}/feedback',{'decision':'approved','note':'Disposable automated online QA review; no customer outreach.'})
    assert next(r for r in call(primary,'GET',f'/recommendations/{cid}')['items'] if r['id']==rid)['status']=='approved'
    passed('Retention recommendation generation and human-review persistence')
    metrics=call(primary,'GET','/model/metrics')
    assert len(metrics['comparison'])==6 and metrics['shap_summary']['sample_size']==40
    assert 'Age group' in metrics['fairness']
    assert call(primary,'GET','/predictions')['items']
    passed('Six-model comparison, SHAP summary, group audits and report data')
    secondary=requests.Session()
    other=call(secondary,'POST','/auth/register',{'email':'qa-isolation-'+uuid.uuid4().hex+'@example.invalid','password':secrets.token_urlsafe(24)},201)
    secondary.headers['Authorization']='Bearer '+other['access_token']
    call(secondary,'GET',f'/customers/{cid}',expected=404)
    call(secondary,'GET','/agents/report/'+execution['execution_id'],expected=404)
    assert call(secondary,'GET','/customers')['total']==0
    passed('Cross-account customer and report isolation')
    call(primary,'POST','/auth/logout')
    call(primary,'GET','/customers',expected=401)
    call(secondary,'POST','/auth/logout')
    passed('Persistent JWT logout revocation')
    output={'url':BASE,'verified_at':datetime.now(timezone.utc).isoformat(),'database':ready['database'],'model_version':ready['model_version'],'checks':results,'count':len(results),'llm_mode':report['narrative_mode'],'note':'Generated QA accounts contain only public academic demonstration records. No real customer or account action occurred.'}
    path=Path(__file__).resolve().parents[1]/'docs/online-verification.json'
    path.write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(f'All {len(results)} online checks passed. No credentials recorded.',flush=True)

if __name__=='__main__': main()
