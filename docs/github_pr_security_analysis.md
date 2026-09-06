# Architecture Specification: Module 10 — GitHub Pull Request Security & Risk Analysis

## 1. Executive Summary & Design Principles

Module 10 enables development and security teams to perform automated, privacy-preserving security and risk assessments directly on **GitHub Pull Requests**.

Unlike traditional CI/CD security tools that clone full repositories and execute build scripts, this platform strictly adheres to **zero repository code execution** and **zero complete repository egress**. Analysis is performed purely by parsing unified diff patches and modified files fetched through read-only GitHub REST APIs, screening for hardcoded secrets, executing AST and Bandit static analyzers locally, predicting risk scores using Scikit-Learn ML models, and grounding AI remediations in curated engineering guidelines.

---

## 2. Security & Privacy Invariants

```
                                      GitHub Pull Request
                                  https://github.com/org/repo/pull/42
                                                   │
                                                   ↓
                                     Read-Only GitHub REST API
                             (Zero Repo Clone, In-Memory Token Handling)
                                                   │
                                                   ↓
                                    Unified Diff & Patch Parser
                            (Extract Added Lines & Filter Binary/Lockfiles)
                                                   │
                        ┌──────────────────────────┴──────────────────────────┐
                        ↓                                                     ↓
         Changed Code File 1 (app/db.py)                       Changed Code File 2 (config/app.py)
                        │                                                     │
                        ↓                                                     ↓
         Secret Detection & Redaction (M3)                     Secret Detection & Redaction (M3)
                        │                                                     │
                        ↓                                                     ↓
         Local AST & Bandit SAST (M4)                          Local AST & Bandit SAST (M4)
                        │                                                     │
                        ↓                                                     ↓
         File Risk Scoring (M5)                                File Risk Scoring (M5)
                        │                                                     │
                        └──────────────────────────┬──────────────────────────┘
                                                   │
                                                   ↓
                                   PR-Level Risk Aggregation
                                (Weighted Composite + Rule Floors)
                                                   │
                                                   ↓
                               Context Minimization (±4 Lines) (M6)
                                                   │
                                                   ↓
                              Engineering Knowledge RAG Search (M9)
                              (OWASP Standards & Incident Post-Mortems)
                                                   │
                                                   ↓
                             Tripartite AI Remediation Engine (M7/M8)
                           (DETECTED FACT, INTERPRETATION, RECOMMENDATION)
                                                   │
                                                   ↓
                                   Comprehensive PR Security Report
```

| Security Invariant | Technical Implementation |
|---|---|
| **Zero Repository Code Execution** | Repository code is never compiled, imported, executed, or passed to dynamic interpreters. |
| **Zero Git Clone / Arbitrary Script Run** | The platform does not clone git repos or execute arbitrary repo scripts (e.g. `setup.py`, `package.json` scripts, `Makefile`). |
| **Zero Complete Repository Egress** | Complete repositories are never sent to external LLMs. Only minimal sanitized context windows ($\pm 4$ lines) of specific findings are analyzed. |
| **In-Memory Credential Handling** | GitHub Personal Access Tokens (PATs) are used strictly in-memory during API calls, never persisted to disk or databases, and masked in telemetry as `ghp_***`. |
| **Minimum Required Permissions** | Requires only read access (`repo:read` or `pull_requests:read` on public/private repos). |
| **Non-Mutating Passive Analysis** | The platform is purely analytical; it never automatically merges, closes, approves, or modifies Pull Requests. |

---

## 3. Diff Parsing & File Filtering

The `DiffParser` module processes standard git unified diff hunk headers:
$$\text{Hunk Header: } @@ -old\_start,old\_count +new\_start,new\_count @@$$

1. **Line Mapping**: Tracks lines marked with `+` (additions) and ` ` (context) to map local synthetic analyzer line numbers back to actual PR line numbers on the target branch.
2. **Noise Filtering**: Automatically ignores non-code assets and generated files:
   - Lockfiles (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`, `composer.lock`, `Cargo.lock`)
   - Binary files, images, videos (`.png`, `.jpg`, `.pdf`, `.zip`, `.jar`, `.so`, `.pyc`)
   - Minified assets (`.min.js`, `.min.css`, `.map`)
   - Vendor folders (`node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`)

---

## 4. Multi-File Risk Aggregation & Deterministic Rule Floors

Let $N$ be the number of scanned code files in the PR, with individual file risk scores $R_1, R_2, \dots, R_N$.

### Composite Score Formula:
$$R_{\text{composite}} = 0.70 \times \max(R_1, \dots, R_N) + 0.30 \times \left( \frac{1}{N} \sum_{i=1}^N R_i \right)$$

### Deterministic Rule Floors:
- If `critical_findings_count` $> 0$:
  $$R_{\text{final}} = \max(R_{\text{composite}}, 85.0 + \min(5.0 \times \text{critical\_count}, 15.0))$$
- If `secrets_count` $> 0$:
  $$R_{\text{final}} = \max(R_{\text{composite}}, 80.0 + \min(4.0 \times \text{secrets\_count}, 15.0))$$
- If `high_findings_count` $> 0$ (and zero critical/secrets):
  $$R_{\text{final}} = \max(R_{\text{composite}}, 65.0 + \min(3.0 \times \text{high\_count}, 15.0))$$
- If `medium_findings_count` $> 0$ (and zero high/critical/secrets):
  $$R_{\text{final}} = \max(R_{\text{composite}}, 40.0 + \min(2.0 \times \text{med\_count}, 15.0))$$

### Risk Tiers:
- **`CRITICAL`**: $80.0 \le R \le 100.0$
- **`HIGH`**: $60.0 \le R < 80.0$
- **`MEDIUM`**: $30.0 \le R < 60.0$
- **`LOW`**: $0.0 \le R < 30.0$

---

## 5. RAG & AI Tripartite Remediation

For the top security findings in the PR:
1. **RAG Knowledge Retrieval**: Queries the 512-dimensional vector store to cite matching security guidelines (e.g. `DOC-SEC-SQLI-001`, `DOC-SEC-SECRETS-001`) and historical incident post-mortems (`DOC-INC-2024-001`).
2. **Epistemic Segregation**: Produces developer remediations cleanly partitioned into:
   - **`DETECTED FACT`**: Verified SAST finding, line number, and sanitized snippet.
   - **`AI INTERPRETATION`**: Contextual explanation of exploitability and impact.
   - **`RECOMMENDATION`**: Step-by-step remediation guidance with safe, non-executable code replacement diffs.
