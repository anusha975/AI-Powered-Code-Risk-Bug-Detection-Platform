import React, { useState } from 'react';
import {
  Wrench,
  ShieldCheck,
  Cpu,
  Layers,
  Sparkles,
  Terminal,
  Activity,
  Sliders,
  AlertTriangle,
  CheckCircle2,
  Copy,
  Check,
  FileCode,
  HelpCircle,
  Zap,
  Info,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { generateDeveloperRemediation } from '../services/api';

const REMEDIATION_PRESETS = [
  {
    name: 'Critical RCE (eval)',
    filename: 'payment_eval.py',
    language: 'python',
    code: `def calculate_fee(user_expression):
    # DANGEROUS: Evaluates raw mathematical string from client
    fee = eval(user_expression)
    return {"calculated_fee": fee}
`
  },
  {
    name: 'Command Injection',
    filename: 'net_diag.py',
    language: 'python',
    code: `import os

def trace_route(server_ip):
    # DANGEROUS: Direct shell concatenation
    cmd = "traceroute -m 5 " + server_ip
    return os.system(cmd)
`
  },
  {
    name: 'SQL Injection in Query',
    filename: 'db_query.py',
    language: 'python',
    code: `import sqlite3

def find_account(account_id):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    # DANGEROUS: Raw string formatting in SQL
    sql = "SELECT balance FROM accounts WHERE id = '%s'" % account_id
    cursor.execute(sql)
    return cursor.fetchone()
`
  },
  {
    name: 'Ambiguous Low-Confidence Flaw',
    filename: 'ambiguous_flow.py',
    language: 'python',
    code: `def process_generic_buffer(buf):
    # Low confidence pattern: broad exception without clear input source
    try:
        data = buf.read()
    except Exception:
        pass
    return data
`
  },
  {
    name: 'Clean Verified Function',
    filename: 'clean_math.py',
    language: 'python',
    code: `def calculate_circle_area(radius: float) -> float:
    """Calculate circle area with strict positive radius validation."""
    if radius < 0:
        raise ValueError("Radius must be non-negative")
    return 3.1415926535 * (radius ** 2)
`
  }
];

export default function DeveloperRemediationCard() {
  const [code, setCode] = useState(REMEDIATION_PRESETS[0].code);
  const [filename, setFilename] = useState(REMEDIATION_PRESETS[0].filename);
  const [language, setLanguage] = useState(REMEDIATION_PRESETS[0].language);
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const handleSelectPreset = (idx) => {
    setSelectedPreset(idx);
    setCode(REMEDIATION_PRESETS[idx].code);
    setFilename(REMEDIATION_PRESETS[idx].filename);
    setLanguage(REMEDIATION_PRESETS[idx].language);
    setResult(null);
    setError(null);
  };

  const handleRunRemediation = async () => {
    if (!code.trim()) {
      setError('Please provide source code to explain.');
      return;
    }

    setLoading(true);
    setError(null);

    const res = await generateDeveloperRemediation({
      content: code,
      filename: filename || 'snippet.py',
      language: language || 'python',
      max_explanations: 3
    });

    setLoading(false);

    if (res.success) {
      setResult(res.data);
    } else {
      setError(res.error || 'Failed to generate developer remediation.');
    }
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="card glass-effect relative overflow-hidden border border-slate-700/60 p-6 md:p-8 space-y-6">
      {/* Background ambient gradient */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-emerald-600/20 border border-cyan-500/30 text-cyan-400 shadow-inner">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-slate-100">
                AI Developer Explanation & Remediation Engine
              </h2>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Module 7 (Active)
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Tripartite Epistemic Segregation: <span className="text-cyan-400 font-semibold">DETECTED FACT</span> &bull; <span className="text-purple-400 font-semibold">AI INTERPRETATION</span> &bull; <span className="text-emerald-400 font-semibold">RECOMMENDATION</span>
            </p>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleRunRemediation}
          disabled={loading}
          className="btn-primary flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-semibold shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {loading ? (
            <>
              <Activity className="w-4 h-4 animate-spin" />
              <span>Generating Tripartite Remediation...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate Developer Remediation</span>
            </>
          )}
        </button>
      </div>

      {/* Preset Selector */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          <span>Select Code Scenario</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {REMEDIATION_PRESETS.map((preset, idx) => (
            <button
              key={preset.name}
              onClick={() => handleSelectPreset(idx)}
              className={`p-2.5 rounded-xl text-left text-xs transition-all border ${
                selectedPreset === idx
                  ? 'bg-cyan-950/40 border-cyan-500/50 text-cyan-200 shadow-sm shadow-cyan-500/10'
                  : 'bg-slate-900/50 border-slate-800/80 text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
              }`}
            >
              <div className="font-semibold text-slate-200 truncate">{preset.name}</div>
              <div className="text-[10px] text-slate-400 mt-0.5 font-mono truncate">{preset.filename}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Code Input */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span className="flex items-center gap-1.5 font-mono">
            <Terminal className="w-3.5 h-3.5 text-slate-500" />
            {filename}
          </span>
          <span>{code.split('\n').length} lines</span>
        </div>
        <div className="relative rounded-xl overflow-hidden border border-slate-700/80 bg-slate-950/80 font-mono text-sm shadow-inner">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={7}
            className="w-full p-4 bg-transparent text-slate-200 resize-y focus:outline-none focus:ring-1 focus:ring-cyan-500/50 leading-relaxed text-xs"
            placeholder="Paste code snippet to generate developer explanation and safer replacement..."
            spellCheck="false"
          />
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Remediation Error</div>
            <div className="text-xs text-red-400/90 mt-0.5">{error}</div>
          </div>
        </div>
      )}

      {/* Results Area */}
      {result && (
        <div className="space-y-6 pt-2 animate-fadeIn">
          {/* Header Summary Banner */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  {result.remediations.length} REMEDIATION PLAN(S)
                </span>
                <span className="text-xs text-slate-400 font-mono">Risk Score: {result.risk_score}/100 ({result.risk_level})</span>
              </div>
              <p className="text-xs text-slate-300 pt-1">
                {result.summary_message}
              </p>
            </div>

            <div className="text-[11px] text-slate-500 max-w-sm font-sans bg-slate-950/40 p-3 rounded-xl border border-slate-800/60">
              <span className="font-semibold text-slate-400">Anti-Hallucination Barrier: </span>
              {result.epistemic_notice}
            </div>
          </div>

          {/* Tripartite Remediation Cards */}
          {result.remediations?.length > 0 ? (
            <div className="space-y-6">
              {result.remediations.map((rem, idx) => (
                <div
                  key={idx}
                  className="rounded-2xl border border-slate-800/80 bg-slate-950/50 overflow-hidden shadow-xl space-y-0"
                >
                  {/* Card Main Bar */}
                  <div className="p-4 bg-slate-900/80 border-b border-slate-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                        rem.fact.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                        rem.fact.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                        'bg-amber-500/20 text-amber-400 border-amber-500/30'
                      }`}>
                        {rem.fact.severity}
                      </span>
                      <h3 className="font-bold text-slate-200 text-sm">{rem.fact.title}</h3>
                    </div>
                    <span className="text-xs text-slate-500 font-mono">ID: {rem.finding_id}</span>
                  </div>

                  {/* 3 Epistemic Tiers Grid */}
                  <div className="p-5 space-y-5">
                    {/* TIER 1: DETECTED FACT */}
                    <div className="rounded-xl border border-cyan-900/40 bg-cyan-950/10 p-4 space-y-2.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
                          <Terminal className="w-4 h-4 text-cyan-400" />
                          <span>1. Detected Fact (Static Analysis Ground Truth)</span>
                        </div>
                        <span className="text-[11px] font-mono text-cyan-300/80">
                          Analyzer: {rem.fact.analyzer} &bull; Line {rem.fact.line_number} (Conf: {(rem.fact.detection_confidence * 100).toFixed(0)}%)
                        </span>
                      </div>

                      <div className="p-2.5 rounded-lg bg-slate-950/80 border border-cyan-900/30 font-mono text-xs text-slate-300">
                        <div className="text-[10px] text-slate-500 pb-1 border-b border-slate-800 mb-1">
                          Flagged Code Snippet:
                        </div>
                        <pre className="overflow-x-auto text-[11px] text-cyan-200/90 whitespace-pre">
                          {rem.fact.code_snippet}
                        </pre>
                      </div>
                    </div>

                    {/* TIER 2: AI INTERPRETATION */}
                    <div className="rounded-xl border border-purple-900/40 bg-purple-950/10 p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-purple-400">
                          <BrainCircuit className="w-4 h-4 text-purple-400" />
                          <span>2. AI Interpretation (Contextual Reasoning)</span>
                        </div>
                        {rem.interpretation.is_insufficient_evidence ? (
                          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-semibold border border-amber-500/30">
                            Insufficient Evidence Fallback
                          </span>
                        ) : (
                          <span className="text-[11px] font-mono text-purple-300/80">
                            Model: {rem.model_used}
                          </span>
                        )}
                      </div>

                      {/* Developer Explanation */}
                      <div className="space-y-1">
                        <div className="text-[11px] font-semibold text-slate-400">Developer Explanation:</div>
                        <p className="text-xs text-slate-200 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-purple-900/30">
                          {rem.interpretation.developer_explanation}
                        </p>
                      </div>

                      {/* Why It Matters & Impact Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-xs">
                        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1">
                          <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5">
                            <Info className="w-3.5 h-3.5 text-purple-400" />
                            <span>Why This Code Pattern Matters:</span>
                          </div>
                          <p className="text-[11px] text-slate-300 leading-relaxed">
                            {rem.interpretation.why_it_matters}
                          </p>
                        </div>

                        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1">
                          <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5">
                            <Zap className="w-3.5 h-3.5 text-rose-400" />
                            <span>Potential Impact if Exploited:</span>
                          </div>
                          <p className="text-[11px] text-slate-300 leading-relaxed">
                            {rem.interpretation.potential_impact}
                          </p>
                        </div>
                      </div>

                      {/* Confidence / Uncertainty Statement */}
                      <div className="p-2.5 rounded-lg bg-purple-950/30 border border-purple-900/30 text-[11px] text-purple-300/90 flex items-center gap-2">
                        <HelpCircle className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                        <span>{rem.interpretation.confidence_statement}</span>
                      </div>
                    </div>

                    {/* TIER 3: RECOMMENDATION & SAFER CODE */}
                    <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/10 p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
                          <ShieldCheck className="w-4 h-4 text-emerald-400" />
                          <span>3. Recommendation (Actionable Engineering Guidance)</span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono">Non-Executable Advice</span>
                      </div>

                      {/* Recommended Strategy */}
                      <p className="text-xs text-slate-200 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-emerald-900/30">
                        {rem.recommendation.recommended_remediation}
                      </p>

                      {/* Action Steps */}
                      {rem.recommendation.remediation_steps?.length > 0 && (
                        <div className="space-y-1.5 text-xs">
                          <div className="text-[11px] font-semibold text-slate-400">Step-by-Step Refactoring:</div>
                          <div className="space-y-1">
                            {rem.recommendation.remediation_steps.map((step, sIdx) => (
                              <div key={sIdx} className="flex items-start gap-2 text-[11px] text-slate-300">
                                <ArrowRight className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                                <span>{step}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Safer Code Replacement Snippet */}
                      {rem.recommendation.safer_code_example && (
                        <div className="space-y-1.5 pt-1">
                          <div className="flex items-center justify-between text-xs font-semibold text-emerald-300">
                            <span>Safer Code Implementation:</span>
                            <button
                              onClick={() => handleCopy(rem.recommendation.safer_code_example, rem.finding_id)}
                              className="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 font-mono cursor-pointer"
                            >
                              {copiedId === rem.finding_id ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                  <span className="text-emerald-400">Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5" />
                                  <span>Copy Safe Code</span>
                                </>
                              )}
                            </button>
                          </div>
                          <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-900/50 font-mono text-xs text-emerald-300 overflow-x-auto">
                            <pre className="whitespace-pre leading-relaxed">{rem.recommendation.safer_code_example}</pre>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-900/30 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Zero issues detected. No developer remediation required for this code submission.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
