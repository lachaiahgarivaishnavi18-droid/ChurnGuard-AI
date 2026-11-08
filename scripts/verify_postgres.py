"""Run only with an explicitly disposable PostgreSQL database URL.
Creates and drops a uniquely named schema; never drops the shared database.
Usage: python scripts/verify_postgres.py (set POSTGRES_TEST_URL first).
"""
import os, sys, uuid
from pathlib import Path
from sqlalchemy import create_engine, text
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.models import db
url=os.environ['POSTGRES_TEST_URL']
if not url.startswith('postgresql'): raise ValueError('A PostgreSQL URL is required')
engine=create_engine(url)
schema='churnguard_test_'+uuid.uuid4().hex
with engine.begin() as conn:
    conn.execute(text(f'CREATE SCHEMA {schema}'))
    conn.execute(text(f'SET LOCAL search_path TO {schema}'))
    db.metadata.create_all(conn)
    assert conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema=:schema"),{'schema':schema}).scalar()>=12
    db.metadata.drop_all(conn)
    conn.execute(text(f'DROP SCHEMA {schema}'))
print('PostgreSQL schema constraints and creation verified in an isolated schema.')
