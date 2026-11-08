# Dataset provenance

Source: [https://github.com/zunicd/Bank-Churn-Prediction/blob/master/Resources/Churn_Modelling.csv](https://github.com/zunicd/Bank-Churn-Prediction/blob/master/Resources/Churn_Modelling.csv). Downloaded 7 November 2026 for academic demonstration. This is the widely circulated Churn_Modelling educational dataset; the mirror does not authenticate real banking provenance or establish redistribution rights. Review upstream licensing before publication or non-academic use.

SHA-256: `ee2a5c9d8daf3aed0d91c4d883a84ebb77d271447bebc0f0c80aafb0f288ceab`

10,000 unique CustomerId records; 2,037 historical Exited outcomes. Fields: RowNumber, CustomerId, Surname, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited. IDs, surnames, row numbers and outcomes are excluded from model features. The UI uses pseudonymous display names. No synthetic transaction or service data is appended.

Limitations: no outcome date, prospective horizon, transaction history, complaints, service events, marketing eligibility, beginning-of-period cohort, intervention assignment, intervention cost, or retention outcomes. EstimatedSalary and Balance are snapshot values with unverified currency; the UI uses EUR as an illustrative presentation convention for France/Germany/Spain and does not assert source currency metadata.

`processed/eda.json` records missing counts, numerical summaries, geography counts and historical outcome rates. Splits are stratified 60/20/20 for fitting/validation/testing. After selection, the final estimator refits on 80%; the test 20% remains untouched by selection.
