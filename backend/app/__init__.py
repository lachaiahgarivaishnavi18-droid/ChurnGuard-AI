import os, secrets
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from dotenv import load_dotenv
from .models import db, RevokedToken
limiter=Limiter(key_func=get_remote_address,default_limits=['300 per minute'],storage_uri=os.getenv('RATELIMIT_STORAGE_URI','memory://'))

def create_app(test_config=None):
    if not os.getenv('VERCEL'): load_dotenv()
    app=Flask(__name__,static_folder='../../frontend/dist',static_url_path='/',instance_path='/tmp/churnguard' if os.getenv('VERCEL') else None)
    database=os.getenv('DATABASE_URL','sqlite:///churnguard.db')
    if database.startswith('postgres://'): database=database.replace('postgres://','postgresql+psycopg://',1)
    if database.startswith('postgresql://'): database=database.replace('postgresql://','postgresql+psycopg://',1)
    secret=os.getenv('JWT_SECRET_KEY')
    if os.getenv('VERCEL') and not database.startswith('postgresql'):
        raise RuntimeError('Hosted deployment requires PostgreSQL')
    if database.startswith('postgresql') and (not secret or len(secret)<32): raise RuntimeError('Set JWT_SECRET_KEY to at least 32 random characters')
    app.config.update(SQLALCHEMY_DATABASE_URI=database,JWT_SECRET_KEY=secret or secrets.token_hex(32),JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=2),MAX_CONTENT_LENGTH=1024*1024)
    if test_config: app.config.update(test_config)
    if database.startswith('postgresql'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS']={'pool_pre_ping':True,'pool_recycle':180,'pool_size':2,'max_overflow':2,'connect_args':{'connect_timeout':15}}
    db.init_app(app); Migrate(app,db)
    CORS(app,resources={r'/api/*':{'origins':os.getenv('FRONTEND_ORIGIN','http://localhost:5173').split(',')}})
    jwt=JWTManager(app)
    @jwt.invalid_token_loader
    def invalid_token(reason): return jsonify(error='Session is invalid. Please sign in again.'),401
    @jwt.token_in_blocklist_loader
    def revoked(header,payload): return db.session.get(RevokedToken,payload['jti']) is not None
    limiter.init_app(app)
    from .routes.api import api
    app.register_blueprint(api)
    @app.errorhandler(404)
    def missing(error): return jsonify(error='Not found'),404
    @app.errorhandler(500)
    def internal(error):
        db.session.rollback(); app.logger.exception('Request failed')
        return jsonify(error='Internal error; consult server logs'),500
    @app.route('/')
    def index(): return app.send_static_file('index.html')
    return app
