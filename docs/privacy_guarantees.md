# Privacy & Security Guarantees

This document outlines the **10 Inviolable Security Principles** governing the design and execution of the Privacy-Preserving AI Code Security & Risk Analysis Platform.

---

### Principle 1: Source Code is Sensitive Asset Data
All source code files analyzed by this system are classified as confidential proprietary assets. No code is transmitted to third-party endpoints or stored outside the verified database boundary without explicit operator policy.

### Principle 2: Never Send Full Repositories to Remote LLMs
The platform prohibits batch transmission of raw repositories, full directory trees, or unreviewed files to any external LLM provider.

### Principle 3: Local/Static Analysis Before AI Processing
Every code artifact is first processed through local static analysis engines (Python AST, Bandit, rule scanners) to detect vulnerabilities locally before any secondary analysis is considered.

### Principle 4: Mandatory Secret Detection & Redaction
High-entropy strings, API keys, passwords, bearer tokens, private keys, and environment values are detected and masked/redacted *before* any text is forwarded to any AI context window.

### Principle 5: Context Minimization
When AI enrichment is used, the system extracts only the specific targeted AST function snippet (maximum line thresholds enforced) rather than the surrounding file or module.

### Principle 6: Support for 100% No-LLM Analysis Mode
The platform is fully operational in `LOCAL_STATIC_ONLY` mode. Organizations with zero-cloud-AI mandates can operate the full vulnerability scanning suite offline.

### Principle 7: Support for Private / Self-Hosted LLMs
The architecture provides interchangeable interfaces to point toward on-premise or local models (e.g., vLLM, Ollama, local Hugging Face instances) within air-gapped perimeters.

### Principle 8: Zero Code Execution
Uploaded or scanned source code is strictly treated as static AST data. The backend does not run, compile, evaluate (`eval()`), or execute submitted scripts under any circumstances.

### Principle 9: Zero Arbitrary Git Execution
Remote repository clones and branch scans are parsed safely without invoking arbitrary build scripts, pre-commit hooks, or setup scripts.

### Principle 10: Zero Hardcoded Credentials
All credentials, database passwords, and connection strings are strictly injected through environment variables and validated through Pydantic settings.
