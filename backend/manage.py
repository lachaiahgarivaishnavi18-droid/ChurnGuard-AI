"""Development initialization; use Flask-Migrate for deployed upgrades."""
from app import create_app
from app.models import db, ModelMetric
from pathlib import Path
import json
app=create_app()
with app.app_context():
    db.create_all()
    path=Path('../trained_models/metrics.json')
    if path.exists():
        metrics=json.loads(path.read_text())
        if not ModelMetric.query.filter_by(version=metrics['version']).first():
            db.session.add(ModelMetric(version=metrics['version'],output=metrics)); db.session.commit()
    print('Database initialized. Register an account in the application.')
