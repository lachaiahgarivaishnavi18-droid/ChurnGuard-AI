# API contract

Base path `/api`. JSON request and response bodies; authenticated endpoints require `Authorization: Bearer <access_token>`. Tokens expire after two hours. Registration returns 201; unauthenticated requests return 401, forbidden admin operations 403, inaccessible customer records 404, validation failures 422, conflicts 409 and failed analysis 503. IDs in customer URLs are internal database IDs, not the dataset CustomerId.

| Method | Path | Request / response |
|---|---|---|
| GET | /health | Public process health |
| POST | /auth/register | `{email,password}` → access_token and analyst role; 12–128 character password |
| POST | /auth/login | `{email,password}` → access_token and role |
| POST | /auth/logout | Revoke current token |
| GET | /customers | `{items,total}`; page/page_size (maximum 500) |
| GET | /customers/{id} | Customer, live probability, risk and segment |
| POST | /customers | `{name,external_id,features}` → new customer |
| PUT | /customers/{id} | `{name?,features}` → updated snapshot |
| DELETE | /customers/{id} | Delete owned record and related analysis; 204 |
| POST | /customers/import-demo | Import 300 public pseudonymous records into empty owned workspace |
| POST | /predict | `{customer_id}` persists owned prediction; `{features}` computes without persistence |
| GET | /predictions | Most recent 100 owned predictions |
| GET | /predictions/{customer_id} | Owned customer prediction history |
| POST | /agents/analyze/{customer_id} | Run graph synchronously → execution_id, status, report |
| GET | /agents/status/{execution_id} | Persisted running/completed/failed status and report |
| GET | /agents/report/{execution_id} | Persisted report |
| GET | /recommendations | Most recent 200 owned proposals |
| GET | /recommendations/{customer_id} | Proposals for owned customer |
| POST | /recommendations/{id}/feedback | `{decision,note}`; approved/rejected/modified; modified requires note |
| POST | /simulate/{customer_id} | Subset of IsActiveMember, NumOfProducts, Balance, Tenure → original, simulated, difference |
| GET | /analytics/summary | Historical outcomes, predicted categories, active members and groups |
| GET | /analytics/churn | Same filtered analytics contract |
| GET | /analytics/segments | Same filtered analytics contract including segments |
| GET | /model/metrics | Actual stored training comparison, test, group audit and curves |
| GET | /model/feature-importance | Metrics contract including descriptive permutation importance |
| GET | /model/status | Metrics contract if trained; 503 otherwise |
| GET | /admin/audit | Admin role required; owned execution statuses |

Customer and analytics filters: `q`, `risk=High|Medium|Low`, `geography`, `segment`, `products`, `age_min/max`, `tenure_min/max`, `balance_min/max`, `probability_min/max`. The frontend exposes search, risk and geography controls plus a More filters panel for age, tenure, balance, churn probability, segment and product count.

Example feature object:

```json
{"CreditScore":650,"Geography":"France","Gender":"Female","Age":40,"Tenure":5,"Balance":80000,"NumOfProducts":1,"HasCrCard":1,"IsActiveMember":0,"EstimatedSalary":75000}
```

Fields are required, unknown fields rejected, numerical values finite, credit score 300–900, age 18–110, tenure 0–60, products 1–4, nonnegative balances/salary, binary membership/card flags. Geography and gender follow dataset categories; generalization outside those categories is unvalidated.

Prediction output: probability, churn boolean at validation-selected threshold, configurable risk category, model version, threshold and confidence note. The binary decision threshold differs from risk-band boundaries. A medium-risk customer can exceed the binary churn threshold; this is deliberate and documented.

Recommendation feedback creates an immutable feedback row and updates proposal status; a modified strategy is recorded in the analyst's note while retaining the original agent output for audit. No communication or banking account execution endpoint exists.
