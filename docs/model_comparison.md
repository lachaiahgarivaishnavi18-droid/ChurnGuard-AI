# Actual model comparison

Validation F2 then PR-AUC; sigmoid calibration via train-only CV

Validation results (not test performance):

| Model | CV PR-AUC | Validation PR-AUC | Recall | Precision | F1 | F2 |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.4670 | 0.4632 | 0.7322 | 0.3465 | 0.4704 | 0.5989 |
| Decision Tree | 0.5809 | 0.6413 | 0.8428 | 0.4261 | 0.5660 | 0.7049 |
| Random Forest | 0.6837 | 0.6825 | 0.7494 | 0.5075 | 0.6052 | 0.6842 |
| XGBoost | 0.6924 | 0.6869 | 0.7445 | 0.4927 | 0.5930 | 0.6754 |
| Gradient Boosting | 0.6989 | 0.6854 | 0.8206 | 0.4282 | 0.5628 | 0.6935 |
| Support Vector Machine | 0.6575 | 0.6226 | 0.6904 | 0.4836 | 0.5688 | 0.6360 |

Selected: **Decision Tree**, binary operating threshold **0.150**, version `ee2a5c9d8daf-v1`.

Held-out test results after final train+validation refit:

- accuracy: 0.7700
- precision: 0.4621
- recall: 0.7936
- f1: 0.5841
- roc_auc: 0.8556
- pr_auc: 0.6871
- brier: 0.1050

Confusion matrix (rows actual retained/churn, columns predicted retained/churn): `[[1217, 376], [84, 323]]`.

The recall-focused F2 rule can select a model with lower PR-AUC than another candidate. The threshold is a selected business proxy, not a measured intervention-cost optimum. Risk bands are separate configurable analyst triage labels. Held-out performance is academic evidence, not a prospective banking validation. See metrics.json for all curves and group results.
