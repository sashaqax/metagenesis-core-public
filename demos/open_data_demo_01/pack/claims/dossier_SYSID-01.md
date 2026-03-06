# Claim Dossier: SYSID-01

| Field | Value |
|-------|--------|
| **claim_id** | SYSID-01 |
| **job_kind** | `sysid1_arx_calibration` |
| **reproduction** | `python -m pytest tests/systems/test_sysid01_arx_calibration.py -v` |
| **evidence location** | job_snapshot.result |
| **V&V thresholds** | `rel_err_a <= 0.03`; `rel_err_b <= 0.03`; `rmse <= 0.05 * ( |
| **canary vs normal** | Same as MTR: job runs in normal or canary mode via `run_job(..., canary_mode=...)`; evidence artifacts produced for both; canary marked in artifact `canary_mode: true`. |
