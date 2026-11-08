from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pandas as pd

NUMERIC = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']
CATEGORICAL = ['Geography', 'Gender']
FEATURES = NUMERIC + CATEGORICAL

def load_data(path):
    df = pd.read_csv(path)
    required = set(FEATURES + ['CustomerId', 'Exited'])
    if not required.issubset(df):
        raise ValueError(f'Missing columns: {required - set(df.columns)}')
    df = df.drop_duplicates(subset=['CustomerId'])
    df = df.dropna(subset=['Exited'])
    if not df.Exited.isin([0, 1]).all():
        raise ValueError('Exited must be binary')
    return df

def preprocessor():
    return ColumnTransformer([
        ('numeric', make_pipeline(SimpleImputer(strategy='median'), StandardScaler()), NUMERIC),
        ('category', make_pipeline(SimpleImputer(strategy='most_frequent'), OneHotEncoder(handle_unknown='ignore', sparse_output=False)), CATEGORICAL)
    ])
