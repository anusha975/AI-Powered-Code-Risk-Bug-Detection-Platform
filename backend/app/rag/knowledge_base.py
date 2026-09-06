"""
Pre-Seeded Knowledge Base Library for Engineering Knowledge RAG.

Contains curated security guidelines, OWASP vulnerability remediation standards,
and synthetic historical incident post-mortems for developer query grounding.
"""

from typing import List
from app.schemas.rag import KnowledgeDocument, SourceType


SEED_KNOWLEDGE_DOCUMENTS: List[KnowledgeDocument] = [
    # 1. SQL Injection Prevention Guidelines
    KnowledgeDocument(
        doc_id="DOC-SEC-SQLI-001",
        title="SQL Injection Prevention & Query Parameterization Standard",
        source_type=SourceType.SECURITY_GUIDELINE,
        author="AppSec Architecture Team",
        tags=["sql", "injection", "owasp-a03", "database", "parameterization"],
        content="""# SQL Injection Prevention & Query Parameterization Standard

## Overview
SQL Injection (SQLi) occurs when untrusted user input is directly concatenated, formatted, or interpolated into SQL command strings, allowing attackers to manipulate database queries and bypass authorization.

## Root Cause
- Using Python `%` string formatting: `cursor.execute("SELECT * FROM users WHERE id = '%s'" % user_id)`
- Using Python f-strings: `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")`
- Using `str.format()` or `+` string concatenation in database statements.

## Mandatory Remediation Standard
Always use DB-API 2.0 parameterized queries with positional or named placeholder binding.

### Safe Implementation:
```python
# PostgreSQL (psycopg2) / SQLite parameterization:
cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))

# SQLite parameterization:
cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
```

## ORM Guidelines
When using SQLAlchemy or Django ORM, always use bound parameters. Never invoke `.filter(text(...))` with raw unescaped strings.
"""
    ),

    # 2. Dynamic Code Execution Guidelines (eval / exec)
    KnowledgeDocument(
        doc_id="DOC-SEC-RCE-001",
        title="Safe Alternatives to Dynamic eval() and exec() in Python",
        source_type=SourceType.CODING_STANDARD,
        author="Core Platform Security Team",
        tags=["eval", "exec", "rce", "ast", "literal_eval"],
        content="""# Safe Alternatives to Dynamic eval() and exec() in Python

## Overview
Python's built-in `eval()` and `exec()` functions parse and execute raw string inputs directly inside Python's CPython interpreter bytecode engine. Supplying untrusted data to `eval()` results in Critical Remote Code Execution (RCE).

## Vulnerability Mechanics
An attacker can invoke arbitrary system calls or spawn reverse shells via payloads such as:
`__import__('os').system('cat /etc/passwd')`

## Approved Secure Remediation Patterns

### 1. Evaluating Data Literals (Dictionaries, Lists, Numbers):
Use `ast.literal_eval()`, which strictly parses standard Python literal structures without executing code:
```python
import ast

# SAFE: Parses strings like "{'amount': 100, 'currency': 'USD'}" securely
safe_data = ast.literal_eval(untrusted_payload_str)
```

### 2. Evaluating Mathematical Expressions:
Use a dedicated arithmetic parser (such as `pyparsing` or an explicit AST math visitor) that enforces an allowlist of numerical operators (`+`, `-`, `*`, `/`).
"""
    ),

    # 3. Command Injection Prevention Guidelines
    KnowledgeDocument(
        doc_id="DOC-SEC-CMD-001",
        title="OS Command Injection Prevention & Subprocess Execution Guidelines",
        source_type=SourceType.SECURITY_GUIDELINE,
        author="AppSec Architecture Team",
        tags=["command-injection", "subprocess", "shell", "os-system"],
        content="""# OS Command Injection Prevention & Subprocess Execution Guidelines

## Overview
Command injection occurs when an application executes host operating system commands using unsanitized user inputs, enabling attackers to execute arbitrary shell commands with the privileges of the application process.

## Unsafe Functions to Avoid
- `os.system(...)`
- `os.popen(...)`
- `subprocess.Popen(..., shell=True)`
- `subprocess.run(..., shell=True)`

## Safe Remediation Standard
Always invoke external processes using `subprocess.run()` or `subprocess.Popen()` with argument lists and `shell=False` (the default).

### Safe Implementation:
```python
import subprocess

# SAFE: Arguments are passed as an array directly to the OS execve() syscall
result = subprocess.run(
    ["ping", "-c", "1", sanitized_ip],
    capture_output=True,
    text=True,
    check=True,
    shell=False  # Mandatory: do not invoke system shell
)
```
"""
    ),

    # 4. Unsafe Deserialization Guidelines (pickle / yaml)
    KnowledgeDocument(
        doc_id="DOC-SEC-DESER-001",
        title="Unsafe Deserialization Prevention in Python (Pickle & PyYAML)",
        source_type=SourceType.CODING_STANDARD,
        author="Core Security Team",
        tags=["deserialization", "pickle", "yaml", "rce"],
        content="""# Unsafe Deserialization Prevention in Python (Pickle & PyYAML)

## Overview
Python's `pickle` module is not secure against erroneous or maliciously constructed data. The unpickling process can instantiate arbitrary Python objects and execute `__reduce__()` methods during reconstruction, leading to Remote Code Execution.

## Prohibited Functions with Untrusted Input
- `pickle.loads(payload)`
- `pickle.load(file)`
- `yaml.load(payload, Loader=yaml.Loader)` (Use `yaml.safe_load` instead)
- `marshal.loads(...)`

## Mandatory Secure Standards
- For data interchange, use `json.loads()` or Protocol Buffers.
- For structured configuration files, use `yaml.safe_load()`.
- If binary caching is required, sign payloads cryptographically with HMAC-SHA256 before pickling, and verify the signature before unpickling.
"""
    ),

    # 5. Secrets Management & Hardcoded Credential Guidelines
    KnowledgeDocument(
        doc_id="DOC-SEC-CREDS-001",
        title="Secrets Management & Zero Hardcoded Credentials Policy",
        source_type=SourceType.CODING_STANDARD,
        author="InfraSec & Governance Team",
        tags=["secrets", "credentials", "api-keys", "environment-variables"],
        content="""# Secrets Management & Zero Hardcoded Credentials Policy

## Policy Requirement
No source code, configuration file, dockerfile, or repository artifact may contain plaintext passwords, API keys, database credentials, JWT secrets, or private keys.

## Approved Secrets Retrieval Architecture
1. **Local Development**: Load secrets via `.env` files parsed using `python-dotenv` or Pydantic `Settings`. Ensure `.env` is listed in `.gitignore`.
2. **Production Workloads**: Retrieve credentials dynamically from cloud vault services (e.g. AWS Secrets Manager, HashiCorp Vault, Azure Key Vault).
3. **Environment Injection**: Inject credentials as container runtime environment variables (`os.environ["AWS_SECRET_KEY"]`).
"""
    ),

    # 6. Synthetic Historical Incident Post-Mortem 1: Billing SQL Injection
    KnowledgeDocument(
        doc_id="INC-2024-001",
        title="Post-Mortem: Incident INC-2024-001 - SQL Injection in Legacy Billing API",
        source_type=SourceType.HISTORICAL_INCIDENT,
        author="Incident Response & Retrospective Team",
        tags=["incident", "postmortem", "sqli", "billing", "retrospective"],
        content="""# Post-Mortem: Incident INC-2024-001 - SQL Injection in Legacy Billing API

## Incident Summary
On March 14, 2024, a security researcher reported a boolean-based blind SQL injection vulnerability in the legacy invoice query endpoint (`/api/billing/invoices?account_id=...`).

## Root Cause Analysis
The legacy billing controller formatted SQL strings directly:
`query = "SELECT * FROM invoices WHERE account_id = '%s'" % account_id`
An attacker passing `1' OR '1'='1` was able to enumerate invoice metadata for adjacent accounts.

## Corrective Actions Implemented
1. All raw string formatting in `billing_service.py` was migrated to parameterized queries (`cursor.execute("... WHERE account_id = %s", (account_id,))`).
2. Added AST static analysis rules in CI pipeline to block raw SQL string interpolation.
3. Added automated regression integration test cases verifying payload rejection.
"""
    ),

    # 7. Synthetic Historical Incident Post-Mortem 2: Diagnostic Network Command Injection
    KnowledgeDocument(
        doc_id="INC-2024-002",
        title="Post-Mortem: Incident INC-2024-002 - OS Command Injection in System Diagnostics",
        source_type=SourceType.HISTORICAL_INCIDENT,
        author="Incident Response Team",
        tags=["incident", "postmortem", "command-injection", "rce", "diagnostics"],
        content="""# Post-Mortem: Incident INC-2024-002 - OS Command Injection in System Diagnostics

## Incident Summary
On June 22, 2024, during an internal red-team exercise, engineers discovered that the diagnostic network utility allowed arbitrary shell command execution via crafted IP parameters.

## Root Cause Analysis
The diagnostic service executed `os.system(f"traceroute -m 5 {server_ip}")`. The parameter `server_ip` was not validated as a valid IPv4/IPv6 address, enabling injection via semicolons (`127.0.0.1; whoami`).

## Corrective Actions Implemented
1. Replaced `os.system()` with `subprocess.run(["traceroute", "-m", "5", ip], shell=False, check=True)`.
2. Enforced strict IP address parsing via Python's `ipaddress.ip_address()` validator before passing parameters.
3. Deployed Bandits static security rules flagging any `os.system` invocation.
"""
    ),

    # 8. Synthetic Historical Incident Post-Mortem 3: Unsafe Pickle Deserialization
    KnowledgeDocument(
        doc_id="INC-2024-003",
        title="Post-Mortem: Incident INC-2024-003 - Unsafe Pickle Caching in Background Workers",
        source_type=SourceType.HISTORICAL_INCIDENT,
        author="Platform Reliability Team",
        tags=["incident", "postmortem", "pickle", "deserialization", "caching"],
        content="""# Post-Mortem: Incident INC-2024-003 - Unsafe Pickle Caching in Background Workers

## Incident Summary
On September 5, 2024, an audit identified that message queue consumers were unpickling cache payloads directly from an unauthenticated Redis cluster.

## Root Cause Analysis
Background tasks invoked `pickle.loads(redis.get(task_key))`. A compromised worker node could publish serialized bytecode leading to lateral privilege escalation.

## Corrective Actions Implemented
1. Completely deprecated `pickle` across all worker queues.
2. Standardized on `json.loads()` and `Pydantic` schema validation for all message payloads.
3. Implemented Redis connection authentication and TLS in transit.
"""
    ),

    # 9. Synthetic Historical Incident Post-Mortem 4: AWS Token Leakage
    KnowledgeDocument(
        doc_id="INC-2024-004",
        title="Post-Mortem: Incident INC-2024-004 - Hardcoded AWS Credentials in Test Fixture",
        source_type=SourceType.HISTORICAL_INCIDENT,
        author="Security Operations Center",
        tags=["incident", "postmortem", "aws", "secrets", "credentials"],
        content="""# Post-Mortem: Incident INC-2024-004 - Hardcoded AWS Credentials in Test Fixture

## Incident Summary
On November 11, 2024, an automated commit scanning tool detected an AWS access key committed to a test fixture file (`test_s3_upload.py`).

## Root Cause Analysis
A developer used real staging credentials inside a mock test file to debug S3 file uploads locally and inadvertently committed the file to the repository.

## Corrective Actions Implemented
1. Revoked the exposed AWS IAM access key immediately within 4 minutes of detection.
2. Installed pre-commit git hooks using entropy and regex secret scanners to reject commits containing API tokens.
3. Implemented local S3 emulation with Moto/LocalStack for local unit tests.
"""
    ),

    # 10. Platform Architecture Standards
    KnowledgeDocument(
        doc_id="DOC-ARCH-PRIVACY-001",
        title="Privacy-Preserving AI Code Security Platform Architecture Standards",
        source_type=SourceType.ARCHITECTURE_DOC,
        author="Chief Security Architect",
        tags=["architecture", "privacy", "invariants", "pipeline"],
        content="""# Privacy-Preserving AI Code Security Platform Architecture Standards

## Core Privacy Invariants
1. **Zero Raw Code Execution**: Uploaded and analyzed source code is never executed, imported, or run in a subprocess.
2. **Deterministic Pre-Processing**: Secret detection & in-place placeholder redaction (`[REDACTED_<TYPE>]`) must occur *before* any AI processing.
3. **Context Minimization Window**: Only isolated snippet windows (±4 lines around flagged findings) enter the AI layer.
4. **Zero-Code Retention in Logs**: Telemetry logs record operational metadata (timestamps, model IDs, finding counts, character lengths) but strictly zero source code or prompts.
5. **Non-Blocking Graceful Degradation**: If AI services are offline or disabled, static analysis and risk scoring continue with 100% fidelity.
"""
    )
]
