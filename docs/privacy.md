# Privacy Model & Data Protection Guarantees

## 1. Core Privacy Philosophy: Zero Unauthorized Egress

The primary purpose of the Privacy-Preserving AI Code Security Platform is to empower engineering teams to harness static analysis and artificial intelligence **without transmitting proprietary source code or confidential secrets to external cloud servers**.

---

## 2. The 10 Inviolable Privacy Guardrails

```
 1. Local-First Analysis Invariant: Code is analyzed locally on-premises.
 2. Zero Unredacted Secret Transmission: Raw credentials never reach an LLM.
 3. Context Minimization: AI receives strictly bounded snippets (±4 lines).
 4. Zero Whole-Repository Ingestion: Entire repos are never uploaded to AI.
 5. Epistemic Separation: Facts, AI interpretations, and recommendations remain distinct.
 6. Local LLM Air-Gap Mode: Full functionality supported via private Ollama/vLLM.
 7. Transient Buffer Cleanup: Temporary file uploads purged immediately.
 8. Vector Grounding Non-Egress: RAG databases index only public security standards.
 9. Non-Persisting Credentials: GitHub PATs and user passwords are never stored in plaintext.
10. Immutable Audit Sanitization: Security audit logs strip code and secret tokens.
```

---

## 3. Privacy-Preserving Pipeline (7-Stage Workflow)

```
[1. Source Code / PR Diff]
           │
           ↓
[2. Shannon Entropy & Regex Secret Detection]
           │
           ↓
[3. In-Memory Redaction ([REDACTED_API_KEY])]
           │
           ↓
[4. Local AST & Bandit Static Analysis]
           │
           ↓
[5. Top Finding Selection (Max N issues)]
           │
           ↓
[6. Context Window Minimization (±4 Lines)]
           │
           ↓
[7. Sanitized AI Query (Local LLM or Mock)]
```

### Context Minimization Mechanics
Instead of transmitting 5,000 lines of an application repository to an LLM, Module 6 extracts only the minimal code context required to explain a verified static analysis finding:
- **Finding Line**: Line 42 (`result = eval(user_input)`).
- **Surrounding Context**: Lines 38–46 ($\pm 4$ lines).
- **Sanitization Check**: Verifies all variable names and strings in the window have been scrubbed of high-entropy credentials.
- **Payload Volume**: Reduces data exposure surface by over **98.5%**.

---

## 4. Privacy Assurance Modes

| Mode | LLM Location | Network Egress | Use Case |
|---|---|---|---|
| `LOCAL_STATIC_ONLY` / `AI Disabled` | None | **Zero (Air-Gapped)** | Highly classified, air-gapped, or regulated environments (HIPAA, FedRAMP). |
| `Private / Local LLM` | On-Premises Server (Ollama/vLLM) | **Zero External Internet Egress** (Local Subnet Only) | Enterprise on-premise deployments with dedicated GPU infrastructure. |
| `External LLM` | Cloud Provider (TLS API) | **Sanitized Minimal Snippets Only** (Zero Secrets, Zero Repos) | Cloud-enabled teams seeking advanced reasoning with strict context scrubbing. |
