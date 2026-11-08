"""Configure fresh Vercel backend secrets over stdin; never print secret values."""
from pathlib import Path
import secrets
import subprocess
import os

ROOT=Path(__file__).resolve().parents[1]
runtime=Path(os.environ['USERPROFILE'])/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
cli=[str(runtime/'bin/node.exe'),str(runtime/'node_modules/pnpm/bin/pnpm.mjs'),'dlx','vercel']
values={
    'JWT_SECRET_KEY':secrets.token_hex(48),
    'FRONTEND_ORIGIN':'https://churnguard-ai-omega.vercel.app,https://churnguard-ai-resume-project3.vercel.app',
    'OMP_NUM_THREADS':'1',
    'OPENBLAS_NUM_THREADS':'1',
    'MKL_NUM_THREADS':'1',
}
for key,value in values.items():
    command=cli+['env','add',key,'--environment','production','--yes']
    if key=='JWT_SECRET_KEY': command+=['--sensitive']
    result=subprocess.run(command,input=value,text=True,cwd=ROOT/'deploy/vercel-backend',capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Failed to configure {key}: '+result.stderr)
    print('Configured '+key+' (value not displayed).',flush=True)
