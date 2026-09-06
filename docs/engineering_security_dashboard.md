# Technical Architecture: Module 11 — Professional Engineering Security Dashboard

## 1. Executive Summary & Design Principles

Module 11 introduces a production-grade, multi-view developer and security operations console for the **Privacy-Preserving AI Code Security & Risk Analysis Platform**.

The dashboard is engineered to provide full operational visibility into codebase health, security vulnerabilities, PR risk profiles, and historical scan audits while enforcing **strict privacy guarantees** and **zero fake statistics**.

---

## 2. 9-View System Architecture

```
                                      Executive Top Navigation
                      ┌─────────────────────────────────────────────────────────┐
                      │  Active AI Mode  •  Privacy Assurance  •  Health Status │
                      └─────────────────────────────────────────────────────────┘
                                                   │
        ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
        ↓                                          ↓                                          ↓
 [1] Overview                               [2] Analyze Code                           [3] PR Analysis
 • Real-time live KPIs                      • Code submission & file upload            • GitHub PR scanner (M10)
 • High-risk & critical counts              • AST & Bandit SAST engine                 • Multi-file diff viewer
 • Severity & category distribution         • Scikit-learn ML risk scoring             • Composite risk gauge
 • Recent scans live feed                   • Tripartite AI remediation                • RAG-grounded remediations

        ↓                                          ↓                                          ↓
 [4] Findings Catalog                       [5] Analysis Details                       [6] Security & Privacy
 • Unified multi-scan findings              • Deep-dive diagnostic inspector           • 10 Inviolable Guardrails
 • Severity & category filter pills         • Line-mapped code & diff context          • Secret scanner playground
 • Instant search & recommendations         • Tripartite epistemic breakdown           • Zero-code audit telemetry

        ↓                                          ↓                                          ↓
 [7] Knowledge Base (RAG)                   [8] Analysis History                       [9] Settings & Config
 • Curated OWASP standards                  • Historical audit logs                    • AI Provider mode switcher
 • Historical post-mortems                  • Paginated execution history              • Local Ollama / vLLM probes
 • Semantic vector search & Q&A             • Click-to-inspect routing                 • Telemetry polling rate
```

---

## 3. Real Telemetry & Non-Fake Statistics Invariant

All metrics surfaced on the dashboard are computed dynamically from active in-memory session records and real static/ML analysis results:

| Telemetry Metric | Computation & Source |
|---|---|
| **Analyses Performed** | Exact count of completed code and PR security sessions in `AnalysisSessionStore`. |
| **High-Risk Analyses** | Count of sessions evaluated with `risk_level` in `('HIGH', 'CRITICAL')` or `risk_score` $\ge 60.0$. |
| **Critical Findings** | Total count of static analysis findings with `severity == 'CRITICAL'`. |
| **Security Findings** | Total count of issues belonging to the `SECURITY` and `SECRETS` categories. |
| **Average Risk Score** | Mean arithmetic risk score: $\bar{R} = \frac{1}{N} \sum_{i=1}^N R_i$ across all recorded sessions. |
| **Secrets Redacted** | Total number of sensitive credentials detected, intercepted, and substituted with placeholders. |

---

## 4. Prominent Privacy Indicators & Epistemic Segregation

### A. Persistent Top-Bar Privacy Indicator:
The dashboard prominently renders the active AI operation mode at all times:
- **`AI MODE: Disabled`**: 100% deterministic local static analysis.
- **`AI MODE: External LLM`**: Cloud TLS connection with secret redaction and $\pm 4$ line context minimization.
- **`AI MODE: Private/Local LLM`**: Local air-gapped server (Ollama / vLLM) with **zero external network egress**.

### B. Inviolable Privacy Assurance Banner:
```
🔒 Secrets detected and redacted before AI analysis. Zero raw credentials or complete repositories transmitted.
```

### C. Analysis Details Inspector:
Provides deep-dive diagnostic inspection with tripartite epistemic segregation:
1. **`DETECTED FACT`**: Verified static analysis finding, issue code, exact line number, and sanitized code snippet.
2. **`AI INTERPRETATION`**: Contextual explanation of exploitability, business impact, and risk drivers.
3. **`RECOMMENDATION`**: Actionable remediation steps with verified safer replacement code diffs.
4. **`EVIDENCE (RAG)`**: Cited engineering standards and historical incident post-mortems with similarity scores.
