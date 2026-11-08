import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from app import create_app
from app.models import db

@pytest.fixture
def client():
    app=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':'sqlite://','JWT_SECRET_KEY':'testing-secret-at-least-thirty-two-characters','RATELIMIT_ENABLED':False})
    with app.app_context(): db.create_all()
    with app.test_client() as client: yield client
    with app.app_context(): db.drop_all()

@pytest.fixture
def auth(client):
    response=client.post('/api/auth/register',json={'email':'analyst@example.test','password':'test-password-1234'})
    return {'Authorization':'Bearer '+response.json['access_token']}

@pytest.fixture
def feature():
    return {'CreditScore':650,'Geography':'France','Gender':'Female','Age':40,'Tenure':5,'Balance':80000,'NumOfProducts':1,'HasCrCard':1,'IsActiveMember':0,'EstimatedSalary':75000}
