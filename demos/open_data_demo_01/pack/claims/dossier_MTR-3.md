# Claim Dossier: MTR-3

| Field | Value |
|-------|--------|
| **claim_id** | MTR-3 |
| **job_kind** | `mtr3_thermal_multilayer_contact_calibration` |
| **reproduction** | `python -m pytest tests/materials/test_mtr3_thermal_multilayer.py -v` |
| **evidence location** | job_snapshot.result |
| **V&V thresholds** | `rel_err_k <= 0.03`; `rel_err_r <= 0.05`; `rmse <= max(deltaT_true) * 0.05`. |
| **canary vs normal** | Same as MTR-1/MTR-2: job runs in normal or canary mode via `run_job(..., canary_mode=...)`; evidence artifacts produced for both; canary marked in artifact `canary_mode: true`. |
