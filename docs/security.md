# Platform Security Architecture & Controls

## 1. Security Invariants

The platform enforces 6 non-negotiable security invariants across all execution paths:

| Invariant | Implementation Mechanism | Enforcement Point |
|---|---|---|
| **Zero Source Code Execution** | Code is analyzed purely via Abstract Syntax Tree (`ast.parse`) and static pattern matching. Dynamic execution (`eval`, `exec`, `importlib`, `compile`) is prohibited. | Module 2 & 4 Ingestion / AST Visitor |
| **Zero Arbitrary Repo Cloning** | Pull requests are analyzed purely via REST unified diff text streams. No `git clone` or external build tools (`setup.py`, `Makefile`) are invoked. | Module 10 Diff Parser |
| **Zero Raw Credential Storage** | Secret strings detected by regex or Shannon entropy are replaced with placeholders (`[REDACTED_API_KEY]`) immediately upon receipt. | Module 3 & 12 Redactor / Audit Logger |
| **Zero Token Persistence** | GitHub Personal Access Tokens (PATs) exist strictly in transient RAM for the duration of the HTTP request and are masked (`ghp_****`) in logs. | Module 10 GitHub Client |
| **Constant-Time Verification** | Password hashes and cryptographic tokens are compared using `hmac.compare_digest` to eliminate timing side-channel attacks. | Module 12 PasswordHasher |
| **Strict Epistemic Separation** | AI responses cannot claim certain discovery of vulnerabilities; static analysis remains the authoritative detection engine. | Module 7 Response Validator |

---

## 2. Authentication & Authorization (RBAC)

### Password Hashing Specification (NIST SP 800-63B)
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Work Factor**: 100,000 iterations
- **Salt**: 32-byte cryptographically secure random salt generated via `secrets.token_bytes(32)`.
- **Format**: `pbkdf2_sha256$100000$<salt_hex>$<hash_hex>`

### JWT Token Lifecycle
- **Signing Algorithm**: HMAC-SHA256 (`HS256`)
- **Claims**: `sub` (User UUID), `username`, `role`, `email`, `exp`, `iat`, `jti` (unique UUID for replay defense).
- **Default TTL**: 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES = 1440`).

### Role-Based Access Control Matrix
| Resource / Action | Anonymous / Guest | DEVELOPER | ADMIN |
|---|---|---|---|
| Health Check & Root Info | Read | Read | Read |
| Code Analysis Submission | Allowed (Dev) | Allowed | Allowed |
| GitHub PR Scan | Allowed (Dev) | Allowed | Allowed |
| View Own Analysis History | Local Session | Allowed | Allowed |
| View All Users' Analysis History | Denied | Denied | Allowed |
| View Security Audit Logs | Denied | Own Events Only | All Events |
| Update Platform AI Config | Denied | Denied | Allowed |
| RAG Knowledge Base Search | Allowed | Allowed | Allowed |
| Index Custom Security Document | Denied | Allowed | Allowed |

---

## 3. Defense-in-Depth HTTP Protections

### Standard Security Headers
All HTTP responses passing through `SecurityHeadersMiddleware` are injected with hardened defense headers:
- `X-Content-Type-Options: nosniff` (Prevents MIME-type sniffing).
- `X-Frame-Options: DENY` (Mitigates clickjacking attacks).
- `X-XSS-Protection: 1; mode=block` (Enforces legacy browser XSS filters).
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Enforces HTTPS).
- `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';` (Restricts script and frame origins).
- `Referrer-Policy: strict-origin-when-cross-origin` (Protects referrer leakage).
- `Permissions-Policy: geolocation=(), camera=(), microphone=()` (Disables unnecessary browser hardware APIs).
- `X-Privacy-Assurance: zero-raw-secret-leakage-guarantee` (Explicit security attestation).

### Rate Limiting (Brute-Force & Denial of Service Defense)
- **Authentication Route** (`POST /api/auth/login`): 10 requests / minute per client IP. Returns `429 Too Many Requests` with `Retry-After: 60`.
- **Heavy Analysis Routes** (`POST /api/code/*`, `POST /api/analysis/*`, `POST /api/github/pr/*`): 30 requests / minute per client IP.

### Centralized Exception Sanitization
Global FastAPI exception handlers intercept:
- `StarletteHTTPException`: Standardizes error payloads into `{ "success": false, "status_code": N, "error": "...", "error_type": "..." }`.
- `RequestValidationError`: Formats Pydantic validation errors cleanly without disclosing server implementation internals.
- `Exception`: Catches unhandled errors, logs traceback internally, and returns generic HTTP 500 without leaking stack traces to the client.
