"""Run from backend: python -m app.ml.train_model"""
import json, hashlib
from pathlib import Path
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier
from .preprocessing import load_data, preprocessor, FEATURES
from .evaluate_model import evaluate
from .segmentation import train_segments

ROOT = Path(__file__).resolve().parents[3]

def train():
    path = ROOT/'dataset/raw/Churn_Modelling.csv'
    df = load_data(path)
    X, y = df[FEATURES], df.Exited
    train_idx, test_idx = train_test_split(np.arange(len(df)), test_size=.2, stratify=y, random_state=42)
    fit_idx, val_idx = train_test_split(train_idx, test_size=.25, stratify=y.iloc[train_idx], random_state=42)
    candidates = {
        'Logistic Regression': (LogisticRegression(max_iter=1000), {'model__C':[.1,1]}),
        'Decision Tree': (DecisionTreeClassifier(random_state=42), {'model__max_depth':[4,7]}),
        'Random Forest': (RandomForestClassifier(n_estimators=120, n_jobs=2, random_state=42), {'model__max_depth':[6,10]}),
        'XGBoost': (XGBClassifier(n_estimators=120, n_jobs=2, random_state=42, eval_metric='logloss'), {'model__max_depth':[2,4]}),
        'Gradient Boosting': (GradientBoostingClassifier(random_state=42), {'model__max_depth':[2,3]}),
        'Support Vector Machine': (SVC(probability=True,random_state=42), {'model__C':[.5,1]})
    }
    results, models = [], {}
    for name,(model,grid) in candidates.items():
        search = GridSearchCV(Pipeline([('preprocess',preprocessor()),('model',model)]), grid, scoring='average_precision', cv=StratifiedKFold(3,shuffle=True,random_state=42), n_jobs=1)
        search.fit(X.iloc[fit_idx], y.iloc[fit_idx])
        calibrated = CalibratedClassifierCV(search.best_estimator_, method='sigmoid', cv=3)
        calibrated.fit(X.iloc[fit_idx], y.iloc[fit_idx])
        p = calibrated.predict_proba(X.iloc[val_idx])[:,1]
        thresholds = np.arange(.15,.66,.025)
        # Maximize F2 on validation: recall receives four times precision's weight.
        scores=[]
        for t in thresholds:
            m=evaluate(y.iloc[val_idx],p,float(t)); scores.append(5*m['precision']*m['recall']/(4*m['precision']+m['recall']+1e-12))
        threshold=float(thresholds[np.argmax(scores)])
        metrics=evaluate(y.iloc[val_idx],p,threshold)
        results.append({'name':name,'cv_pr_auc':float(search.best_score_),'parameters':search.best_params_,'threshold':threshold,'validation':metrics,'f2':max(scores)})
        models[name]=calibrated
        print(name, 'validation PR-AUC', round(metrics['pr_auc'],4), flush=True)
    winner=max(results,key=lambda r:(r['f2'],r['validation']['pr_auc']))
    selected=models[winner['name']]
    # Refit only after model and operating threshold have been selected.
    selected.fit(X.iloc[train_idx],y.iloc[train_idx])
    test_p=selected.predict_proba(X.iloc[test_idx])[:,1]
    fairness={}
    for col in ['Gender','Geography']:
        fairness[col]={}
        for group in df.iloc[test_idx][col].unique():
            mask=df.iloc[test_idx][col].values==group
            fairness[col][group]={'n':int(mask.sum()),**evaluate(y.iloc[test_idx].values[mask],test_p[mask],winner['threshold'])}
    importance=permutation_importance(selected,X.iloc[val_idx],y.iloc[val_idx],n_repeats=3,scoring='average_precision',random_state=42)
    # Importance uses training-partition rows after final refit; descriptive, not held-out evidence.
    version=hashlib.sha256(path.read_bytes()).hexdigest()[:12]+'-v1'
    artifact={'model':selected,'features':FEATURES,'threshold':winner['threshold'],'version':version,'background':X.iloc[fit_idx].sample(40,random_state=42),'segmentation':train_segments(X.iloc[train_idx]),'training_ids':df.iloc[train_idx].CustomerId.tolist()}
    out=ROOT/'trained_models'; out.mkdir(exist_ok=True)
    joblib.dump(artifact,out/'churn_model.pkl')
    report={'selected':winner['name'],'version':version,'threshold':winner['threshold'],'selection':'Validation F2 then PR-AUC; sigmoid calibration via train-only CV','split':{'fit':len(fit_idx),'validation':len(val_idx),'test':len(test_idx)},'comparison':results,'test':evaluate(y.iloc[test_idx],test_p,winner['threshold']),'fairness':fairness,'importance':[{'feature':f,'importance':float(v)} for f,v in zip(FEATURES,importance.importances_mean)],'importance_scope':'Descriptive refitted training partition','limitations':['Snapshot data: no transaction, complaint, or intervention outcomes','No prospective or causal validation','Group metrics are an audit, not proof of fairness']}
    (out/'metrics.json').write_text(json.dumps(report,indent=2))
    eda={'rows':len(df),'missing':df.isna().sum().to_dict(),'churn_rate':float(y.mean()),'geography':df.groupby('Geography').Exited.agg(['count','mean']).to_dict(),'numeric':df.describe().to_dict(),'split_note':'Customer IDs, surnames, RowNumber and target excluded from features; no SMOTE, no synthetic records'}
    (ROOT/'dataset/processed').mkdir(exist_ok=True)
    (ROOT/'dataset/processed/eda.json').write_text(json.dumps(eda,indent=2))
    print('Selected:',winner['name'],'Test:',report['test']['pr_auc'],flush=True)

if __name__=='__main__':
    train()
    import runpy
    runpy.run_path(str(ROOT/'scripts/global_explanations.py'),run_name='__main__')
