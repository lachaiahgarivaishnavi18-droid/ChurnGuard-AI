"""Create a credential-free Vercel API source package from the canonical backend."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / 'deploy' / 'vercel-backend'
target.mkdir(parents=True, exist_ok=True)
for name in ['app', 'migrations']:
    shutil.copytree(ROOT / 'backend' / name, target / 'backend' / name, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '.env', '*.db'))
for name in ['trained_models', 'dataset']:
    shutil.copytree(ROOT / name, target / name, dirs_exist_ok=True)
for name in ['server.py', 'requirements.txt', 'pyproject.toml', 'vercel.json', '.vercelignore', 'migrate.py']:
    shutil.copy2(ROOT / 'deployment' / 'vercel-api' / name, target / name)
print('Prepared Vercel API package without local secrets or database files.')
