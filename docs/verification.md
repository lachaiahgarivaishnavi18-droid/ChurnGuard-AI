# Verification record

Performed locally on 7 November 2026 with Python 3.12.14 and Node 24.22.1. The final package versions are recorded in `backend/requirements-lock.txt` and `frontend/pnpm-lock.yaml`.

- Downloaded the public CSV, verified 10,000 unique customer IDs, trained all six requested classifiers and generated actual validation and held-out test results. The selected calibrated decision tree achieved test ROC-AUC 0.8556, average precision (labelled PR-AUC) 0.6871, recall 0.7936 and precision 0.4621 at the validation-selected 0.150 threshold. Full results: `trained_models/metrics.json` and `docs/model_comparison.md`.
- Generated 40 real held-out Kernel SHAP explanations. Individual baseline-plus-contribution sums reconcile with the exact calibrated prediction. The summary is a small descriptive sample, not population-level proof.
- Final automated result: **8 passed in 15.45 seconds**. Automated integration checks cover dataset integrity, train-only imputation, probability/risk boundaries, exact-model SHAP, JWT authentication/revocation/invalid-token handling, cross-user CRUD and simulation denial, admin role protection, finite-value validation, all six graph outputs, execution persistence, recommendation feedback, deletion, demo import, analytics filters, simulation immutability and LLM timeout fallback. Run `python -m pytest tests -q` in backend to reproduce.
- Verified the single-command start-local.ps1 launcher: migration upgrade completed, built dashboard HTML returned HTTP 200, its JavaScript asset returned HTTP 200, and /api/health returned ok at port 5088. Temporary verification servers were stopped after testing.
- Built the React production bundle successfully with Vite. Browser testing used the development server at 127.0.0.1:5174 and Flask at 127.0.0.1:5088 because an unrelated local service occupied a default port.
- Browser smoke verified registration, sign-in, import of 300 records, 21.0% historical exited rate in the fixed sample, 24 predicted high-risk records, opening a high-risk customer, all six completed agent statuses with timings, SHAP factors and model version, and a simulation from 89.0% to 9.2% when product count changed from 3 to 2. This numerical change is solely a model simulation, not an intervention recommendation or causal estimate.
- Verified an approved proposal persisted in the review screen. No customer contact or account operation occurred. Inspected all six comparison rows, ROC/PR charts, confusion matrix, global SHAP summary and age/gender/geography audit on Model performance. Desktop and mobile views were inspected; the browser's scaled desktop viewport reported 1152 CSS pixels wide without horizontal page overflow (document width 1140).
- Found and corrected a stale-session blank-screen defect during the browser smoke. Invalid JWTs now return 401 and the client returns to sign-in; unavailable workspace data shows retry/recovery controls.
- Generated an Alembic initial migration from an empty database and successfully upgraded a fresh SQLite database. PostgreSQL DDL is also provided as `docs/database_schema.sql`.

Initial local verification used SQLite. Subsequent deployment and live PostgreSQL checks are recorded below. No LLM API key was provided: external LLM narration remains unverified, and the application explicitly labels its deterministic mode. Docker and Render remain unverified alternatives. Rate limiting currently uses process-local memory; production needs centralized storage. Browser smoke is manual, with its reproducible regression steps in `docs/e2e_test_plan.md`.

The application is an academic demonstrator. Group audits show material performance variation (for example, age-group recall) and do not certify fairness. Future time horizons, real retention uplift, eligibility/suitability decisions and operational bank performance remain unvalidated.

## Connected production deployment — 7 November 2026

- Frontend: https://churnguard-ai-omega.vercel.app — deployment `dpl_6va3yTAqJib62fskbDMsSZWRdyAf`, Ready.
- Flask API: https://churnguard-api.vercel.app — deployment `dpl_6WeFx4L77iQmsRKNe2TjQu8FJyHV`, Ready.
- Persistent database: dedicated Neon `churnguard-postgres`, free_v3 plan, iad1. Alembic applied the initial schema against PostgreSQL during deployment.
- Readiness returned status ready, database postgresql, and model version ee2a5c9d8daf-v1. The frontend routes /api/* to the deployed backend.
- All ten checks in `scripts/verify_online.py` passed through the public frontend URL, including registration, login, data import, predictions, six-agent SHAP analysis, simulations, review persistence, reports, isolation and persistent JWT revocation. Generated credentials were not logged or stored. See `online-verification.json` for the timestamp and exact checklist.
- The user explicitly approved storing the newly generated JWT signing secret as an encrypted Vercel production secret; its value is not present in source, documentation or frontend code.

The optional external LLM API remains unconfigured. Deterministic multi-agent evidence reporting is live and explicitly labelled. No real banking data, outreach or account action was used during verification.

Production browser smoke also registered a separate disposable analyst, imported the 300 public snapshot records, opened a high-risk customer and visibly completed all six agents, including the SHAP waterfall and retention plan. Proof is saved in docs/online-preview.jpg. The QA tab was closed; the user's existing tab and in-progress registration form were preserved.
