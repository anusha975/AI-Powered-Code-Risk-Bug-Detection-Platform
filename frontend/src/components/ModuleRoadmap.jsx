import React from 'react';
import { Compass, CheckCircle2, Clock, ShieldCheck, Cpu, Code2, GitPullRequest, BrainCircuit, FileCode2, ShieldAlert, Sparkles, Server, BookOpen } from 'lucide-react';

const MODULES = [
  {
    id: "module-1",
    title: "Module 1: Foundation & Telemetry",
    status: "ACTIVE",
    icon: CheckCircle2,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "FastAPI Modular Monolith backend structure",
      "PostgreSQL engine & resilient session management",
      "Health & Telemetry endpoint (GET /api/health)",
      "React + Vite cyberpunk dashboard & live sync",
      "Strict environment isolation & zero-credential hardcoding"
    ]
  },
  {
    id: "module-2",
    title: "Module 2: Secure Code Ingestion Layer",
    status: "ACTIVE",
    icon: FileCode2,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "Code submission & file upload APIs (POST /api/code/analyze, /upload)",
      "Path traversal defense & Windows device name sanitization",
      "Multi-language resolution (Python, Java, JS, TS)",
      "Strict file size (2 MB) & code length (500k char) validation",
      "Safe transient file storage with guaranteed auto-cleanup"
    ]
  },
  {
    id: "module-3",
    title: "Module 3: Secret Detection & Redaction Engine",
    status: "ACTIVE",
    icon: ShieldAlert,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "Multi-pass secret detection (AWS, OpenAI, GitHub, JWT, DB, Private Keys)",
      "Shannon entropy algorithm for high-entropy secret detection",
      "Deterministic in-place token replacement ([REDACTED_<TYPE>])",
      "Zero secret leakage guarantee across responses, logs, and database",
      "Security scanning API (POST /api/security/scan)"
    ]
  },
  {
    id: "module-4",
    title: "Module 4: Local Static Code Analysis Engine",
    status: "ACTIVE",
    icon: Code2,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "Python AST security visitor (eval, exec, compile, shell)",
      "Command & SQL injection heuristics detection",
      "Unsafe deserialization (pickle, marshal, PyYAML)",
      "Bandit SAST integration with normalized findings (LOW-CRITICAL)",
      "100% offline analysis & Rice's theorem limitation documentation"
    ]
  },
  {
    id: "module-5",
    title: "Module 5: ML Risk Scoring Engine",
    status: "ACTIVE",
    icon: BrainCircuit,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "16-dimensional numeric feature vector (findings, density, complexity, secrets)",
      "Deterministic rule-based baseline scoring engine",
      "Scikit-learn RandomForest regression pipeline on synthetic profiles",
      "Bounded 0-100 score & LOW/MEDIUM/HIGH/CRITICAL tiers",
      "Explainability engine detailing exact risk drivers (POST /api/risk/score)"
    ]
  },
  {
    id: "module-6",
    title: "Module 6: Privacy-Aware AI Analysis Layer",
    status: "ACTIVE",
    icon: Cpu,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "7-stage unidirectional privacy pipeline (Secret Redaction -> AST -> Minimized Context -> LLM)",
      "Context minimization window (±4 lines around findings with masked tokens)",
      "LLMProvider abstraction (MockLLMProvider, ExternalLLMProvider, LocalLLMProvider)",
      "Non-blocking graceful degradation (AI_DISABLED, DEGRADED_TIMEOUT, DEGRADED_RATE_LIMITED)",
      "Zero-code audit telemetry logger (POST /api/ai/analyze, GET /api/ai/audit)"
    ]
  },
  {
    id: "module-7",
    title: "Module 7: AI Developer Explanation & Remediation",
    status: "ACTIVE",
    icon: Sparkles,
    color: "#06b6d4",
    badgeClass: "badge-cyan",
    features: [
      "Tripartite Epistemic Segregation (DETECTED_FACT, AI_INTERPRETATION, RECOMMENDATION)",
      "Strict grounding in authoritative AST/Bandit static diagnostic facts",
      "Anti-hallucination barrier with automatic 'Insufficient evidence' fallback",
      "Actionable engineering refactoring steps & non-executable safe replacement code",
      "Explanation & Remediation API (POST /api/remediation/explain)"
    ]
  },
  {
    id: "module-8",
    title: "Module 8: Private AI / Local LLM Support",
    status: "ACTIVE",
    icon: Server,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "LocalLLMProvider abstraction supporting native Ollama & OpenAI-compatible servers",
      "Dual Mode Architecture: Mode 1 (Cloud TLS) & Mode 2 (Private Local / Air-Gapped)",
      "Guaranteed zero external network egress & air-gapped operation without API keys",
      "Live connectivity testing, model discovery & health probe endpoints (GET /api/ai/providers)",
      "Graceful offline fallback ensuring static analysis & risk scoring never fail"
    ]
  },
  {
    id: "module-9",
    title: "Module 9: Engineering Knowledge RAG",
    status: "ACTIVE",
    icon: BookOpen,
    color: "#06b6d4",
    badgeClass: "badge-cyan",
    features: [
      "Semantic vector embeddings over OWASP guidelines & historical post-mortems",
      "Strict knowledge boundary invariant (Zero proprietary code ingested into vector store)",
      "Anti-hallucination threshold filter (< 0.35 -> 'No relevant evidence found.')",
      "Explicit source attribution (Doc ID, section, relevance score) on all retrieved chunks",
      "RAG Query & Document Indexing APIs (POST /api/rag/query, POST /api/rag/documents)"
    ]
  },
  {
    id: "module-10",
    title: "Module 10: GitHub Pull Request Security Analysis",
    status: "ACTIVE",
    icon: GitPullRequest,
    color: "#10b981",
    badgeClass: "badge-emerald",
    features: [
      "Read-only GitHub REST API ingestion & unified diff patch parsing",
      "Zero repo code execution & zero arbitrary cloning/building",
      "Multi-file secret redaction, local AST/SAST analysis & composite risk scoring",
      "Tripartite AI remediation & RAG grounding on top PR findings",
      "Passive security audit report with strict in-memory token safety (POST /api/github/pr/analyze)"
    ]
  }
];

