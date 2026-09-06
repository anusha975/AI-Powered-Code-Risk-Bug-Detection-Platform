# Privacy-Preserving AI Code Security & Risk Analysis Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.5.0-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Tests Passing](https://img.shields.io/badge/pytest-135%20passed%20(100%25)-success.svg?style=flat&logo=pytest)](https://pytest.org/)

An enterprise-grade, **zero-leak** static analysis and AI-driven code security platform. Designed as a high-performance **Modular Monolith**, it empowers engineering teams to detect vulnerabilities, intercept secrets, predict composite risk scores, and generate tripartite remediations **without transmitting proprietary source code or confidential credentials to external cloud servers**.

---

## 1. Problem Statement

Modern software teams increasingly rely on cloud-hosted LLM assistants for code reviews and vulnerability triage. However, sending unredacted enterprise codebases to external third-party AI APIs introduces severe compliance, legal, and operational risks:
1. **Proprietary Source Code Egress**: Intellectual property and confidential business logic leak outside perimeter boundaries.
2. **Secret & Credential Exposure**: Hardcoded API keys, JWTs, and database URIs risk ingestion and retention in remote AI logs or model training sets.
3. **AI Hallucinations & Fictitious Findings**: Pure LLM scanners invent non-existent CVEs with unwarranted certainty.
4. **Security Risks from Repository Cloning**: Downloading and running build scripts on untrusted repositories risks Remote Code Execution (RCE).

**This platform solves these challenges** through a local-first, zero-execution architecture combining AST/SAST static analysis as ground truth with Shannon entropy secret redaction, on-premises/air-gapped local LLMs (Ollama/vLLM), and vector-grounded RAG.

---

## 2. Platform Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  WEB DASHBOARD (React 18 + Vite)                       │
│  [Overview]  [Analyze Code]  [PR Scanner]  [Findings]  [Details]  [Privacy]  [Settings]  │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │  REST API (JSON over HTTP)
                                          ↓
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI MODULAR MONOLITH GATEWAY                          │
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

## 3. Core Modules & Capabilities

- **Module 1: Core Foundation & Health Telemetry**: FastAPI backend, PostgreSQL session handling, and real-time health telemetry.
- **Module 2: Secure Code Ingestion Layer**: Multi-language detection (`.py`, `.java`, `.js`, `.ts`), path traversal sanitization, binary header validation, and transient memory cleanup.
- **Module 3: Secret Detection & Redaction Engine**: Shannon entropy analysis ($H(X) \ge 3.8$) and multi-pattern regex matching for AWS, OpenAI, GitHub, Stripe, and Database credentials.
- **Module 4: Local Static Code Analysis Engine**: Zero-execution Python AST visitor and Bandit SAST analyzer.
- **Module 5: ML Risk & Vulnerability Predictor**: 5-stage Scikit-Learn `RandomForestRegressor` and deterministic severity rule floors.
- **Module 6: Privacy-Aware AI Analysis Layer**: Context minimization pipeline reducing code exposure surface by over 98.5%.
- **Module 7: AI Developer Remediation Engine**: Tripartite epistemic response format (`DETECTED FACT`, `AI INTERPRETATION`, `RECOMMENDATION`).
- **Module 8: Private AI & Local LLM Support**: Native support for on-premise Ollama and OpenAI-compatible vLLM endpoints with air-gapped zero-egress guarantees.
- **Module 9: Engineering Knowledge RAG**: In-memory dense vector search over curated security standards, CWE guidelines, and incident post-mortems.
- **Module 10: GitHub Pull Request Security Scanner**: Passive, non-cloning PR diff scanner with in-memory PAT lifecycle protection.
- **Module 11: Professional Engineering Security Dashboard**: 9 comprehensive views with live telemetry session store.
- **Module 12: Authentication, Authorization & Security Audit**: NIST SP 800-63B PBKDF2 password hashing, PyJWT tokens, RBAC (`ADMIN` vs `DEVELOPER`), rate limiting, security defense headers, and zero-leak audit logging.

---

## 4. The 10 Inviolable Privacy Guardrails

1. **Local-First Analysis Invariant**: Code is analyzed locally on-premises.
2. **Zero Unredacted Secret Transmission**: Raw credentials never reach an LLM.
3. **Context Minimization**: AI receives strictly bounded snippets ($\pm 4$ lines).
4. **Zero Whole-Repository Ingestion**: Complete repos are never sent to external AI.
5. **Epistemic Separation**: Detected facts, AI interpretations, and recommendations remain distinct.
6. **Local LLM Air-Gap Mode**: Full functionality supported via private Ollama/vLLM.
7. **Transient Buffer Cleanup**: Temporary file uploads purged immediately.
8. **Vector Grounding Non-Egress**: RAG databases index only public security standards.
9. **Non-Persisting Credentials**: GitHub PATs and user passwords are never stored in plaintext.
10. **Immutable Audit Sanitization**: Security audit logs strip code and secret tokens.

---

## 5. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, PyJWT.
- **Machine Learning & Static Analysis**: Scikit-Learn, NumPy, Python AST, Bandit.
- **Frontend**: React 18, Vite, Lucide Icons, Vanilla CSS Design System.
- **Testing**: Pytest, Pytest-Asyncio, HTTPX, Starlette TestClient (**135 tests, 100% passing**).
- **Documentation**: Markdown technical whitepapers in `docs/`.

---

## 6. Setup & Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### Installation
```bash
# Clone the repository
git clone https://github.com/anusha975/AI-Powered-Code-Risk-Bug-Detection-Platform.git
cd "Privacy-Preserving AI Code Security"

# Setup Backend
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt

# Setup Frontend
cd ../frontend
npm install
```

### Running the Application
```bash
# Terminal 1: Backend API (Port 8000)
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend Dashboard (Port 5173)
cd frontend
npm run dev
```
- Open Dashboard: `http://127.0.0.1:5173`
- Open API Docs: `http://127.0.0.1:8000/docs`

### Running the Test Suite
```bash
cd backend
.venv\Scripts\pytest -v
```

---

## 7. Pre-Configured Demo Credentials

| Role | Username | Email | Password | Privileges |
|---|---|---|---|---|
| **ADMIN** | `admin` | `admin@security.local` | `AdminSecret!2026` | Full platform access, multi-user audit logs, AI configuration. |
| **DEVELOPER** | `developer` | `dev@security.local` | `DevPass!2026` | Code submission, PR scanner, RAG search, personal history. |

---

## 8. Honest Limitations & Engineering Assumptions

1. **Static AST Analysis Scope**: Static AST analysis captures structural code defects (`eval()`, unsafe deserialization, SQL injection patterns) but cannot resolve dynamic runtime data flow across complex multi-service boundaries.
2. **Secret Detection Limits**: Shannon entropy and regex patterns catch high-entropy random keys and known formats, but split keys (e.g. `k = "sk-" + "part1" + "part2"`) or custom obfuscations may require manual review.
3. **In-Memory Session Store**: In development mode, session logs and audit trails use thread-safe in-memory circular repositories. For enterprise multi-node persistence, configure PostgreSQL connection strings in `.env`.
4. **Local LLM Hardware Dependency**: Running on-premise models (e.g. `llama3.2`, `deepseek-coder`) requires sufficient local VRAM / RAM on the host server.

---

## 9. Comprehensive Documentation Index

- [System Architecture](docs/architecture.md)
- [Security Architecture & Controls](docs/security.md)
- [Privacy Model & Guarantees](docs/privacy.md)
- [REST API Specification](docs/api.md)
- [Enterprise Threat Model](docs/threat-model.md)
- [Installation & Setup Guide](docs/setup.md)
