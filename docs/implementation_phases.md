# Implementation phases and reproducibility

Run commands from the project root unless a working directory is named. Python dependencies are in `backend/requirements.txt`; frontend dependencies are in `frontend/package.json`. This guide names the actual implementation files rather than reproducing them into a second divergent document.

| Phase | Purpose and implementation | Run / expected output / verification |
|---|---|---|
| 1 Architecture | `docs/architecture.md`: frontend/API/ML/database boundaries and agent graph | Inspect Mermaid architecture and sequence diagrams; six specialists join before reporting |
| 2 Dataset & EDA | `scripts/download_dataset.py`, `dataset/README.md`, `notebooks/exploratory_data_analysis.ipynb` | `python scripts/download_dataset.py`; training writes `dataset/processed/eda.json`; expected 10,000 rows, 20.37% historical exited rate |
| 3 Preprocessing | `backend/app/ml/preprocessing.py`: missing-value imputation, deduplication, train-only one-hot encoding and scaling | `pytest backend/tests/test_platform.py` from backend with the configured Python path; invalid columns/labels rejected; IDs and outcome excluded |
| 4 Model training | `backend/app/ml/train_model.py`, `evaluate_model.py`: six learners, grid CV, calibration, validation F2, held-out test | From backend: `python -m app.ml.train_model`; expect per-model PR-AUC, selected model and saved artifacts. No accuracy-only selection; no SMOTE |
| 5 Explainability | `backend/app/ml/explainability.py`: Kernel SHAP calls exact calibrated predict_proba | Run SHAP test; baseline + signed contributions must reconstruct individual probability |
| 6 Specialized agents | Six modules in `backend/app/agents/` | Workflow test verifies all six named outputs and evidence-based strategies |
| 7 LangGraph | `backend/app/agents/supervisor.py`: typed state, parallel branches, fan-in, retries and conditional routing | `POST /api/agents/analyze/{id}` returns six completed timings and report; mismatched explanations fail |
| 8 Retention engine | `retention_strategy_agent.py`: voluntary support based on available account flags | Analyze inactive single-product customer; expect assistance and optional review; estimated impact null |
| 9 Database | `backend/app/models/__init__.py`, `backend/migrations/`, `compose.yaml` | `flask --app run db upgrade`; fresh schema created. PostgreSQL smoke test requires POSTGRES_TEST_URL |
| 10 REST API | `backend/app/routes/api.py`, app factory and `run.py` | `python run.py`; GET /api/health → ok. Integration tests exercise auth/isolation/persistence |
| 11 React UI | `frontend/src/App.jsx`, `components/Charts.jsx`, services and styles | `npm run dev`; register, import data, inspect portfolio. `npm run build` produces dist |
| 12 Integration | Customer profiles call saved model and real LangGraph endpoint | Select customer → analysis → SHAP → simulation → proposal review → JSON export |
| 13 Testing | `backend/tests/`, frontend production build, browser smoke workflow | `python -m pytest tests -q` from backend. See verification record for actual checks and limits |
| 14 Deployment | `render.yaml`, `frontend/vercel.json`, Dockerfile | Requires user-controlled Vercel/Render accounts; see README. Deployment has not occurred |
| 15 Documentation | README, API contract, architecture, ERD, phases, model report and notebooks | Follow fresh setup or Docker instructions; compare current metrics with generated model report |

Do not present expected outputs as observed outcomes unless they are recorded in `docs/verification.md`. Artifacts are calibrated academic models, not bank-validated operational risk systems.
