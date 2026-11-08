import json, uuid
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from flask import Blueprint, request, jsonify, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from ..models import db, User, Customer, Account, Execution, Prediction, Explanation, Segment, Recommendation, AgentLog, Feedback, RevokedToken
from ..schemas import CustomerFeatures
from ..ml.predict import predict, artifact, risk
from ..ml.preprocessing import FEATURES
from ..agents.supervisor import analyze
from .. import limiter

api=Blueprint('api',__name__,url_prefix='/api')

def body():
    value=request.get_json(silent=True)
    if not isinstance(value,dict): abort(400,description='JSON object required')
    return value
def owner(): return int(get_jwt_identity())
def customer(cid): return Customer.query.filter_by(id=cid,owner_id=owner()).first_or_404()
def features(value):
    try: return CustomerFeatures.model_validate(value).model_dump()
    except ValidationError as e: abort(422,description=str(e))
def owned_query(model): return model.query.join(Customer,model.customer_id==Customer.id).filter(Customer.owner_id==owner())

@api.errorhandler(400)
@api.errorhandler(404)
@api.errorhandler(422)
def invalid(e): return jsonify(error=e.description),e.code

@api.get('/health')
def health(): return {'status':'ok'}

@api.get('/health/ready')
def ready():
    from sqlalchemy import text
    try:
        db.session.execute(text('SELECT 1'))
        return {'status':'ready','database':'postgresql' if db.engine.dialect.name=='postgresql' else 'local development','model_version':artifact()['version']}
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Readiness check failed')
        return {'status':'unavailable'},503

@api.get('/config')
@jwt_required()
def config():
    import os
    return {'risk_medium':float(os.getenv('RISK_MEDIUM','.3')),'risk_high':float(os.getenv('RISK_HIGH','.6'))}

@api.post('/auth/register')
@limiter.limit('10 per minute')
def register():
    data=body(); email=str(data.get('email','')).strip().lower(); password=data.get('password','')
    if '@' not in email or len(email)>254 or not isinstance(password,str) or not 12<=len(password)<=128: return {'error':'Valid email and password of 12–128 characters required'},422
    user=User(email=email,password_hash=generate_password_hash(password),role='analyst'); db.session.add(user)
    try: db.session.commit()
    except IntegrityError: db.session.rollback(); return {'error':'Email already registered'},409
    return {'access_token':create_access_token(identity=str(user.id)),'user':{'email':email,'role':user.role}},201

@api.post('/auth/login')
@limiter.limit('10 per minute')
def login():
    data=body(); user=User.query.filter_by(email=str(data.get('email','')).lower().strip()).first()
    if not user or not isinstance(data.get('password'),str) or not check_password_hash(user.password_hash,data['password']): return {'error':'Invalid credentials'},401
    return {'access_token':create_access_token(identity=str(user.id)),'user':{'email':user.email,'role':user.role}}

@api.post('/auth/logout')
@jwt_required()
def logout():
    db.session.add(RevokedToken(jti=get_jwt()['jti'])); db.session.commit(); return {'status':'logged out'}

def scored(rows):
    if not rows: return []
    a=artifact(); frame=pd.DataFrame([r.features for r in rows])[FEATURES]; probabilities=a['model'].predict_proba(frame)[:,1]
    seg=a['segmentation']; from ..ml.segmentation import SEGMENT_FEATURES
    labels=seg['model'].predict(seg['scaler'].transform(frame[SEGMENT_FEATURES]))
    return [{**r.public(),'probability':float(p),'risk':risk(float(p)),'segment':seg['profiles'][int(label)]['name']} for r,p,label in zip(rows,probabilities,labels)]

def filtered():
    rows=scored(Customer.query.filter_by(owner_id=owner()).order_by(Customer.id).all())
    q=request.args.get('q','').lower()
    for key in ['age','tenure','balance','probability']:
        for bound in ['min','max']:
            value=request.args.get(f'{key}_{bound}')
            if value is not None:
                try: v=float(value)
                except ValueError: abort(422,description='Invalid numeric filter')
                field={'age':'Age','tenure':'Tenure','balance':'Balance'}.get(key)
                rows=[r for r in rows if ((r['features'][field] if field else r['probability'])>=v if bound=='min' else (r['features'][field] if field else r['probability'])<=v)]
    return [r for r in rows if (not q or q in (r['name']+' '+r['external_id']).lower()) and (not request.args.get('risk') or r['risk']==request.args['risk']) and (not request.args.get('geography') or r['features']['Geography']==request.args['geography']) and (not request.args.get('segment') or r['segment']==request.args['segment']) and (not request.args.get('products') or str(r['features']['NumOfProducts'])==request.args['products'])]

