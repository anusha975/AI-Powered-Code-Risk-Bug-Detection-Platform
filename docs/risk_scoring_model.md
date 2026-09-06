# Code Risk Scoring Engine & ML Pipeline Specification

**Module:** Module 5: Code Risk Scoring Engine  
**Status:** Active  
**Privacy Guarantees:** 100% Offline, In-Memory Execution, Zero Data Ingress to External AI Providers  

---

## 1. Architecture Overview

The **Code Risk Scoring Engine** computes an overall security and quality risk score ($0 - 100$) for submitted source code by synthesizing deterministic static analysis heuristics with a Scikit-learn Machine Learning regression pipeline.

```
+--------------------------------------------------------------------------------+
|                             SOURCE CODE SUBMISSION                             |
+--------------------------------------------------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
    +-----------------------------+         +-----------------------------+
    | Local Static Code Analysis  |         | Secret Detection & Privacy  |
    | (Python AST & Bandit SAST)  |         | (Entropy & Regex Scanners)  |
    +-----------------------------+         +-----------------------------+
                   |                                       |
                   |  Standardized Findings                |  Redacted Secrets Count
                   +-------------------+-------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |     Stage 1: Feature Extraction     |
                    | (16-Dimensional Normalized Vector)  |
                    +-------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
    +-----------------------------+         +-----------------------------+
    | Stage 2: Deterministic Rule |         | Stage 3: Scikit-learn ML    |
    | Baseline Scoring Engine     |         | Preprocessor & RF Regressor |
    +-----------------------------+         +-----------------------------+
                   |                                       |
                   | Baseline Score + Reasons              | Predicted ML Score
                   +-------------------+-------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |   Stage 4: Score Blending & Floor   |
                    |     Enforcement (Bounds: 0-100)     |
                    +-------------------------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |   Stage 5: Explainability Engine    |
                    |  & Severity Level Classification    |
                    +-------------------------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |     Structured API JSON Output      |
                    +-------------------------------------+
```

---

## 2. 16-Dimensional Feature Vector Specification

The feature extractor converts raw code strings, AST metrics, and SAST findings into an ordered 16-dimensional vector:

| Index | Feature Dimension | Type | Description |
|---|---|---|---|
| `0` | `critical_findings_count` | `float` | Number of issues categorized as `CRITICAL` severity (e.g. `eval()`, `exec()`, remote code execution). |
| `1` | `high_findings_count` | `float` | Number of issues categorized as `HIGH` severity (e.g. SQL injection, command injection, weak crypto). |
| `2` | `medium_findings_count` | `float` | Number of issues categorized as `MEDIUM` severity (e.g. empty except blocks, suspicious imports). |
| `3` | `low_findings_count` | `float` | Number of issues categorized as `LOW` severity (e.g. line length, minor config smells). |
| `4` | `security_category_count` | `float` | Count of findings tagged with `SECURITY` or `VULNERABILITY` category. |
| `5` | `complexity_category_count` | `float` | Count of findings tagged with `COMPLEXITY` or `MAINTAINABILITY`. |
| `6` | `error_handling_category_count` | `float` | Count of findings tagged with `ERROR_HANDLING` or `EXCEPTION`. |
| `7` | `style_category_count` | `float` | Count of findings tagged with `STYLE` or `CONFIG`. |
| `8` | `ast_analyzer_findings` | `float` | Number of findings flagged by the native Python AST analyzer. |
| `9` | `bandit_analyzer_findings` | `float` | Number of findings flagged by the isolated Bandit SAST engine. |
| `10` | `max_finding_confidence` | `float` | Maximum confidence score across all findings ($0.0 \le C \le 1.0$). |
| `11` | `avg_finding_confidence` | `float` | Arithmetic mean confidence score across all findings. |
| `12` | `cyclomatic_complexity` | `float` | McCabe structural complexity computed from AST branch points ($M = E - N + 2P$). |
| `13` | `max_nesting_depth` | `float` | Deepest block nesting depth identified in the AST. |
| `14` | `finding_density_per_100_lines` | `float` | Ratio of total findings to total lines of code multiplied by 100. |
| `15` | `has_secrets_flag` | `float` | Binary flag ($1.0$ if hardcoded secrets or entropy anomalies detected, else $0.0$). |

---

## 3. Five-Stage Pipeline Implementation

### Stage 1: Feature Extraction & Structural Parsing
- Parses the Python AST safely without execution using `CodeMetricsVisitor`.
- Quantifies branching statements (`If`, `For`, `While`, `ExceptHandler`, `BoolOp`).
- Computes finding density and normalizes missing data with zero-fill.

### Stage 2: Deterministic Baseline Engine
- Applies rule-based weights to generate an interpretable baseline score:
  $$\text{Score}_{\text{base}} = \min(100, \sum (w_i \cdot \text{count}_i) + \text{ComplexityPenalty} + \text{SecretsPenalty})$$
- Floor Enforcement:
  - If `critical_findings_count > 0` or `has_secrets_flag == 1.0`, baseline is forced to $\ge 80$.
  - If `high_findings_count > 0`, baseline is forced to $\ge 55$.

### Stage 3: Scikit-learn Model Training & Preprocessing
- **Preprocessor:** Uses `StandardScaler` to normalize feature dimensions to zero mean and unit variance.
- **Model:** `RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)`.
- **Training Distribution:** 1,200 synthetic vectors stratified across 5 risk profiles (Pristine, Low Quality Smells, Moderate Complexity, Known Vulnerabilities, Critical RCE / Secrets).
- **Validation:** Evaluated on a 20% test split achieving $R^2 \ge 0.95$ and $\text{MAE} \le 3.5$ on the synthetic dataset.

### Stage 4: Score Blending
- Pristine code ($0$ findings, $0$ secrets, complexity $< 5$) evaluates to deterministic $0$.
- Non-trivial code blends predictions:
  $$\text{Score}_{\text{final}} = \text{round}\left(\text{clip}\left(0.60 \cdot \text{Score}_{\text{deterministic}} + 0.40 \cdot \text{Score}_{\text{ML}}, 0, 100\right)\right)$$

### Stage 5: Explainability Engine & Severity Classification
Maps the final integer score to severity bands:
- **`LOW`** ($0 - 24$): Clean or minor cosmetic findings.
- **`MEDIUM`** ($25 - 54$): Moderate complexity, broad exception handlers, or multiple minor smells.
- **`HIGH`** ($55 - 79$): High-severity security vulnerabilities or significant structural decay.
- **`CRITICAL`** ($80 - 100$): Dynamic code execution (`eval`), exposed secrets, unverified deserialization.

Generates dynamic human-readable `reasons` explaining precisely why the score was assigned.

---

## 4. Synthetic Data Disclaimer & Limitations

> [!IMPORTANT]
> **Synthetic Data Disclaimer:**
> The Scikit-learn regression model is trained on a mathematically modeled synthetic dataset of static code metric profiles. While this provides smooth non-linear interpolation between compound risk factors (such as high complexity combined with unhandled exceptions), it **does not claim empirical predictive validity against real-world CVE zero-day distributions**. The deterministic baseline guarantees that critical security rules are never bypassed by ML approximation.
