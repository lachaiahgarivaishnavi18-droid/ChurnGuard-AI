import pandas as pd
import numpy as np
import shap
from .predict import artifact
from .preprocessing import FEATURES, CATEGORICAL

def explain(customer):
    a=artifact(); background=a['background'].copy(); row=pd.DataFrame([customer])[FEATURES]
    categories={col:sorted(background[col].unique()) for col in CATEGORICAL}
    def encode(frame):
        frame=frame.copy()
        for col,values in categories.items(): frame[col]=frame[col].map({v:i for i,v in enumerate(values)}).fillna(-1)
        return frame.astype(float).values
    def function(values):
        frame=pd.DataFrame(values,columns=FEATURES)
        for col,labels in categories.items(): frame[col]=frame[col].round().astype(int).map(dict(enumerate(labels))).fillna('Unknown')
        return a['model'].predict_proba(frame)[:,1]
    explainer=shap.KernelExplainer(function,encode(background),link='identity')
    values=np.asarray(explainer.shap_values(encode(row),nsamples=256,silent=True))[0]
    factors=sorted([{'feature':f,'value':customer[f],'contribution':float(v)} for f,v in zip(FEATURES,values)],key=lambda r:abs(r['contribution']),reverse=True)
    elevated=[f['feature'] for f in factors if f['contribution']>0][:3]
    summary='The model associates '+', '.join(elevated)+' with higher churn probability relative to the training background.' if elevated else 'No positive contribution is present relative to this background.'
    return {'method':'Kernel SHAP on exact calibrated pipeline','unit':'probability','baseline':float(explainer.expected_value),'factors':factors,'summary':summary,'reconstructed_probability':float(explainer.expected_value+values.sum()),'model_version':a['version'],'note':'Approximate associations relative to a 40-row training background; not causes'}
