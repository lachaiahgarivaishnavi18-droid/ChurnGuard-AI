"""Explicit public dataset download with provenance. No credentials required."""
from pathlib import Path
import hashlib, json, urllib.request
ROOT=Path(__file__).resolve().parents[1]
url='https://raw.githubusercontent.com/zunicd/Bank-Churn-Prediction/master/Resources/Churn_Modelling.csv'
path=ROOT/'dataset/raw/Churn_Modelling.csv'
path.parent.mkdir(parents=True,exist_ok=True)
urllib.request.urlretrieve(url,path)
print(json.dumps({'source':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size},indent=2))
