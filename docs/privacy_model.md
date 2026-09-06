# Privacy Model & Secret Redaction Architecture

## Overview

The **Privacy-Preserving AI Code Security Platform** enforces a defense-in-depth sanitization boundary before source code is ever evaluated for risk or processed by AI models.

Proprietary source code often contains hardcoded API tokens, database URIs with passwords, cloud credentials, or private cryptographic keys. Transmitting these secrets over external networks represents a catastrophic compliance and security hazard.

The **Privacy Protection Engine** guarantees that all secrets are detected, stripped, and substituted with immutable placeholder tokens before code ever crosses any security boundary.

---

## The 4-Phase Sanitization Pipeline

```
+---------------------+
|     Source Code     |  (Uploaded file or pasted snippet)
+----------+----------+
           |
           v
+---------------------+
| 1. Security Ingest  |  - Path traversal validation
|    & Sanitization   |  - Binary & executable rejection
+----------+----------+  - UTF-8 text verification
           |
           v
+---------------------+
| 2. Multi-Pass       |  - Pass 1: Pattern scanning (AWS, JWT, DB, Private Keys, SaaS)
|    Secret Detection |  - Pass 2: Shannon Entropy calculation (H >= 3.8)
+----------+----------+  - Pass 3: Span deduplication & line indexing
           |
           v
+---------------------+
| 3. Zero-Leak        |  - In-place right-to-left substitution
|    Redactor Engine  |  - Placeholder injection: [REDACTED_<TYPE>]
+----------+----------+  - Raw secret strings purged from finding descriptors
           |
           v
+---------------------+
| 4. Sanitized Code   |  - Safe for local AST analysis & privacy-preserved export
|    & Finding Record |  - Raw secret presence in response = 0%
+---------------------+
```

---

## Detection Techniques

### 1. Curated Pattern Signatures
The engine evaluates deterministic regex rules targeting standardized key formats:
- **Cloud Credentials**: AWS Access Key ID (`AKIA...`), AWS Secret Access Key
- **SaaS API Tokens**: GitHub (`ghp_...`, `github_pat_...`), GitLab (`glpat-...`), OpenAI (`sk-...`), Google API Key (`AIza...`), Stripe (`sk_live_...`), Slack (`xoxb-...`)
- **JSON Web Tokens (JWT)**: `eyJ...` encoded header + payload + signature
- **Database Connection Strings**: `postgresql://user:password@host/db`, `mongodb://...`, `mysql://...`
- **Private Key Blocks**: `-----BEGIN RSA PRIVATE KEY-----` and OpenSSH key envelopes
- **Generic Password Assignments**: `password = "..."`, `api_secret = "..."`

### 2. Shannon Entropy Analysis
For arbitrary pseudo-random strings (such as custom hex tokens, internal cryptographic seeds, or high-entropy API secrets):
$$H(X) = -\sum_{i=1}^n P(x_i) \log_2 P(x_i)$$
String literals exceeding $H \ge 3.8$ with length $\ge 16$ are flagged as `HIGH_ENTROPY_KEY` and redacted with `[REDACTED_HIGH_ENTROPY_KEY]`.

---

## Privacy Invariants

1. **Zero Secret Egress**: Raw secret values are NEVER present in API JSON responses, HTTP error messages, stdout/stderr logs, or persistent databases.
2. **Deterministic Placeholders**: Secrets are replaced with standardized tokens:
   - `API_KEY = "AKIA1234567890ABCDEF"` &rarr; `API_KEY = "[REDACTED_AWS_ACCESS_KEY]"`
   - `DATABASE_URL = "postgres://u:p@h/d"` &rarr; `DATABASE_URL = "[REDACTED_DATABASE_URI]"`
   - `JWT = "eyJ..."` &rarr; `JWT = "[REDACTED_JWT_TOKEN]"`
3. **Public Finding Model**:
   ```json
   {
     "secret_type": "AWS_ACCESS_KEY",
     "file": "payment_service.py",
     "line_number": 4,
     "confidence": "HIGH",
     "redaction_status": "REDACTED",
     "placeholder": "[REDACTED_AWS_ACCESS_KEY]"
   }
   ```
4. **Syntax Preservation**: Redaction preserves surrounding syntax (variable names, quotes, semicolons, brackets) so downstream static AST parsers can continue analyzing code structure without syntax errors.
