import os
from pathlib import Path
from functools import lru_cache
import joblib
import pandas as pd
from .preprocessing import FEATURES

@lru_cache
def artifact():
    return joblib.load(Path(__file__).resolve().parents[3]/'trained_models/churn_model.pkl')

def risk(p):
    medium=float(os.getenv('RISK_MEDIUM','.3')); high=float(os.getenv('RISK_HIGH','.6'))
    if not 0<medium<high<1: raise ValueError('Invalid risk thresholds')
    return 'High' if p>=high else 'Medium' if p>=medium else 'Low'

def predict(customer):
    a=artifact(); p=float(a['model'].predict_proba(pd.DataFrame([customer])[FEATURES])[0,1])
    return {'probability':p,'churn':p>=a['threshold'],'risk':risk(p),'model_version':a['version'],'threshold':a['threshold'],'confidence':'Calibrated model probability; not an individual confidence interval'}
