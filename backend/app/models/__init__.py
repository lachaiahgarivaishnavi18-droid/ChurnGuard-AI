from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

def now(): return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(254),unique=True,nullable=False)
    password_hash=db.Column(db.String(256),nullable=False)
    role=db.Column(db.String(20),nullable=False,default='analyst')
    created_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)

class Customer(db.Model):
    __tablename__='bank_customers'
    id=db.Column(db.Integer,primary_key=True)
    owner_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False,index=True)
    external_id=db.Column(db.String(64),nullable=False)
    name=db.Column(db.String(120),nullable=False)
    features=db.Column(db.JSON,nullable=False)
    historical_churn=db.Column(db.Boolean,nullable=True)
    source=db.Column(db.String(100),nullable=False,default='analyst supplied')
    created_at=db.Column(db.DateTime(timezone=True),default=now,nullable=False)
    __table_args__=(db.UniqueConstraint('owner_id','external_id'),)
    def public(self): return dict(id=self.id,external_id=self.external_id,name=self.name,features=self.features,historical_churn=self.historical_churn,source=self.source)

class Account(db.Model):
    __tablename__='customer_accounts'
    id=db.Column(db.Integer,primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('bank_customers.id',ondelete='CASCADE'),unique=True,nullable=False)
    snapshot=db.Column(db.JSON,nullable=False)
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class Execution(db.Model):
    __tablename__='agent_executions'
    id=db.Column(db.String(36),primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('bank_customers.id',ondelete='CASCADE'),nullable=False,index=True)
    owner_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False,index=True)
    status=db.Column(db.String(20),nullable=False)
    report=db.Column(db.JSON)
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class Prediction(db.Model):
    __tablename__='churn_predictions'
    id=db.Column(db.Integer,primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('bank_customers.id',ondelete='CASCADE'),nullable=False,index=True)
    output=db.Column(db.JSON,nullable=False)
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class Explanation(db.Model):
    __tablename__='churn_explanations'
    id=db.Column(db.Integer,primary_key=True)
    prediction_id=db.Column(db.Integer,db.ForeignKey('churn_predictions.id',ondelete='CASCADE'),nullable=False)
    output=db.Column(db.JSON,nullable=False)

class Segment(db.Model):
    __tablename__='customer_segments'
    id=db.Column(db.Integer,primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('bank_customers.id',ondelete='CASCADE'),nullable=False,index=True)
    output=db.Column(db.JSON,nullable=False)

class Recommendation(db.Model):
    __tablename__='retention_recommendations'
    id=db.Column(db.Integer,primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('bank_customers.id',ondelete='CASCADE'),nullable=False,index=True)
    execution_id=db.Column(db.String(36),db.ForeignKey('agent_executions.id'),nullable=False)
    output=db.Column(db.JSON,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='pending')
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class AgentLog(db.Model):
    __tablename__='agent_execution_logs'
    id=db.Column(db.Integer,primary_key=True)
    execution_id=db.Column(db.String(36),db.ForeignKey('agent_executions.id'),nullable=False,index=True)
    output=db.Column(db.JSON,nullable=False)

class Feedback(db.Model):
    __tablename__='analyst_feedback'
    id=db.Column(db.Integer,primary_key=True)
    recommendation_id=db.Column(db.Integer,db.ForeignKey('retention_recommendations.id',ondelete='CASCADE'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    decision=db.Column(db.String(20),nullable=False)
    note=db.Column(db.String(2000),nullable=False,default='')
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class ModelMetric(db.Model):
    __tablename__='model_metrics'
    id=db.Column(db.Integer,primary_key=True)
    version=db.Column(db.String(64),unique=True,nullable=False)
    output=db.Column(db.JSON,nullable=False)
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class RevokedToken(db.Model):
    __tablename__='revoked_tokens'
    jti=db.Column(db.String(64),primary_key=True)
    created_at=db.Column(db.DateTime(timezone=True),default=now)