@api.get('/customers')
@jwt_required()
def customers():
    rows=filtered()
    try: page=max(1,int(request.args.get('page',1))); size=min(500,max(1,int(request.args.get('page_size',100))))
    except ValueError: abort(422,description='Invalid pagination')
    return {'items':rows[(page-1)*size:page*size],'total':len(rows)}

@api.get('/customers/<int:cid>')
@jwt_required()
def detail(cid): return scored([customer(cid)])[0]

@api.post('/customers')
@jwt_required()
def create_customer():
    data=body(); name=str(data.get('name','')).strip(); external=str(data.get('external_id','')).strip()
    if not name or len(name)>120 or not external or len(external)>64: abort(422,description='Name and external_id required within length limits')
    c=Customer(owner_id=owner(),name=name,external_id=external,features=features(data.get('features',{})),source='analyst supplied'); db.session.add(c)
    try: db.session.flush(); db.session.add(Account(customer_id=c.id,snapshot={k:c.features[k] for k in ['Balance','NumOfProducts','HasCrCard']})); db.session.commit()
    except IntegrityError: db.session.rollback(); return {'error':'Duplicate external ID'},409
    return c.public(),201

@api.put('/customers/<int:cid>')
@jwt_required()
def update(cid):
    c=customer(cid); data=body(); c.features=features(data.get('features',{}))
    if 'name' in data:
        if not isinstance(data['name'],str) or not 1<=len(data['name'])<=120: abort(422,description='Invalid name')
        c.name=data['name']
    account=Account.query.filter_by(customer_id=cid).first()
    if account: account.snapshot={k:c.features[k] for k in ['Balance','NumOfProducts','HasCrCard']}
    db.session.commit(); return c.public()

@api.delete('/customers/<int:cid>')
@jwt_required()
def delete(cid):
    c=customer(cid)
    # Explicit ordered removal also supports local SQLite without FK cascades.
    recs=Recommendation.query.filter_by(customer_id=cid).all()
    for r in recs: Feedback.query.filter_by(recommendation_id=r.id).delete()
    Recommendation.query.filter_by(customer_id=cid).delete()
    for e in Execution.query.filter_by(customer_id=cid): AgentLog.query.filter_by(execution_id=e.id).delete()
    Execution.query.filter_by(customer_id=cid).delete()
    for p in Prediction.query.filter_by(customer_id=cid): Explanation.query.filter_by(prediction_id=p.id).delete()
    Prediction.query.filter_by(customer_id=cid).delete(); Segment.query.filter_by(customer_id=cid).delete(); Account.query.filter_by(customer_id=cid).delete()
    db.session.delete(c); db.session.commit(); return '',204

@api.post('/customers/import-demo')
@jwt_required()
def demo():
    if Customer.query.filter_by(owner_id=owner()).count(): return {'error':'Demo import requires an empty customer list'},409
    path=Path(__file__).resolve().parents[3]/'dataset/raw/Churn_Modelling.csv'
    df=pd.read_csv(path).sample(300,random_state=42)
    for _,row in df.iterrows():
        f=features({k:row[k] for k in FEATURES})
        c=Customer(owner_id=owner(),external_id=str(row.CustomerId),name='Customer '+str(row.CustomerId)[-5:],features=f,historical_churn=bool(row.Exited),source='Public academic dataset; pseudonymous demo'); db.session.add(c); db.session.flush()
        db.session.add(Account(customer_id=c.id,snapshot={k:f[k] for k in ['Balance','NumOfProducts','HasCrCard']}))
    db.session.commit(); return {'imported':len(df)}

@api.post('/predict')
@jwt_required()
def prediction():
    data=body()
    if data.get('customer_id'):
        c=customer(data['customer_id']); out=predict(c.features); db.session.add(Prediction(customer_id=c.id,output=out)); db.session.commit(); return out
    return predict(features(data.get('features',{})))

@api.post('/simulate/<int:cid>')
@jwt_required()
def simulate(cid):
    c=customer(cid); changes=body(); allowed={'IsActiveMember','NumOfProducts','Tenure','Balance'}
    if not changes or set(changes)-allowed: abort(422,description='Only activity, products, tenure and balance may be simulated')
    original=predict(c.features); simulated=predict(features({**c.features,**changes}))
    return {'original':original,'simulated':simulated,'difference':simulated['probability']-original['probability'],'note':'Model simulation, not a causal estimate; customer data was not changed'}

@api.get('/predictions')
@api.get('/predictions/<int:cid>')
@jwt_required()
def history(cid=None):
    query=owned_query(Prediction)
    if cid: customer(cid); query=query.filter(Prediction.customer_id==cid)
    return {'items':[{'id':p.id,'customer_id':p.customer_id,'timestamp':p.created_at.isoformat(),**p.output} for p in query.order_by(Prediction.id.desc()).limit(100)]}

