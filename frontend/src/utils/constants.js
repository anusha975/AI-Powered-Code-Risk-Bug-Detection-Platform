/**
 * System Constants and Privacy Safeguards Definition for the Frontend.
 */

export const PRIVACY_PRINCIPLES = [
  {
    id: 1,
    title: "Source Code is Sensitive",
    description: "All repository files are treated as confidential assets with zero unapproved external exposure.",
    tag: "STRICT_ASSET"
  },
  {
    id: 2,
    title: "Never Send Full Repositories to Remote LLMs",
    description: "Prohibits raw multi-file codebase transmission over external networks.",
    tag: "ZERO_BATCH_LEAK"
  },
  {
    id: 3,
    title: "Local/Static Analysis First",
    description: "All AST inspection, syntax validation, and SAST rules execute locally on the host machine.",
    tag: "LOCAL_FIRST"
  },
  {
    id: 4,
    title: "Secret Detection & Redaction",
    description: "Entropy and pattern scanners mask API keys, tokens, and credentials before any analysis.",
    tag: "PRE_ENRICHMENT"
  },
  {
    id: 5,
    title: "Context Minimization",
    description: "Only isolated, critical AST function nodes (max 50 lines) are ever extracted for deep inspection.",
    tag: "LEAST_PRIVILEGE"
  },
  {
    id: 6,
    title: "No-LLM Analysis Mode",
    description: "Full vulnerability scanning and rule matching works 100% offline without AI dependencies.",
    tag: "OFFLINE_READY"
  },
  {
    id: 7,
    title: "Private / Self-Hosted LLM Ready",
    description: "Architectural support for air-gapped local models (vLLM, Ollama, on-premise endpoints).",
    tag: "AIRGAP_READY"
  },
  {
    id: 8,
    title: "Zero Source Code Execution",
    description: "Uploaded or target files are parsed strictly as AST nodes and text. Code is never run or evaluated.",
    tag: "NO_EXEC"
  },
  {
    id: 9,
    title: "Zero Arbitrary Git Execution",
    description: "Cloning and parsing mechanisms avoid running arbitrary build, make, or setup scripts.",
    tag: "SANDBOX_SAFE"
  },
  {
    id: 10,
    title: "Zero Hardcoded Credentials",
    description: "Strict environment-driven configuration with zero committed secrets or API tokens.",
    tag: "ENV_ISOLATED"
  }
];

export const ARCHITECTURE_LAYERS = [
  {
    name: "API & Ingestion Layer",
    module: "backend/app/api/",
    description: "FastAPI endpoints handling health telemetry, authenticated requests, and schema validation.",
    status: "ACTIVE"
  },
  {
    name: "Security & Redaction Engine",
    module: "backend/app/security/",
    description: "Secret entropy scanner, token masking, context minimization, and privacy guardrails.",
    status: "FOUNDATION"
  },
  {
    name: "Static AST & SAST Analyzers",
    module: "backend/app/analyzers/",
    description: "Python AST parsing, Bandit security linting, and Semgrep pattern matching engine.",
    status: "FOUNDATION"
  },
  {
    name: "Database & Storage Layer",
    module: "backend/app/database/",
    description: "PostgreSQL with SQLAlchemy ORM storing scan audit logs (zero raw code storage).",
    status: "ACTIVE"
  }
];