export default function ModuleRoadmap() {
  return (
    <section className="glass-panel" style={{ padding: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{
          padding: '8px',
          borderRadius: '8px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)'
        }}>
          <Compass size={20} color="#10b981" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>Project Engineering Roadmap</h2>
          <p style={{ fontSize: '0.8rem' }}>Step-by-step modular progression &bull; Modules 1 through 10 Active</p>
        </div>
      </div>


      {/* Grid of Roadmap Modules */}
      <div className="grid-3" style={{ gap: '16px' }}>
        {MODULES.map((module) => {
          const Icon = module.icon;
          const isActive = module.status === "ACTIVE";
          
          return (
            <div 
              key={module.id}
              style={{
                background: isActive ? 'rgba(16, 185, 129, 0.04)' : 'rgba(255, 255, 255, 0.02)',
                border: isActive ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '12px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                boxShadow: isActive ? '0 0 20px rgba(16, 185, 129, 0.1)' : 'none'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span className={`badge ${module.badgeClass}`} style={{ fontSize: '0.65rem' }}>
                    {module.status}
                  </span>
                  <Icon size={16} color={module.color} />
                </div>

                <h3 style={{ fontSize: '0.95rem', color: '#f8fafc', marginBottom: '10px' }}>
                  {module.title}
                </h3>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {module.features.map((feat, i) => (
                    <li key={i} style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                      <span style={{ color: module.color, fontSize: '0.9rem', lineHeight: '1' }}>&bull;</span>
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {isActive && (
                <div style={{
                  marginTop: '14px',
                  padding: '6px 10px',
                  background: 'rgba(16, 185, 129, 0.12)',
                  borderRadius: '6px',
                  fontSize: '0.7rem',
                  color: '#10b981',
                  textAlign: 'center',
                  fontWeight: 600
                }}>
                  ACTIVE &amp; DEPLOYED
                </div>
              )}
            </div>
          );
        })}
      </div>

    </section>
  );
}
