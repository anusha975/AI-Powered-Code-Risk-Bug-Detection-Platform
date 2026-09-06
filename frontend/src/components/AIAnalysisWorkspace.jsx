import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  ShieldCheck,
  Cpu,
  Lock,
  EyeOff,
  Sparkles,
  Terminal,
  Activity,
  Sliders,
  AlertTriangle,
  CheckCircle2,
  Copy,
  Check,
  Layers,
  History,
  Info,
  ChevronRight,
  Flame,
  ShieldAlert,
  Power
} from 'lucide-react';
import { runAIAnalysis, fetchAIAuditLogs } from '../services/api';

const AI_PRESETS = [
  {
    name: 'Critical RCE & Secret Token',
    filename: 'auth_handler.py',
    language: 'python',
    code: `import os

AWS_ACCESS_KEY = "AKIA1234567890EXAMPLE"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def execute_untrusted_task(payload_str):
    # DANGEROUS: Arbitrary dynamic execution
    result = eval(payload_str)
    return {"status": "SUCCESS", "result": result}
`
  },
  {
    name: 'Command Injection Flaw',
    filename: 'system_diag.py',
    language: 'python',
    code: `import os

def ping_host(target_host):
    # DANGEROUS: Unsanitized shell execution
    command = f"ping -c 1 {target_host}"
    return os.system(command)
`
  },
  {
    name: 'SQL Injection Flaw',
    filename: 'user_repository.py',
    language: 'python',
    code: `import sqlite3

def query_user_profile(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # DANGEROUS: Raw string formatting in query
    query = "SELECT id, username, email FROM users WHERE id = '%s'" % user_id
    cursor.execute(query)
    return cursor.fetchone()
`
  },
  {
    name: 'Pristine Clean Code',
    filename: 'math_helper.py',
    language: 'python',
    code: `def calculate_hypotenuse(a: float, b: float) -> float:
    """Calculate the hypotenuse using Pythagorean theorem safely."""
    return (a ** 2 + b ** 2) ** 0.5
`
  }
];

