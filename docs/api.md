# REST API Specification & Endpoint Catalog

## 1. Global Standards & Authentication

- **Base URL**: `http://127.0.0.1:8000/api` (or `/api/v1`)
- **Interactive Documentation**: `http://127.0.0.1:8000/docs` (Swagger UI) or `/redoc`
- **Authentication**: JWT Bearer token in the `Authorization` header:
  ```http
  Authorization: Bearer <JWT_ACCESS_TOKEN>
  ```
- **Error Response Format**:
  ```json
  {
    "success": false,
    "status_code": 401,
    "error": "Authentication required. Please provide a valid Bearer token.",
    "error_type": "HTTP_EXCEPTION"
  }
  ```

---

## 2. Core API Endpoint Reference

### A. Health & Platform Telemetry
| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | Public | Real-time platform health, DB connectivity, and active module status. |
| `GET` | `/` | Public | Root discovery endpoint. |

### B. Authentication & Authorization (Module 12)
| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | Public | Register a new user account with secure PBKDF2 password hashing. |
| `POST` | `/auth/login` | Public (Rate-Limited) | Authenticate user credentials and return signed JWT access token. |
| `GET` | `/auth/me` | Bearer Token | Fetch authenticated user profile. |

### C. Security Audit & Compliance (Module 12)
| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/audit/events` | DEVELOPER / ADMIN | Paginated audit trail. DEVELOPER sees own logs; ADMIN sees all. |
| `GET` | `/audit/summary` | DEVELOPER / ADMIN | Aggregated audit telemetry and event breakdown. |

### D. Code Ingestion & Static Analysis (Modules 2–4)
| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/code/analyze` | Optional | Ingest code text snippet, validate constraints, and execute local static analysis. |
| `POST` | `/code/upload` | Optional | Multi-part file upload with binary validation and AST scanning. |
| `POST` | `/security/scan` | Optional | Run entropy and regex secret detector, returning sanitized code. |
| `POST` | `/analysis/python` | Optional | Direct Python AST visitor & Bandit SAST analyzer. |

### E. Risk Scoring & ML Predictor (Module 5)
| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/risk/score` | Optional | Compute deterministic and RandomForest composite risk score (0–100) and risk tier. |

### F. Privacy-Aware AI & Remediation (Modules 6–8)
| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/ai/analyze` | Optional | Execute context-minimized AI explanation without exposing secrets or whole repos. |
| `POST` | `/remediation/explain` | Optional | Generate tripartite developer explanation and safer code refactoring. |
| `GET` | `/ai/providers/catalog` | Optional | List active AI providers (Local Ollama, External, Mock). |
| `POST` | `/ai/providers/test` | Optional | Ping and health-test a local Ollama or OpenAI-compatible server. |

### G. Engineering Knowledge RAG (Module 9)
| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/rag/documents` | Optional | List all indexed security guidelines, CWE playbooks, and post-mortems. |
| `POST` | `/rag/search` | Optional | Semantic vector search for relevant security standards. |
| `POST` | `/rag/query` | Optional | Grounded Q&A against verified engineering documentation. |
| `POST` | `/rag/index` | DEVELOPER / ADMIN | Index a custom security documentation guide. |

### H. GitHub Pull Request Security (Module 10)
| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/github/pr/parse-url` | Public | Validate and parse GitHub PR URLs into owner, repo, and pull number. |
| `POST` | `/github/pr/analyze` | Optional | Passive PR diff scanner with secret redaction, AST analysis, and composite risk scoring. |

### I. Executive Dashboard Analytics (Module 11)
| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/analytics/overview` | Public | Real-time executive KPI metrics, severity distribution, and recent activity. |
| `GET` | `/analytics/history` | Optional | Paginated analysis sessions (user-scoped for DEVELOPER). |
| `GET` | `/analytics/history/{id}` | Optional | Deep-dive diagnostic inspector for an analysis session. |
| `GET` | `/analytics/findings` | Optional | Universal findings catalog with search and severity/category filters. |
