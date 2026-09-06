# Privacy-Aware AI Analysis & Context Minimization Pipeline

**Module:** Module 6: Privacy-Aware AI Analysis Layer  
**Status:** Active  
**Core Guarantee:** Zero Whole-Repository Exposure, Mandatory Secret Redaction, Context Window Minimization ($\pm 4$ lines), and Zero Code Retention in Audit Logs.

---

## 1. The 7-Stage Privacy Pipeline

To eliminate the security risks of transmitting proprietary codebases to external LLMs, this system enforces a strict 7-stage unidirectional pipeline:

```
[1. Raw Source Code Ingestion]
             |
             v
[2. Secret Detection & Redaction]
   - Scans for AWS, OpenAI, GitHub, DB URIs, JWTs, RSA Keys, high-entropy tokens
   - Deterministically replaces secrets with [REDACTED_<TYPE>]
             |
             v
[3. Local Static Code Analysis]
   - 100% offline Python AST visitor + isolated Bandit SAST
   - Normalizes security findings into structured schema
             |
             v
[4. Code Risk Scoring Engine]
   - Evaluates 16-feature vector via Scikit-learn RandomForest regression
   - Computes composite risk score (0-100) and risk tier
             |
             v
[5. Privacy Context Minimization]
   - Filters to Top 3 critical findings
   - Extracts minimal bounding snippet window (±4 lines around finding)
   - Annotates line numbers and verifies zero residual raw secrets
             |
             v
[6. LLM Provider Abstraction]
   - Transmits ONLY the minimized snippet and finding metadata
   - Enforces strict timeout guard (10s) and rate-limit backoff
             |
             v
[7. Privacy Audit Logging & Delivery]
   - Records metadata only (model, status, latency, character count)
   - ZERO source code, ZERO prompts, ZERO secrets stored permanently
```

---

## 2. Context Minimization Architecture

### Why Context Minimization Matters
Traditional AI code assistants send entire files or multi-file workspace contexts to cloud providers. This platform limits the attack surface by transmitting only the minimum bounding context required for an LLM to comprehend the vulnerability:

```
FULL REPOSITORY / FILE (1,000+ lines)  --- [BLOCK] ---> NEVER SENT TO AI
                                                              |
                                                              v
MINIMIZED CONTEXT WINDOW (±4 lines)   --- [ALLOW] ---> SENT TO AI
```

### Minimized Payload Specification
```json
{
  "finding_id": "AST-SEC-EVAL-001",
  "issue_title": "Dangerous Dynamic Code Execution (eval)",
  "severity": "CRITICAL",
  "line_number": 12,
  "start_line": 8,
  "end_line": 16,
  "context_snippet": "    8 | def handle_request(payload):\n    9 |     # Sanitized token: [REDACTED_API_KEY]\n   10 |     target = payload.get('code')\n   11 |\n>> 12 |     result = eval(target)\n   13 |\n   14 |     return result",
  "char_count": 218,
  "has_redactions": true
}
```

---

## 3. LLM Provider Abstraction

The system decouples analysis logic from specific AI vendors via the `LLMProvider` abstract base class:

| Provider Class | Environment | Capabilities | Security Profile |
|---|---|---|---|
| **`MockLLMProvider`** | Offline / CI / Dev | Deterministic, context-aware remediation templates. | 100% Air-Gapped, Zero Network I/O. |
| **`LocalLLMProvider`** | On-Premise / Edge | Queries local Ollama or vLLM instance on `localhost:11434`. | Air-Gapped, Zero Cloud Transmission. |
| **`ExternalLLMProvider`** | Cloud TLS | OpenAI/Anthropic/Gemini compatible API with strict timeouts. | Transmits only minimized, sanitized snippets. |

---

## 4. Graceful Degradation & Non-Blocking Resilience

If AI services are disabled or unavailable, the system **never fails the user request**. Instead, it gracefully returns complete local static analysis results, risk scores, and an informative degradation status:

| Failure Scenario | AI Status | System Behavior |
|---|---|---|
| `AI_ENABLED=false` | `AI_DISABLED` | Returns static AST/Bandit findings and risk score; skips AI calls. |
| Clean code (0 findings) | `SKIPPED_CLEAN` | Explanations skipped for clean code; returns 0-risk score. |
| Provider timeout ($> 10$s) | `DEGRADED_TIMEOUT` | Aborts AI request, logs audit event, returns complete static findings. |
| Provider rate limit (429) | `DEGRADED_RATE_LIMITED` | Catches 429 status, logs telemetry, returns complete static findings. |
| Provider error (5xx / network) | `DEGRADED_ERROR` | Logs error diagnostic, returns complete static findings. |

---

## 5. Inviolable Privacy Audit Log Guarantees

The `AIAuditLogger` records telemetry for compliance and monitoring while enforcing strict privacy invariants:

```json
{
  "event_id": "9d41b53e-8c3b-4f9e-a0e2-1248a31e8f9b",
  "timestamp": "2026-09-06T12:00:00Z",
  "provider": "MockLLMProvider (Offline)",
  "model": "privacy-guard-mock-v1",
  "status": "SUCCESS",
  "findings_count": 2,
  "payload_chars": 432,
  "latency_ms": 24.5,
  "details": null
}
```

> [!CAUTION]
> **Zero Code Invariant:**
> The audit logger API does not accept source code or prompt text parameters. No proprietary code is ever persisted in database logs, disk traces, or telemetry records.
