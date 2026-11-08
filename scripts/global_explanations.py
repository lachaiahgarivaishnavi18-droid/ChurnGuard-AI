"""Produce a small held-out SHAP sample and age-group audit, using the saved model."""
import sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.ml.predict import artifact
from app.ml.preprocessing import load_data,FEATURES
from app.ml.explainability import explain
from app.ml.evaluate_model import evaluate
ROOT=Path(__file__).resolve().parents[1]
a=artifact(); df=load_data(ROOT/'dataset/raw/Churn_Modelling.csv')
test=df.loc[~df.CustomerId.isin(a['training_ids'])]
sample=test.sample(40,random_state=11)
results=[]
for _,row in sample.iterrows():
    e=explain(row[FEATURES].to_dict())
    results.append({'factors':e['factors'],'baseline':e['baseline'],'probability':e['reconstructed_probability']})
summary={'sample_size':len(results),'scope':'40 randomly sampled held-out test customers; descriptive approximate Kernel SHAP','model_version':a['version'],'rows':results,'importance':[{'feature':f,'mean_abs_shap':float(np.mean([abs(next(v['contribution'] for v in r['factors'] if v['feature']==f)) for r in results]))} for f in FEATURES]}
(ROOT/'trained_models/shap_summary.json').write_text(json.dumps(summary,indent=2))
path=ROOT/'trained_models/metrics.json'; metrics=json.loads(path.read_text())
age_groups={}
for label,mask in [('18–34',test.Age<35),('35–49',(test.Age>=35)&(test.Age<50)),('50+',test.Age>=50)]:
    group=test.loc[mask]; p=a['model'].predict_proba(group[FEATURES])[:,1]
    age_groups[label]={'n':len(group),**evaluate(group.Exited,p,a['threshold'])}
metrics['fairness']['Age group']=age_groups
path.write_text(json.dumps(metrics,indent=2))
print('Saved 40 held-out SHAP explanations and age-group audit.')
