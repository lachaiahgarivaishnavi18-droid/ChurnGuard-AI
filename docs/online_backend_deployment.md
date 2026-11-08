# Online backend deployment

The deployment package is prepared by `scripts/prepare_vercel_backend.py` from the canonical backend, migrations, public academic dataset and saved model artifacts. It excludes local databases, environment files, virtual environments and training-only dependencies. Its source templates are in `deployment/vercel-api/`.

Vercel project: `churnguard-api` in the same Vercel team as the frontend. Database: `churnguard-postgres`, a dedicated Neon PostgreSQL resource on the `free_v3` plan in `iad1`. The integration injects database credentials into the backend's production environment only; frontend code never receives them.

Deployment executes `migrate.py` before publication to apply the existing Alembic migration against PostgreSQL. Serverless operation requires a stable JWT signing secret; SQLite and ephemeral signing keys are rejected on Vercel. Database connections use pre-ping, bounded pooling, recycling and connection timeouts. `/api/health/ready` checks the database and saved model.

Both services are now live and connected. The user approved the new JWT secret transfer, the backend migrated PostgreSQL successfully, and the frontend was redeployed with its same-origin API proxy.

Frontend: https://churnguard-ai-omega.vercel.app

API readiness: https://churnguard-api.vercel.app/api/health/ready

Ten live checks passed via `scripts/verify_online.py`: readiness; registration/login; data import and analytics; trained-model predictions; all six LangGraph agents and SHAP reconciliation; simulation immutability; recommendation feedback; model comparison/report data; cross-user isolation; persistent logout revocation. Results: `docs/online-verification.json`.

The optional LLM narrator uses deterministic evidence reporting until an LLM API key is supplied. Rate limiting currently uses per-instance memory; configure centralized storage before high-volume production use. Signing secrets and database credentials stay in backend production environment variables. The frontend never receives them.
