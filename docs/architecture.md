# Architecture

React calls authenticated Flask endpoints. JWT identity scopes every customer, execution, prediction and recommendation query to the owning analyst. SQLAlchemy persists the workflow outputs in PostgreSQL; SQLite is an explicit local development option. The ML artifact contains the exact preprocessing pipeline, calibrated estimator, training SHAP background and fitted account segmenter. No LLM estimates churn probabilities.

```mermaid
flowchart LR
    UI[React analyst workspace] --> API[Flask REST API and JWT authorization]
    API --> DB[(PostgreSQL)]
    API --> G[LangGraph supervisor]
    G --> A[Customer analysis agent]
    G --> P[Churn prediction agent]
    G --> S[Account segmentation agent]
    P --> M[Calibrated trained ML pipeline]
    P --> E[SHAP explanation agent]
    E --> M
    A --> R[Retention strategy agent]
    E --> R
    S --> R
    R --> F[Final reporting and consistency agent]
    F -. optional grounded draft .-> L[LLM API]
    F --> API
```

```mermaid
sequenceDiagram
    actor Analyst
    participant API as Flask supervisor endpoint
    participant Graph as LangGraph
    participant Model as Saved ML pipeline
    participant DB as Database
    Analyst->>API: Analyze owned customer
    API->>DB: Persist running execution
    API->>Graph: Validated customer state
    par independent branches
      Graph->>Graph: Analyze account snapshot
    and
      Graph->>Model: Calibrated churn probability
      Model-->>Graph: Probability, version, threshold
      Graph->>Model: SHAP over exact predict_proba
    and
      Graph->>Graph: Assign fitted K-Means cluster
    end
    Graph->>Graph: Join evidence and generate strategies
    Graph->>Graph: Validate SHAP reconstruction and version
    Graph-->>API: Structured final report and timings
    API->>DB: Persist prediction, explanation, segment, proposals and logs
    API-->>Analyst: Report and execution ID
    Analyst->>API: Approve, reject or modify proposal
    API->>DB: Record feedback only
```

State is a TypedDict with separate outputs for each specialist and an append reducer for concurrent log writes. Node outputs merge into state, and a multi-source edge waits for independent branches before retention. Conditional routing permits reporting only when strategies exist; the supervisor rejects incomplete results. Transient timeout/connection failures receive at most two attempts. ML failures do not generate fake fallback probabilities. Failed execution status is stored and the client receives a generic error with an execution ID.

The chosen design uses deterministic evidence tools for the first five agents and an optional LLM draft in reporting. They are specialized workflow agents, not six autonomous LLM conversations. LangGraph is the actual orchestrator. Grounded structured fields remain authoritative when an LLM draft is present.
