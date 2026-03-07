# Use Cases

MetaGenesis Core applies to any domain where a computational result
must be verified independently, without access to the original environment.

---

## 1. ML benchmark and AI accuracy claims

**The problem:** Every ML team claims state-of-the-art results. Reviewers
cannot check without re-running training — which requires the original
compute, data, and environment. Published accuracy numbers are routinely
inflated, cherry-picked, or evaluated on leaked test sets.

**What MetaGenesis Core does:** Package the model's predictions
(y_true / y_pred CSV) into a tamper-evident bundle. SHA-256 fingerprint
the dataset. Any reviewer runs one command and gets PASS or FAIL.

```bash
# Claim: model achieves 94.3% accuracy on this test set
result = run_certificate(
    dataset_relpath="predictions/model_v3_test.csv",
    claimed_accuracy=0.943
)
# Bundle includes: dataset fingerprint, predictions, metrics, provenance
# Verifier runs: mg.py verify --pack bundle.zip → PASS or FAIL
```

**Who needs this:** ML research teams, AI product companies, benchmark
organizers, regulators reviewing AI system submissions (EU AI Act,
FDA AI/ML guidance for Software as a Medical Device).

---

## 2. Pharmaceutical and clinical computational submissions

**The problem:** Drug discovery and clinical trials increasingly rely on
computational models — ADMET predictions, pharmacokinetic simulations,
biomarker analysis. Regulators (FDA 21 CFR Part 11, EMA) require
audit trails but existing infrastructure is expensive and proprietary.

**What MetaGenesis Core does:** Package any computational model output
into a verifiable bundle. The bundle contains the full provenance chain —
inputs, algorithm version, result — in a form any regulator can verify
offline. No proprietary tools required.

**Target claim types:**
- IC50 / binding affinity predictions
- PK/PD simulation outputs
- Clinical trial outcome model validation
- Safety signal detection algorithm outputs

**Who needs this:** Biotech and pharma computational chemistry teams,
CROs submitting computational evidence to regulators, clinical trial
data management organizations.

---

## 3. Carbon credit and ESG model verification

**The problem:** Carbon credits are issued based on computational models
— satellite imagery analysis, deforestation algorithms, carbon
sequestration estimates. These models are opaque. Auditors cannot verify
the outputs without the original proprietary software.

The market for voluntary carbon credits is in crisis precisely because
there is no credible independent verification standard for the underlying
computations.

**What MetaGenesis Core does:** Any carbon model output becomes a
verifiable bundle. Third-party auditors — corporate ESG teams, rating
agencies, regulators — verify offline without access to the proprietary
model. The bundle is tamper-evident.

**Target claim types:**
- Deforestation rate estimates (hectares / year)
- Carbon sequestration model outputs (tonnes CO₂e)
- Satellite-derived land-use change metrics

**Who needs this:** Carbon project developers, voluntary carbon market
registries (Verra, Gold Standard), ESG rating agencies, corporate buyers
requiring credible offset documentation.

---

## 4. Financial risk model validation

**The problem:** Banks and asset managers run risk models (VaR, credit
scoring, stress testing) that regulators must validate. Basel III/IV
requires model risk management. Current validation is expensive,
proprietary, and manual.

**What MetaGenesis Core does:** Financial model outputs are packaged
into verifiable bundles. Regulators and internal model risk teams
verify specific claim outputs — VaR estimates, loss given default,
scenario analysis results — without re-running the full model.

**Target claim types:**
- Value at Risk (VaR) computation outputs
- Credit model PD/LGD/EAD estimates
- Stress test scenario results
- Algorithmic trading strategy backtests

**Who needs this:** Bank model risk management teams, regulatory
technology (regtech) vendors, internal audit functions, central bank
supervisory teams.

---

## 5. Materials science and engineering calibration

**The original domain.** Simulation-based design — finite element
analysis, molecular dynamics, thermal simulation — produces calibrated
material property claims that other teams depend on.

**What MetaGenesis Core does:** Calibration results (Young's modulus,
thermal conductivity, contact resistance) are packaged into verifiable
bundles. Engineering teams hand off simulation results to clients and
regulators with independent verification proof.

Active claims: MTR-1 (Young's modulus), MTR-2 (thermal paste conductivity),
MTR-3 (multilayer thermal contact), DRIFT-01 (drift monitoring).

```
MTR-1 verified:  E = 70 GPa  →  trusted anchor
Client receives: mg.py verify --pack mtr1_bundle.zip → PASS
```

**Who needs this:** Materials science labs, aerospace and automotive
simulation teams, component qualification for safety-critical applications.

---

## Common pattern across all domains

The verification workflow is identical regardless of domain:

```
1. Computation runs → produces result
2. result + provenance → evidence bundle (mg.py pack build)
3. Bundle sent to third party
4. Third party: mg.py verify --pack bundle.zip → PASS or FAIL
```

No GPU. No environment access. No trust.

The only thing that changes per domain is the claim type and V&V thresholds.
