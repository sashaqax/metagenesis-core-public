# Claim Dossier: MTR-1

| Field | Value |
|-------|--------|
| **claim_id** | MTR-1 |
| **job_kind** | `mtr1_youngs_modulus_calibration` |
| **reproduction** | `python -m pytest tests/materials/test_mtr1_youngs_modulus.py -v` |
| **evidence location** | job_snapshot.result |
| **V&V thresholds** | `relative_error <= 0.01`; `rmse <= (E_true * max_strain) * 0.02`. |
| **canary vs normal** | Same job kind runs in normal (authoritative) or canary (non-authoritative) mode via Progress Engine `run_job(..., canary_mode=...)`. Ledger action/actor differ (job_completed vs job_completed_canary; scheduler_v1 vs scheduler_v1_canary). Evidence artifacts are produced for both; canary runs are marked in artifact `canary_mode: true`. |
