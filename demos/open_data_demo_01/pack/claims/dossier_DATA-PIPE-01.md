# Claim Dossier: DATA-PIPE-01

| Field | Value |
|-------|--------|
| **claim_id** | DATA-PIPE-01 |
| **job_kind** | `datapipe1_quality_certificate` |
| **reproduction** | `python -m pytest tests/data/test_datapipe01_quality_certificate.py -v` |
| **evidence location** | job_snapshot.result |
| **V&V thresholds** | pass is True when schema/range checks pass; no absolute paths in output. |
| **canary vs normal** | Same as MTR: job runs in normal or canary mode; evidence artifacts for both. |
