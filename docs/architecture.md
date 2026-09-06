# System Architecture & Technical Specification

## 1. Architectural Paradigm: Modular Monolith

The **Privacy-Preserving AI Code Security & Risk Analysis Platform** is architected as an enterprise-grade **Modular Monolith**. Rather than introducing operational overhead with distributed microservices, network serialization latency, and complex Kubernetes orchestrators, the system achieves strict separation of concerns through well-defined in-process module boundaries, shared immutable domain contracts, and asynchronous service abstractions.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FASTAPI GATEWAY LAYER                                    │
│  [Security Headers] → [Rate Limiter] → [CORS] → [JWT Auth & RBAC] → [Router Registry]  │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
    ┌───────────────────┬─────────────────┼─────────────────┬───────────────────┐
    ↓                   ↓                 ↓                 ↓                   ↓
[Module 2: Ingest] [Module 3: Secret] [Module 4: Static] [Module 5: Risk]  [Module 9: RAG]
- Safe Parsing     - Shannon Entropy  - Python AST Visitor - RandomForest   - Vector Store
- Binary Header Def- Regex Catalog    - Bandit SAST Engine - 5-Stage ML Pipe- BM25 Grounding
- Path Normalizer  - Token Masker     - Zero-Execution     - Deterministic   - Source Citations
    │                   │                 │                 │                   │
    └───────────────────┼─────────────────┴─────────────────┼───────────────────┘
                        │                                   │
                        ↓                                   ↓
        [Module 6: Context Minimizer]           [Module 11 & 12: Audit & Telemetry]
        - Finding Extraction (±4 lines)         - Circular Session Store (500 runs)
        - Secret Scrubbing Invariant            - Circular Audit Log (5,000 events)
        - Zero Full-Repo Egress                 - RBAC & User-Scoped Query Engine
                        │
                        ↓
        [Module 7 & 8: AI Remediation Engine]
        - Epistemic Segregation (FACT / INTERPRETATION / RECOMMENDATION)
        - Dual-Mode LLMProvider (Local Ollama/vLLM vs External TLS)
        - Offline Mock Fallback (Air-gapped)
```

---

## 2. Core Subsystems & Module Breakdown

### Module 1: Foundation & Health Telemetry
- **FastAPI Core**: Async ASGI web framework with strict Pydantic v2 data validation and OpenAPI 3.1 documentation.
- **Database Abstraction**: SQLAlchemy ORM with PostgreSQL backend support and graceful offline fallback to in-memory repositories.

### Module 2: Secure Code Ingestion Layer
- **Defensive Ingestion**: Accepts raw source code text and multi-part file uploads (`.py`, `.java`, `.js`, `.ts`).
- **Path Traversal Defense**: Normalizes filenames, strips directory separators (`/`, `\`), eliminates null bytes (`\x00`), and blocks Windows reserved device names (`CON`, `PRN`, `AUX`).
- **Binary Header Detection**: Magic byte inspector rejects executable binaries (ELF `\x7fELF`, PE `MZ`, Mach-O) and non-code assets.

### Module 3: Secret Detection & Privacy Protection Engine
- **Shannon Entropy Scanner**: Calculates informational entropy ($H(X) = -\sum p(x) \log_2 p(x)$) over sliding alphanumeric windows to identify high-entropy random keys.
- **Regex Pattern Catalog**: Comprehensive rules for AWS Access Keys, OpenAI Keys, GitHub PATs, Stripe Secret Keys, Private Key Blocks, Database Connection Strings, JWTs, and Passwords.
- **Deterministic Redaction**: Masks detected values with type-specific placeholders (`[REDACTED_AWS_KEY]`) before code is logged, persisted, or processed by downstream analyzers.

### Module 4: Local Static Code Analysis Engine
- **Python AST Visitor**: Safely parses abstract syntax trees without executing submitted code (`eval()`, `exec()`, `os.system()`, `subprocess.Popen()`, `pickle.loads()`, `yaml.unsafe_load()`).
- **Bandit SAST Integration**: Dispatches local subprocess scans with security plugins.
- **Standardized Finding Schema**: Normalizes all issues into a unified schema containing `issue_id`, `title`, `category`, `severity`, `confidence`, `file`, `line_number`, `code_snippet`, and `recommendation`.

### Module 5: Code Risk Scoring & Explainability Engine
- **Interpretable Scoring Pipeline**: 
  1. Feature extraction ($N$-dimensional feature vector).
  2. Standard scaling and polynomial preprocessing.
  3. Scikit-Learn `RandomForestRegressor` inference.
  4. Deterministic severity override floors ($\ge 80.0$ for CRITICAL, $\ge 60.0$ for HIGH).
- **Human-Centric Attribution**: Explains *why* the score was generated based on vulnerability severity weights and category density.

### Module 6: Privacy-Aware AI Analysis Layer
- **Context Minimization**: Extracts strictly bounded code snippets ($\pm 4$ lines surrounding verified static analysis findings) rather than sending entire files or repositories.
- **Zero Raw Secret Invariant**: Guarantees raw secrets are never passed to external or local LLM context windows.

### Module 7 & 8: AI Developer Remediation & Local LLM Support
- **Epistemic Segregation**: Tripartite response schema strictly separating:
  - `DETECTED FACT`: Verified static analysis finding.
  - `AI INTERPRETATION`: Model reasoning and risk context.
  - `RECOMMENDATION`: Verified actionable remediation steps and safer refactored code.
- **Provider Abstraction**: Decoupled `LLMProvider` interface supporting:
  - `LocalLLMProvider`: Direct integration with self-hosted Ollama or OpenAI-compatible vLLM endpoints over local network.
  - `ExternalLLMProvider`: Secure TLS API calls.
  - `MockLLMProvider`: Zero-network offline testing simulator.

### Module 9: Privacy-Aware Engineering Knowledge RAG
- **Vector Indexing**: In-memory dense embeddings with cosine similarity matching over curated security standards, OWASP top 10 rules, CWE remediation guides, and post-mortems.
- **Source Attribution**: Retaining strict citations (`DOC-SEC-SQLI-001`) preventing artificial hallucinations.

### Module 10: GitHub Pull Request Security Scanner
- **Passive In-Memory Scanning**: Fetches pull request diffs via GitHub REST API v3 without cloning repositories, executing build scripts, or persisting tokens.

### Module 11: Engineering Security Dashboard
- **9 Core Views**: Executive Overview, Code Studio, PR Scanner, Universal Findings Catalog, Deep-Dive Audit Inspector, Privacy Guardrails, RAG Knowledge Base, Session History, and Settings.
- **Real-Time Session Store**: Circular buffer holding real analysis audit records without fake statistics.

### Module 12: Authentication, Authorization & Security Audit
- **NIST SP 800-63B Auth**: PBKDF2-HMAC-SHA256 password hashing (100,000 iterations, 32-byte salt), PyJWT tokens, and RBAC (`ADMIN` vs `DEVELOPER`).
- **Zero-Credential Audit Log**: Circular audit log sanitizing all event metadata.
