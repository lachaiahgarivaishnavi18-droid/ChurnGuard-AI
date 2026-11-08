# Database design

```mermaid
erDiagram
    users ||--o{ bank_customers : owns
    users ||--o{ agent_executions : requests
    users ||--o{ analyst_feedback : authors
    bank_customers ||--|| customer_accounts : has
    bank_customers ||--o{ churn_predictions : receives
    bank_customers ||--o{ customer_segments : assigned
    bank_customers ||--o{ agent_executions : analyzed
    churn_predictions ||--o{ churn_explanations : explained
    agent_executions ||--o{ agent_execution_logs : logs
    agent_executions ||--o{ retention_recommendations : proposes
    bank_customers ||--o{ retention_recommendations : receives
    retention_recommendations ||--o{ analyst_feedback : reviewed
    users { int id PK string email UK string password_hash string role datetime created_at }
    bank_customers { int id PK int owner_id FK string external_id string name json features boolean historical_churn string source }
    customer_accounts { int id PK int customer_id FK json snapshot datetime created_at }
    churn_predictions { int id PK int customer_id FK json output datetime created_at }
    churn_explanations { int id PK int prediction_id FK json output }
    customer_segments { int id PK int customer_id FK json output }
    agent_executions { string id PK int owner_id FK int customer_id FK string status json report datetime created_at }
    retention_recommendations { int id PK int customer_id FK string execution_id FK json output string status }
    analyst_feedback { int id PK int user_id FK int recommendation_id FK string decision string note datetime created_at }
    agent_execution_logs { int id PK string execution_id FK json output }
    model_metrics { int id PK string version UK json output datetime created_at }
    revoked_tokens { string jti PK datetime created_at }
```

The canonical schema is `backend/app/models/__init__.py`; the initial migration is under `backend/migrations/versions`. Customer identity is unique per owner (`owner_id`, `external_id`). Users have unique emails; accounts are unique per customer; execution and prediction foreign keys preserve traceability. Owner and customer join columns are indexed. Structured feature validation is enforced at the API boundary using Pydantic; numerical feature ranges are stored in JSON rather than individual database check constraints.

Customer account snapshots do not imply separate actual account numbers. Sensitive source surnames are not imported into the application. `historical_churn` is nullable to distinguish unknown outcomes from retained customers. Source provenance is stored on each customer. Transaction and interaction tables are intentionally absent because their underlying data is unavailable.

An analyst cannot assign their own role through registration. The admin audit endpoint checks the database role. Ownership still applies to administrators; there is no implicit cross-user access. Controlled administrative role provisioning is performed by a trusted database operator, outside the public registration API.
