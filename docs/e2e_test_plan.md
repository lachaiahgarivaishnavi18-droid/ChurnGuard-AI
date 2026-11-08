# Browser end-to-end regression

Use a local instance with the supplied public academic dataset and a dedicated test analyst. No external banking actions are performed. Test through the React UI, not through direct database writes.

1. Open the landing page; choose Get started. Register a unique `example.test` email and a password of at least 12 characters. Expect an empty isolated workspace, not another analyst's portfolio.
2. Click Import academic dataset. Expect 300 customers and a 21.0% historical exited rate in the fixed 300-record sample. Current saved artifact produces 24 high-risk customers; retraining can alter this score count.
3. Open a high-risk customer from the overview table. Verify the external ID, account snapshot and probability. Run multi-agent analysis. Expect all six specialist names, completed timings, an exact model version and prediction timestamp.
4. Inspect signed SHAP factors. Baseline plus contributions should match the probability. No invented complaint, transaction decline or dissatisfaction should appear.
5. Change only membership, product count, balance or tenure in the what-if form. Run simulation. Expect original, simulated and signed difference; the snapshot above must remain unchanged. A sensitive demographic field must not be offered in this simulation form.
6. Open Retention strategies. Add a review note and choose Approve, Modify or Reject. Expect a saved review status and explicit notice that no customer action occurred. Modification without a note should fail clearly.
7. Search a displayed customer ID. Filter geography and risk; verify the table matches the visible selections. Clear filters and recover the full list.
8. Open Model performance. Verify all six algorithms, separate validation and held-out test results, ROC, precision-recall, confusion matrix, SHAP sample summary and group audits. Export the JSON and compare its version with the customer report.
9. Open the add-customer form. Invalid negative age/balance and missing required features must fail. Save valid data, edit a snapshot, predict again, and verify that the edited values are used. Delete only a dedicated disposable test record after the UI confirmation.
10. Sign out. Expect the landing page; a revoked token must fail API access. Register another analyst and verify that their workspace is empty.
11. Verify mobile and desktop layouts. On mobile, open/close the sidebar, keep form fields readable and allow wide tables to scroll. There must be no page-wide horizontal overflow.

Automated backend tests cover the persistence and isolation contracts behind these steps. The browser smoke result and any unverified steps are recorded in `verification.md`.
