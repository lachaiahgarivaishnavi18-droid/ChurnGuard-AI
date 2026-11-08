from pathlib import Path
from flask_migrate import upgrade
from server import app

with app.app_context():
    if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
        raise RuntimeError('Vercel deployment requires a hosted PostgreSQL database')
    upgrade(directory=str(Path(__file__).resolve().parent / 'backend' / 'migrations'))
print('PostgreSQL schema migrations completed.')