export default function AIAnalysisWorkspace() {
  const [code, setCode] = useState(AI_PRESETS[0].code);
  const [filename, setFilename] = useState(AI_PRESETS[0].filename);
  const [language, setLanguage] = useState(AI_PRESETS[0].language);
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [aiEnabled, setAiEnabled] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copiedCodeId, setCopiedCodeId] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [showAuditLogs, setShowAuditLogs] = useState(false);

  const handleSelectPreset = (idx) => {
    setSelectedPreset(idx);
    setCode(AI_PRESETS[idx].code);
    setFilename(AI_PRESETS[idx].filename);
    setLanguage(AI_PRESETS[idx].language);
    setResult(null);
    setError(null);
  };

  const handleRunAnalysis = async () => {
    if (!code.trim()) {
      setError('Please provide source code to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    const res = await runAIAnalysis({
      content: code,
      filename: filename || 'snippet.py',
      language: language || 'python',
      ai_enabled: aiEnabled
    });

    setLoading(false);

    if (res.success) {
      setResult(res.data);
      // Refresh audit logs
      loadAuditLogs();
    } else {
      setError(res.error || 'Failed to execute privacy-preserving AI analysis.');
    }
  };

  const loadAuditLogs = async () => {
    const res = await fetchAIAuditLogs(10);
    if (res.success && res.data) {
      setAuditLogs(res.data);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedCodeId(id);
    setTimeout(() => setCopiedCodeId(null), 2000);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'AI_DISABLED':
        return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
      case 'SKIPPED_CLEAN':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'DEGRADED_TIMEOUT':
      case 'DEGRADED_RATE_LIMITED':
      case 'DEGRADED_ERROR':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      default:
        return 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30';
    }
  };

  return (
    <div className="card glass-effect relative overflow-hidden border border-slate-700/60 p-6 md:p-8 space-y-6">
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500/20 to-indigo-600/20 border border-purple-500/30 text-purple-400 shadow-inner">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-slate-100">
                Privacy-Aware AI Analysis & Remediation
              </h2>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Module 6 (Active)
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Strict 7-stage privacy pipeline: Secret Redaction &rarr; AST/SAST &rarr; Context Minimization (&plusmn;4 lines) &rarr; LLM Provider
            </p>
          </div>
        </div>

        {/* Controls: AI Toggle & Action Button */}
        <div className="flex items-center gap-3">
          {/* AI Enabled Toggle */}
          <button
            onClick={() => setAiEnabled(!aiEnabled)}
            className={`px-3 py-2 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-all cursor-pointer ${
              aiEnabled
                ? 'bg-indigo-950/40 border-indigo-500/40 text-indigo-300 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 text-slate-400'
            }`}
            title="Toggle AI assistance (demonstrates graceful fallback)"
          >
            <Power className={`w-3.5 h-3.5 ${aiEnabled ? 'text-indigo-400' : 'text-slate-500'}`} />
            <span>AI: {aiEnabled ? 'ENABLED' : 'DISABLED'}</span>
          </button>

          {/* Trigger Button */}
          <button
            onClick={handleRunAnalysis}
            disabled={loading}
            className="btn-primary flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-semibold shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? (
              <>
                <Activity className="w-4 h-4 animate-spin" />
                <span>Running Privacy AI Pipeline...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Run Privacy-Aware AI Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Preset Selector */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-purple-400" />
          <span>Interactive Vulnerability Scenarios</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {AI_PRESETS.map((preset, idx) => (
            <button
              key={preset.name}
              onClick={() => handleSelectPreset(idx)}
              className={`p-3 rounded-xl text-left text-xs transition-all border ${
                selectedPreset === idx
                  ? 'bg-purple-950/40 border-purple-500/50 text-purple-200 shadow-sm shadow-purple-500/10'
                  : 'bg-slate-900/50 border-slate-800/80 text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
              }`}
            >
              <div className="font-semibold text-slate-200 truncate">{preset.name}</div>
              <div className="text-[11px] text-slate-400 mt-1 font-mono">{preset.filename}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Code Editor */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span className="flex items-center gap-1.5 font-mono">
            <Terminal className="w-3.5 h-3.5 text-slate-500" />
            {filename}
          </span>
          <span>{code.split('\n').length} lines &bull; {code.length} chars</span>
        </div>
        <div className="relative rounded-xl overflow-hidden border border-slate-700/80 bg-slate-950/80 font-mono text-sm shadow-inner">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={8}
            className="w-full p-4 bg-transparent text-slate-200 resize-y focus:outline-none focus:ring-1 focus:ring-purple-500/50 leading-relaxed text-xs"
            placeholder="Paste code to analyze with privacy guarantees..."
            spellCheck="false"
          />
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Analysis Error</div>
            <div className="text-xs text-red-400/90 mt-0.5">{error}</div>
          </div>
        </div>
      )}

      {/* Results Area */}
      {result && (
        <div className="space-y-6 pt-2 animate-fadeIn">
          {/* Status & Privacy Invariant Banner */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusBadge(result.ai_status)}`}>
                  AI STATUS: {result.ai_status}
                </span>
                <span className="text-xs text-slate-400 font-mono">ID: {result.analysis_id.slice(0, 8)}...</span>
              </div>
              <div className="text-xs text-slate-400 flex items-center gap-2 pt-1">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{result.privacy_guarantee}</span>
              </div>
            </div>

            {/* Diagnostic Metrics Pills */}
            <div className="flex items-center gap-2 text-xs font-mono shrink-0">
              <div className="px-3 py-2 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                <div className="text-[10px] text-slate-500 uppercase">Redacted Secrets</div>
                <div className={`font-bold text-sm ${result.secrets_detected_count > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {result.secrets_detected_count}
                </div>
              </div>
              <div className="px-3 py-2 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                <div className="text-[10px] text-slate-500 uppercase">Static Issues</div>
                <div className="font-bold text-sm text-indigo-300">{result.total_findings_count}</div>
              </div>
              <div className="px-3 py-2 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                <div className="text-[10px] text-slate-500 uppercase">Risk Score</div>
                <div className="font-bold text-sm text-purple-300">{result.risk_score}/100</div>
              </div>
            </div>
          </div>

          {/* Privacy Context Transparency Inspector: Full File vs Minimized Context */}
          {result.minimized_contexts?.length > 0 && (
            <div className="p-5 rounded-2xl bg-indigo-950/20 border border-indigo-900/40 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-semibold text-indigo-200">
                  <EyeOff className="w-4 h-4 text-indigo-400" />
                  <span>Privacy Context Transparency: Minimal AI Ingress Payload</span>
                </div>
                <span className="text-[11px] text-slate-400 font-mono">
                  Full Code ({code.length} chars) &rarr; Minimized Payload ({result.minimized_contexts.reduce((acc, c) => acc + c.char_count, 0)} chars)
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Below is the exact isolated snippet window (&plusmn;4 lines) exposed to the AI model. Notice that all raw secrets have been masked as <code>[REDACTED_...]</code> and unreferenced lines were excluded.
              </p>

              <div className="space-y-2 pt-1">
                {result.minimized_contexts.map((ctx, i) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-950/90 border border-indigo-900/30 font-mono text-xs text-slate-300">
                    <div className="flex items-center justify-between text-[11px] text-slate-500 border-b border-slate-800 pb-1.5 mb-2">
                      <span className="text-indigo-300 font-semibold">{ctx.finding_id} &bull; {ctx.issue_title}</span>
                      <span>Lines {ctx.start_line}-{ctx.end_line} ({ctx.char_count} chars)</span>
                    </div>
                    <pre className="overflow-x-auto text-[11px] text-slate-300 whitespace-pre leading-relaxed">
                      {ctx.context_snippet}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Remediation Explanations */}
          {result.ai_explanations?.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span>AI-Assisted Root Cause & Remediation Guidance</span>
              </h3>

              <div className="space-y-4">
                {result.ai_explanations.map((exp, idx) => (
                  <div key={idx} className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
                    {/* Finding Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                          exp.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                          exp.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                          'bg-amber-500/20 text-amber-400 border-amber-500/30'
                        }`}>
                          {exp.severity}
                        </span>
                        <h4 className="font-bold text-slate-200 text-sm">{exp.issue_title}</h4>
                        <span className="text-xs text-slate-500 font-mono">(Line {exp.line_number})</span>
                      </div>

                      <div className="text-[11px] text-slate-400 font-mono flex items-center gap-1.5">
                        <Cpu className="w-3.5 h-3.5 text-purple-400" />
                        <span>{exp.provider_used} ({exp.model_name})</span>
                      </div>
                    </div>

                    {/* Root Cause Diagnosis */}
                    <div className="space-y-1.5">
                      <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Vulnerability Root Cause Analysis
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60">
                        {exp.root_cause_explanation}
                      </p>
                    </div>

                    {/* Actionable Remediation */}
                    <div className="space-y-1.5">
                      <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                        Recommended Remediation Strategy
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3.5 rounded-xl border border-indigo-900/30">
                        {exp.remediation_advice}
                      </p>
                    </div>

                    {/* Secure Code Replacement */}
                    {exp.secure_code_example && (
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-emerald-400">
                          <span>Secure Implementation Replacement</span>
                          <button
                            onClick={() => handleCopy(exp.secure_code_example, exp.finding_id)}
                            className="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 normal-case font-mono cursor-pointer"
                          >
                            {copiedCodeId === exp.finding_id ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-400" />
                                <span className="text-emerald-400">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>Copy Secure Code</span>
                              </>
                            )}
                          </button>
                        </div>
                        <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-900/40 font-mono text-xs text-emerald-300/90 overflow-x-auto">
                          <pre className="whitespace-pre leading-relaxed">{exp.secure_code_example}</pre>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-900/30 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
              <Info className="w-4 h-4 text-slate-500" />
              <span>
                {result.ai_status === 'SKIPPED_CLEAN' ? 'Zero vulnerabilities detected. AI remediation skipped for clean code.' :
                 result.ai_status === 'AI_DISABLED' ? 'AI analysis was bypassed per user preference (AI_ENABLED=false). Complete static findings returned.' :
                 'No AI explanations were generated for this submission.'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Privacy Audit Log Telemetry Drawer */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/30">
        <button
          onClick={() => setShowAuditLogs(!showAuditLogs)}
          className="w-full p-4 text-xs font-semibold text-slate-300 flex items-center justify-between hover:bg-slate-900/50 transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-purple-400" />
            <span>Privacy Audit Telemetry Log ({auditLogs.length} recent events)</span>
          </div>
          <span className="text-[11px] text-slate-500">
            {showAuditLogs ? 'Hide Audit Log' : 'Inspect Audit Log (Zero Code Retention)'}
          </span>
        </button>

        {showAuditLogs && (
          <div className="p-4 border-t border-slate-800/80 bg-slate-950/70 space-y-2 font-mono text-xs">
            <div className="text-[11px] text-slate-500 mb-2 font-sans">
              <span className="font-semibold text-slate-400">Privacy Compliance Note: </span>
              Audit records persist strictly operational metadata (timestamps, model IDs, finding counts, character lengths). Source code and raw prompt payloads are permanently discarded.
            </div>

            {auditLogs.length > 0 ? (
              <div className="space-y-1.5 max-h-60 overflow-y-auto">
                {auditLogs.map((log) => (
                  <div key={log.event_id} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60 flex items-center justify-between text-[11px]">
                    <div className="flex items-center gap-2">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${getStatusBadge(log.status)}`}>
                        {log.status}
                      </span>
                      <span className="text-slate-300">{log.provider}</span>
                    </div>
                    <div className="flex items-center gap-3 text-slate-400">
                      <span>{log.findings_count} findings ({log.payload_chars} chars)</span>
                      <span className="text-purple-300 font-bold">{log.latency_ms}ms</span>
                      <span className="text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-slate-500 text-center py-4">No audit events recorded yet.</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
