# Privacy-Aware Engineering Knowledge RAG Specification

## 1. Architectural Overview

The **Privacy-Aware Engineering Knowledge RAG Engine (Module 9)** enables developers to query security guidelines, coding standards, and historical issue post-mortems through grounded vector retrieval.

### Core Privacy & Knowledge Boundary Invariants:
1. **Zero Proprietary Code Ingestion**: The vector store **never** automatically ingests or indexes uploaded source code or repository contents. It stores strictly curated engineering knowledge documents, standards, and incident post-mortems.
2. **Strict Source Attribution**: Every retrieved chunk and explanation must explicitly cite its originating document ID, title, and section.
3. **Anti-Hallucination Guard**: The AI model is strictly prohibited from inventing non-existent documentation or fake historical post-mortems. If no evidence exceeds the relevance threshold ($\ge 0.35$), the engine returns:
   > `"No relevant evidence found."`

---

## 2. End-to-End RAG Pipeline

```
Documentation Sources
 (OWASP, Guidelines, Post-Mortems)
           ↓
   Document Chunking
 (500 chars / 50 overlap)
           ↓
   Semantic Vectorizer
(Subword & Word n-grams + L2 norm)
           ↓
    Vector Database
(In-Memory Cosine Index)
           ↓
Relevant Vector Search (Top-K)
           ↓
Relevance Threshold Gate (>= 0.35)
  ├── Below Threshold (< 0.35) → "No relevant evidence found."
  └── Above Threshold (>= 0.35) → Grounded AI Explanation + Source Attributions
```

---

## 3. Seed Knowledge Library

| Document ID | Title | Category | Key Topics |
|---|---|---|---|
| `DOC-SEC-SQLI-001` | SQL Injection Prevention & Query Parameterization | `SECURITY_GUIDELINE` | DB-API 2.0 placeholders, raw string `%` formatting risks, ORM binding |
| `DOC-SEC-RCE-001` | Safe Alternatives to Dynamic eval() and exec() | `CODING_STANDARD` | `ast.literal_eval`, arithmetic parsers, RCE mechanics |
| `DOC-SEC-CMD-001` | OS Command Injection Prevention & Subprocess | `SECURITY_GUIDELINE` | `subprocess.run(shell=False)`, `os.system` prohibition |
| `DOC-SEC-DESER-001` | Unsafe Deserialization Prevention in Python | `CODING_STANDARD` | `pickle.loads` RCE, `yaml.safe_load`, HMAC signing |
| `DOC-SEC-CREDS-001` | Secrets Management & Zero Hardcoded Credentials | `CODING_STANDARD` | `.env` variables, cloud vault integration, zero-leak policy |
| `INC-2024-001` | Post-Mortem: SQL Injection in Legacy Billing API | `HISTORICAL_INCIDENT` | Blind boolean SQLi in invoice API, parameterization migration |
| `INC-2024-002` | Post-Mortem: OS Command Injection in System Diag | `HISTORICAL_INCIDENT` | Unvalidated IP traceroute injection, `ipaddress` validation |
| `INC-2024-003` | Post-Mortem: Unsafe Pickle in Background Workers | `HISTORICAL_INCIDENT` | Redis queue deserialization exploit, JSON/Pydantic standardization |
| `INC-2024-004` | Post-Mortem: Hardcoded AWS Credentials in Test | `HISTORICAL_INCIDENT` | S3 fixture token leak, 4-minute key revocation, pre-commit hooks |
| `DOC-ARCH-PRIVACY-001` | Platform Architecture & Privacy Standards | `ARCHITECTURE_DOC` | Context minimization, zero code execution, telemetry-only logs |

---

## 4. API Endpoints

- `GET /api/rag/documents`: List all indexed engineering knowledge documents.
- `POST /api/rag/documents`: Ingest and index new project-owned documents into the vector store.
- `POST /api/rag/search`: Execute raw semantic similarity search with score ranking and threshold pruning.
- `POST /api/rag/query`: Execute full grounded RAG query returning AI answer and attributed sources.