@api.post('/agents/analyze/<int:cid>')
@jwt_required()
def agents(cid):
    c=customer(cid); e=Execution(id=str(uuid.uuid4()),customer_id=c.id,owner_id=owner(),status='running'); db.session.add(e); db.session.commit()
    try:
        report=analyze(c.features); report.update(customer_id=c.id,timestamp=datetime.now(timezone.utc).isoformat()); e.report=report; e.status='completed'
        p=Prediction(customer_id=c.id,output=report['prediction']); db.session.add(p); db.session.flush()
        db.session.add(Explanation(prediction_id=p.id,output=report['explanation'])); db.session.add(Segment(customer_id=c.id,output=report['segment']))
        for s in report['strategies']: db.session.add(Recommendation(customer_id=c.id,execution_id=e.id,output=s))
        for log in report['agent_logs']: db.session.add(AgentLog(execution_id=e.id,output=log))
        db.session.commit()
    except Exception:
        db.session.rollback(); e=db.session.get(Execution,e.id); e.status='failed'; db.session.commit(); current_app.logger.exception('Workflow failed: %s',e.id)
        return {'error':'Analysis failed; consult execution logs','execution_id':e.id},503
    return {'execution_id':e.id,'status':e.status,'report':report}

@api.get('/agents/status/<eid>')
@api.get('/agents/report/<eid>')
@jwt_required()
def execution(eid):
    e=Execution.query.filter_by(id=eid,owner_id=owner()).first_or_404()
    return {'execution_id':e.id,'status':e.status,'report':e.report}

@api.get('/recommendations')
@api.get('/recommendations/<int:cid>')
@jwt_required()
def recommendations(cid=None):
    query=owned_query(Recommendation)
    if cid: customer(cid); query=query.filter(Recommendation.customer_id==cid)
    return {'items':[{'id':r.id,'customer_id':r.customer_id,'status':r.status,**r.output} for r in query.order_by(Recommendation.id.desc()).limit(200)]}

@api.post('/recommendations/<int:rid>/feedback')
@jwt_required()
def feedback(rid):
    r=owned_query(Recommendation).filter(Recommendation.id==rid).first_or_404(); data=body(); decision=data.get('decision'); note=data.get('note','')
    if decision not in ['approved','rejected','modified'] or not isinstance(note,str) or len(note)>2000 or (decision=='modified' and not note.strip()): abort(422,description='Decision must be approved, rejected, or modified; modifications require a note')
    r.status=decision; db.session.add(Feedback(recommendation_id=rid,user_id=owner(),decision=decision,note=note)); db.session.commit(); return {'status':decision}

@api.get('/analytics/summary')
@api.get('/analytics/churn')
@api.get('/analytics/segments')
@jwt_required()
def analytics():
    rows=filtered(); n=len(rows); known=[r for r in rows if r['historical_churn'] is not None]; churn=sum(r['historical_churn'] for r in known)
    def groups(key):
        out={}
        for r in rows:
            label=str(key(r)); item=out.setdefault(label,{'count':0,'historical_churn':0,'known_outcomes':0}); item['count']+=1
            if r['historical_churn'] is not None: item['known_outcomes']+=1; item['historical_churn']+=int(r['historical_churn'])
        return out
    return {'total':n,'historical_churned':churn,'historical_known':len(known),'historical_churn_rate':churn/len(known) if known else None,'retention_rate':None,'retention_note':'No beginning-of-period cohort or longitudinal outcomes available','active':sum(r['features']['IsActiveMember'] for r in rows),'risk':{risk:sum(r['risk']==risk for r in rows) for risk in ['High','Medium','Low']},'average_probability':sum(r['probability'] for r in rows)/n if n else 0,'geography':groups(lambda r:r['features']['Geography']),'age':groups(lambda r:f"{int(r['features']['Age']//10)*10}s"),'tenure':groups(lambda r:r['features']['Tenure']),'products':groups(lambda r:r['features']['NumOfProducts']),'segments':groups(lambda r:r['segment'])}

@api.get('/model/metrics')
@api.get('/model/feature-importance')
@api.get('/model/status')
@jwt_required()
def metrics():
    path=Path(__file__).resolve().parents[3]/'trained_models/metrics.json'
    if not path.exists(): return {'status':'not trained'},503
    out=json.loads(path.read_text())
    summary=path.parent/'shap_summary.json'
    if summary.exists(): out['shap_summary']=json.loads(summary.read_text())
    return out

@api.get('/admin/audit')
@jwt_required()
def audit():
    user=db.session.get(User,owner())
    if user.role!='admin': return {'error':'Administrator role required'},403
    return {'items':[{'execution_id':e.id,'status':e.status,'timestamp':e.created_at.isoformat()} for e in Execution.query.filter_by(owner_id=owner()).order_by(Execution.created_at.desc()).limit(100)]}
