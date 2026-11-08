# ChurnGuard AI

A banking churn research platform with a React analyst workspace, Flask API, calibrated machine learning, exact-pipeline SHAP explanations, and a six-agent LangGraph workflow. Source files are in this project root; there is no extra `banking-churn-multi-agent` wrapper directory.

## What is implemented

- Six-model training comparison, train-only preprocessing, three-fold cross-validation, validation F2 threshold selection, sigmoid calibration, a held-out test evaluation, and serialized joblib model.
- Six specialized agents with parallel graph branches, structured state, synchronized recommendations, retries for transient failures, execution timing, persisted reports, and explanation reconciliation.
- Customer CRUD, isolated analyst accounts, hashed passwords, expiring and revocable JWTs, rate limits, input validation, admin-gated audit access, and PostgreSQL-compatible SQLAlchemy models and Alembic migration.
- Live model-scored portfolio, search and risk/geography filters, customer details, SHAP contribution plot, what-if simulations, segments, historical analytics, model comparison, group audits, recommendation review and JSON exports.
- Optional LLM-generated report draft. Without an API key, the full graph runs with deterministic evidence-based reporting; it does not pretend an LLM was called.

## Run locally (Python 3.12 and Node 20+)

From this directory, create a virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt -c backend/requirements-lock.txt
cd frontend
npm install
cd ..
```

The public CSV and trained artifact are included. To reproduce them:

```powershell
.\.venv\Scripts\python.exe scripts/download_dataset.py
cd backend
..\.venv\Scripts\python.exe -m app.ml.train_model
```

Training writes `trained_models/churn_model.pkl`, `trained_models/metrics.json`, `trained_models/shap_summary.json` and `dataset/processed/eda.json`. The saved object includes the calibrated pipeline, background data, operating threshold, version and fitted segmenter. Keeping preprocessing with the model prevents a mismatched preprocessing artifact. Do not load untrusted pickle/joblib files.

For a quick local demonstration, no `.env` is needed: the API uses SQLite and an ephemeral JWT key (restarting invalidates sessions). Initialize and run:

```powershell
cd backend
..\.venv\Scripts\python.exe -m flask --app run db upgrade
..\.venv\Scripts\python.exe run.py
```

In another terminal:

```powershell
cd frontend
npm run dev
```

Open [the local dashboard](http://localhost:5173), or the alternate port printed by Vite if 5173 is busy. The API defaults to port 5088. Register an account with a password of at least 12 characters, then click **Import academic dataset**. Choose a customer, run multi-agent analysis, inspect SHAP, run a simulation, then review the generated recommendation under Retention strategies. No customer is contacted and no banking account is changed.

If using this workspace's bundled runtime, `.venv` is already installed. The Node runtime has pnpm rather than npm; invoke the bundled Node executable with `frontend/node_modules/vite/bin/vite.js` if pnpm's environment repair wrapper intervenes. `frontend/pnpm-lock.yaml` records installed dependencies.

## PostgreSQL

Copy `backend/.env.example` to `backend/.env`, configure a PostgreSQL database and a long random JWT secret, then run migrations. Production must use a stable secret. Use `sslmode=require` in the hosted database URL when required by the provider. `manage.py` is a convenience initializer for fresh development databases; deployed upgrades use Alembic.

Alternatively, set `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` in your shell and run `docker compose up --build`. This starts PostgreSQL 16 and the API; run the frontend separately. Local integration tests use SQLite. The deployed application has now also passed online checks against its dedicated Neon PostgreSQL database. Run `scripts/verify_postgres.py` with `POSTGRES_TEST_URL` against a disposable PostgreSQL instance for an isolated-schema smoke test.

## Test and build

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
cd ../frontend
npm run build
```

Tests exercise real saved-model inference, dataset loading, SHAP additivity, risk boundaries, graph execution, persistent reports, feedback, simulation immutability, input rejection, JWT revocation, admin authorization and cross-user isolation. Model training is an explicit reproducible integration job rather than a test that retrains every time.

## Deployment

The live frontend is [ChurnGuard AI](https://churnguard-ai-omega.vercel.app), the Flask API is [churnguard-api.vercel.app](https://churnguard-api.vercel.app/api/health/ready), and the persistent PostgreSQL database is the dedicated Neon `churnguard-postgres` resource on its free plan. Both Vercel deployments are Ready. The frontend proxies `/api/*` to the backend, so no database credentials or signing secrets reach frontend code.

The backend has a stable encrypted JWT signing secret, configured frontend origins, bounded PostgreSQL connection pooling, and a Python 3.12 runtime. Database migrations run during the backend build. `scripts/prepare_vercel_backend.py` creates the source package from `deployment/vercel-api/` and the canonical application; deploy the generated `deploy/vercel-backend` directory with Vercel CLI, then deploy `frontend`. Keep the project links in the ignored `.vercel` directories. Do not rerun the one-time signing-secret configuration script unless intentionally rotating the key; rotation invalidates existing sessions.

`python scripts/verify_online.py` runs ten live checks with generated disposable QA accounts and public academic records. Results are in `docs/online-verification.json`. Registration/login, PostgreSQL persistence, prediction, all six LangGraph agents, SHAP reconciliation, simulations, recommendations, feedback, model reports, account isolation and JWT logout passed through the frontend URL. Register your own account and choose Import academic dataset to begin.

`render.yaml` and Docker configuration remain alternative deployment options. Optional LLM narration requires an LLM API key configured only on the backend; the online workflow currently uses its explicitly labelled deterministic evidence-report mode.

## Evidence and limitations

The [public CSV mirror](https://github.com/zunicd/Bank-Churn-Prediction/blob/master/Resources/Churn_Modelling.csv) contains 10,000 records with 2,037 exited outcomes. See `dataset/README.md` for source and checksum. It is an educational snapshot, not authenticated current banking data. Confirm upstream licensing before redistribution or non-academic use.

Transaction history, complaints, service interactions, time-to-churn and intervention outcomes are absent. No transaction or interaction tables are populated or invented. Retention impact remains null. Historical exited rates are separate from model predictions; a cohort retention rate is unavailable. Simulations describe model behavior, not causal effects. Demo customers can overlap training records; test metrics come exclusively from a reserved test partition. Model probabilities have no verified future time horizon.

Age, gender and geography are available model features and fairness-audit dimensions. They do not establish customer value, dissatisfaction or eligibility. Group disparities require investigation, including feature ablations and prospective validation, before real banking use. Recommendation rules use account engagement evidence and propose voluntary support, with human review.

The current API runs graph requests synchronously; the execution record is persisted before the graph begins, so a second request can inspect status. A durable worker queue and checkpoints, centralized rate-limit storage, secrets management and an operational audit-retention policy are needed for a production service. Tokens are stored in sessionStorage for this academic client; hardened deployments should consider a secure HttpOnly-cookie design and CSP.

## Project documentation

- [Architecture and workflow](docs/architecture.md)
- [API contract](docs/api_documentation.md)
- [Database design](docs/database_design.md)
- [Phase-by-phase implementation guide](docs/implementation_phases.md)
- [Actual model comparison](docs/model_comparison.md)
- [Verification record](docs/verification.md)

## Start the built local application

After the frontend build, run ./start-local.ps1 from the project root. It applies migrations and serves the built React app and API together at http://127.0.0.1:5088. This workspace already contains the installed virtual environment and built frontend; no cloud account is required. Local databases, the demo analyst and generated secret are ignored by Git. Create your own analyst account when sharing a clean checkout.
