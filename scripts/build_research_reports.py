"""Build documentation and executable notebooks from actual saved results."""
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'trained_models/metrics.json').read_text())
path=ROOT/'dataset/raw/Churn_Modelling.csv'
source='https://github.com/zunicd/Bank-Churn-Prediction/blob/master/Resources/Churn_Modelling.csv'
(ROOT/'dataset/README.md').write_text(f'''# Dataset provenance

Source: [{source}]({source}). Downloaded 7 November 2026 for academic demonstration. This is the widely circulated Churn_Modelling educational dataset; the mirror does not authenticate real banking provenance or establish redistribution rights. Review upstream licensing before publication or non-academic use.

SHA-256: `{hashlib.sha256(path.read_bytes()).hexdigest()}`

10,000 unique CustomerId records; 2,037 historical Exited outcomes. Fields: RowNumber, CustomerId, Surname, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited. IDs, surnames, row numbers and outcomes are excluded from model features. The UI uses pseudonymous display names. No synthetic transaction or service data is appended.

Limitations: no outcome date, prospective horizon, transaction history, complaints, service events, marketing eligibility, beginning-of-period cohort, intervention assignment, intervention cost, or retention outcomes. EstimatedSalary and Balance are snapshot values with unverified currency; the UI uses EUR as an illustrative presentation convention for France/Germany/Spain and does not assert source currency metadata.

`processed/eda.json` records missing counts, numerical summaries, geography counts and historical outcome rates. Splits are stratified 60/20/20 for fitting/validation/testing. After selection, the final estimator refits on 80%; the test 20% remains untouched by selection.
''',encoding='utf-8')
lines=['# Actual model comparison','',m['selection'],'','Validation results (not test performance):','','| Model | CV PR-AUC | Validation PR-AUC | Recall | Precision | F1 | F2 |','|---|---:|---:|---:|---:|---:|---:|']
for r in m['comparison']:
    v=r['validation']; lines.append(f"| {r['name']} | {r['cv_pr_auc']:.4f} | {v['pr_auc']:.4f} | {v['recall']:.4f} | {v['precision']:.4f} | {v['f1']:.4f} | {r['f2']:.4f} |")
lines+=['',f"Selected: **{m['selected']}**, binary operating threshold **{m['threshold']:.3f}**, version `{m['version']}`.",'','Held-out test results after final train+validation refit:','']
for k in ['accuracy','precision','recall','f1','roc_auc','pr_auc','brier']: lines.append(f"- {k}: {m['test'][k]:.4f}")
lines+=['',f"Confusion matrix (rows actual retained/churn, columns predicted retained/churn): `{m['test']['confusion_matrix']}`.",'','The recall-focused F2 rule can select a model with lower PR-AUC than another candidate. The threshold is a selected business proxy, not a measured intervention-cost optimum. Risk bands are separate configurable analyst triage labels. Held-out performance is academic evidence, not a prospective banking validation. See metrics.json for all curves and group results.']
(ROOT/'docs/model_comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def notebook(name,title,code):
    obj={'cells':[{'cell_type':'markdown','metadata':{},'source':[f'# {title}\n','Run from the notebooks directory with the project virtual environment. Outputs are generated on execution, never fabricated.']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(keepends=True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks').mkdir(exist_ok=True)
    (ROOT/'notebooks'/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
notebook('exploratory_data_analysis.ipynb','Banking churn exploratory analysis',"""import pandas as pd
from pathlib import Path
df = pd.read_csv('../dataset/raw/Churn_Modelling.csv')
display(df.describe(include='all'))
display(df.isna().sum())
display(df.groupby('Geography').Exited.agg(['count','mean']))
display(df.groupby(pd.cut(df.Age,[17,30,40,50,60,110])).Exited.agg(['count','mean']))
print('Historical exited rate:', df.Exited.mean())
print('No transaction or service behavior fields are available.')
""")
notebook('model_training.ipynb','Reproduce six-model training',"""import sys
from pathlib import Path
sys.path.insert(0,str(Path('../backend').resolve()))
from app.ml.train_model import train
train()
""")
notebook('model_evaluation.ipynb','Inspect actual evaluation and explanations',"""import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path('../backend').resolve()))
from app.ml.explainability import explain
from app.ml.predict import predict
from app.ml.preprocessing import FEATURES
metrics=json.loads(Path('../trained_models/metrics.json').read_text())
display(pd.DataFrame([{'name':r['name'],**{k:v for k,v in r['validation'].items() if isinstance(v,(float,int))}} for r in metrics['comparison']]))
display(metrics['test'])
display(metrics['fairness'])
customer=pd.read_csv('../dataset/raw/Churn_Modelling.csv').iloc[0][FEATURES].to_dict()
result=explain(customer)
assert abs(result['reconstructed_probability']-predict(customer)['probability'])<1e-5
display(pd.DataFrame(result['factors']))
""")
print('Generated provenance, actual model report and three notebooks.')
