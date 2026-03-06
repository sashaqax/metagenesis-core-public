# Claim Dossier: MTR-2

| Field | Value |
|-------|--------|
| **claim_id** | MTR-2 |
| **job_kind** | `mtr2_thermal_paste_conductivity_calibration` |
| **reproduction** | `python -m pytest tests/materials/test_mtr2_thermal_paste_conductivity.py -v` |
| **evidence location** | job_snapshot.result |
| **V&V thresholds** | `relative_error <= 0.02`; `rmse <= max(deltaT_true) * 0.03`. |
| **canary vs normal** | Same as MTR-1: job runs in normal or canary mode via `run_job(..., canary_mode=...)`; evidence artifacts produced for both; canary marked in artifact `canary_mode: true`. |
