import React, { useState } from 'react';
import {
  TrendingUp,
  Cpu,
  BrainCircuit,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  Flame,
  Activity,
  Layers,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp,
  Sliders,
  Terminal,
  Zap
} from 'lucide-react';
import { calculateRiskScore } from '../services/api';

const RISK_PRESETS = [
  {
    name: 'Pristine Clean Code',
    language: 'python',
    filename: 'math_utils.py',
    expectedRisk: 'LOW',
    code: `def calculate_average(values: list[float]) -> float:
    """Calculate the arithmetic mean of a numbers list safely."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def normalize_scores(scores: list[float]) -> list[float]:
    """Normalize score values between 0.0 and 1.0."""
    if not scores:
        return []
    max_val = max(scores)
    min_val = min(scores)
    if max_val == min_val:
        return [1.0 for _ in scores]
    return [(s - min_val) / (max_val - min_val) for s in scores]
`
  },
  {
    name: 'High Complexity & Error Smells',
    language: 'python',
    filename: 'order_processor.py',
    expectedRisk: 'MEDIUM',
    code: `def process_order(order_data, flags):
    # Deep nesting and unhandled exception flaws
    status = "INIT"
    if order_data:
        if "items" in order_data:
            for item in order_data["items"]:
                if item.get("valid"):
                    if item.get("in_stock"):
                        if flags.get("allow_discount"):
                            try:
                                apply_discount(item)
                            except:
                                pass  # Silent swallow
    return status
`
  },
  {
    name: 'SQL & Command Injections',
    language: 'python',
    filename: 'admin_exec.py',
    expectedRisk: 'HIGH',
    code: `import os
import sqlite3

def run_diagnostics(user_cmd, table_name):
    # Command injection vulnerability
    os.system(f"ping -c 1 {user_cmd}")
    
    # SQL injection vulnerability
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE role = '%s'" % table_name
    cursor.execute(query)
    return cursor.fetchall()
`
  },
  {
    name: 'Critical RCE & Exposed Secrets',
    language: 'python',
    filename: 'payment_gateway.py',
    expectedRisk: 'CRITICAL',
    code: `import os
import pickle

AWS_SECRET_KEY = "AKIA1234567890EXAMPLE"
STRIPE_API_KEY = "sk_test_51MockDemoKey00000000000000"

def handle_webhook(payload, raw_bytes):
    # Critical dynamic evaluation and unpickling
    eval(payload.get("expression"))
    data = pickle.loads(raw_bytes)
    return data
`
  }
];

export default function RiskScoringDashboard() {
  const [code, setCode] = useState(RISK_PRESETS[0].code);
  const [filename, setFilename] = useState(RISK_PRESETS[0].filename);
  const [language, setLanguage] = useState(RISK_PRESETS[0].language);
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showFeatures, setShowFeatures] = useState(false);

  const handleSelectPreset = (idx) => {
    setSelectedPreset(idx);
    setCode(RISK_PRESETS[idx].code);
    setFilename(RISK_PRESETS[idx].filename);
    setLanguage(RISK_PRESETS[idx].language);
    setResult(null);
    setError(null);
  };

  const handleCalculateScore = async () => {
    if (!code.trim()) {
      setError('Please provide source code to calculate risk score.');
      return;
    }

    setLoading(true);
    setError(null);

    const res = await calculateRiskScore({
      content: code,
      filename: filename || 'snippet.py',
      language: language || 'python'
    });

    setLoading(false);

    if (res.success) {
      setResult(res.data);
    } else {
      setError(res.error || 'Failed to compute code risk score.');
    }
  };

  // Helper for risk colors
  const getRiskTheme = (level, score) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return {
          badge: 'bg-red-500/20 text-red-400 border-red-500/40',
          gradient: 'from-red-600 via-rose-500 to-amber-500',
          gaugeText: 'text-red-400',
          bg: 'bg-red-950/20 border-red-900/30',
          bar: 'bg-gradient-to-r from-red-600 to-rose-500',
          icon: Flame
        };
      case 'HIGH':
        return {
          badge: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
          gradient: 'from-orange-500 via-amber-500 to-yellow-500',
          gaugeText: 'text-orange-400',
          bg: 'bg-orange-950/20 border-orange-900/30',
          bar: 'bg-gradient-to-r from-orange-500 to-amber-500',
          icon: ShieldAlert
        };
      case 'MEDIUM':
        return {
          badge: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
          gradient: 'from-amber-500 via-yellow-400 to-lime-400',
          gaugeText: 'text-amber-400',
          bg: 'bg-amber-950/20 border-amber-900/30',
          bar: 'bg-gradient-to-r from-amber-500 to-yellow-400',
          icon: AlertTriangle
        };
      case 'LOW':
      default:
        return {
          badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
          gradient: 'from-emerald-500 via-teal-400 to-cyan-400',
          gaugeText: 'text-emerald-400',
          bg: 'bg-emerald-950/20 border-emerald-900/30',
          bar: 'bg-gradient-to-r from-emerald-500 to-teal-400',
          icon: CheckCircle2
        };
    }
  };

  const currentTheme = getRiskTheme(result?.risk_level, result?.risk_score);
  const StatusIcon = currentTheme.icon;

  return (
    <div className="card glass-effect relative overflow-hidden border border-slate-700/60 p-6 md:p-8 space-y-6">
      {/* Background ambient lighting */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-600/20 border border-indigo-500/30 text-indigo-400 shadow-inner">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-slate-100">
                Code Risk Scoring & Explainability Engine
              </h2>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Module 5 (Active)
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Hybrid scoring fusing local AST/Bandit metrics with a 16-feature Scikit-learn RandomForest pipeline
            </p>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleCalculateScore}
          disabled={loading}
          className="btn-primary flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-semibold shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {loading ? (
            <>
              <Activity className="w-4 h-4 animate-spin" />
              <span>Calculating Model Inferences...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Calculate Risk Score</span>
            </>
          )}
        </button>
      </div>

      {/* Demo Profile Selector */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-indigo-400" />
          <span>Interactive Risk Presets</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {RISK_PRESETS.map((preset, idx) => (
            <button
              key={preset.name}
              onClick={() => handleSelectPreset(idx)}
              className={`p-3 rounded-xl text-left text-xs transition-all border ${
                selectedPreset === idx
                  ? 'bg-indigo-950/40 border-indigo-500/50 text-indigo-200 shadow-sm shadow-indigo-500/10'
                  : 'bg-slate-900/50 border-slate-800/80 text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
              }`}
            >
              <div className="font-semibold text-slate-200 truncate">{preset.name}</div>
              <div className="text-[11px] mt-1 flex items-center justify-between text-slate-400">
                <span>{preset.filename}</span>
                <span className={`px-1.5 py-0.2 rounded font-mono text-[10px] ${
                  preset.expectedRisk === 'CRITICAL' ? 'text-red-400 bg-red-950/40' :
                  preset.expectedRisk === 'HIGH' ? 'text-orange-400 bg-orange-950/40' :
                  preset.expectedRisk === 'MEDIUM' ? 'text-amber-400 bg-amber-950/40' :
                  'text-emerald-400 bg-emerald-950/40'
                }`}>
                  {preset.expectedRisk}
                </span>
              </div>
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
          <span>{code.split('\n').length} lines</span>
        </div>
        <div className="relative rounded-xl overflow-hidden border border-slate-700/80 bg-slate-950/80 font-mono text-sm shadow-inner">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={8}
            className="w-full p-4 bg-transparent text-slate-200 resize-y focus:outline-none focus:ring-1 focus:ring-indigo-500/50 leading-relaxed text-xs"
            placeholder="Paste code snippet to evaluate risk..."
            spellCheck="false"
          />
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">Calculation Error</div>
            <div className="text-xs text-red-400/90 mt-0.5">{error}</div>
          </div>
        </div>
      )}

      {/* Risk Results Area */}
      {result && (
        <div className="space-y-6 pt-2 animate-fadeIn">
          {/* Main Score Display Banner */}
          <div className={`p-6 rounded-2xl border ${currentTheme.bg} flex flex-col md:flex-row items-center justify-between gap-6`}>
            {/* Left Gauge & Tier */}
            <div className="flex items-center gap-6">
              {/* Circular Gauge Visual */}
              <div className="relative w-28 h-28 flex items-center justify-center shrink-0">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    className="text-slate-800/80 stroke-current"
                    strokeWidth="8"
                    fill="transparent"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    className={`${currentTheme.gaugeText} stroke-current transition-all duration-1000 ease-out`}
                    strokeWidth="8"
                    strokeDasharray={2 * Math.PI * 40}
                    strokeDashoffset={(2 * Math.PI * 40) * (1 - result.risk_score / 100)}
                    strokeLinecap="round"
                    fill="transparent"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center text-center">
                  <span className="text-2xl font-black text-slate-100 font-mono tracking-tight">
                    {result.risk_score}
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                    / 100
                  </span>
                </div>
              </div>

              {/* Tier Details */}
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${currentTheme.badge}`}>
                    <StatusIcon className="w-3.5 h-3.5" />
                    {result.risk_level} RISK
                  </span>
                  <span className="text-xs text-slate-400">
                    Calculated for <code className="text-slate-300 font-mono">{result.filename}</code>
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-100">
                  {result.risk_score >= 80 ? 'Critical Security Hazards Detected' :
                   result.risk_score >= 55 ? 'High Risk Vulnerabilities Present' :
                   result.risk_score >= 25 ? 'Moderate Complexity & Code Smells' :
                   'Clean & Resilient Code Profile'}
                </h3>
                <p className="text-xs text-slate-400 max-w-lg">
                  {result.risk_score >= 80 ? 'Code contains high-impact execution or credential exposure risks requiring immediate remediation.' :
                   result.risk_score >= 55 ? 'Severe vulnerabilities detected that could be exploited without proper sanitization.' :
                   result.risk_score >= 25 ? 'Code exhibits elevated structural branching, nested blocks, or unhandled exceptions.' :
                   'AST visitors and Bandit analyzers identified zero critical vulnerabilities or credential leaks.'}
                </p>
              </div>
            </div>

            {/* Quick Diagnostic Pills */}
            <div className="grid grid-cols-2 gap-3 w-full md:w-auto shrink-0 font-mono text-xs">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div className="text-[10px] uppercase tracking-wider text-slate-400">AST Findings</div>
                <div className="text-base font-bold text-indigo-300 mt-0.5">
                  {result.breakdown.total_findings_count}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div className="text-[10px] uppercase tracking-wider text-slate-400">Secrets Found</div>
                <div className={`text-base font-bold mt-0.5 ${result.breakdown.secrets_detected_count > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {result.breakdown.secrets_detected_count}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div className="text-[10px] uppercase tracking-wider text-slate-400">Cyclomatic</div>
                <div className="text-base font-bold text-slate-200 mt-0.5">
                  {result.breakdown.cyclomatic_complexity}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
                <div className="text-[10px] uppercase tracking-wider text-slate-400">Nesting Depth</div>
                <div className="text-base font-bold text-slate-200 mt-0.5">
                  {result.breakdown.max_nesting_depth}
                </div>
              </div>
            </div>
          </div>

          {/* Explainability Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Why was this score assigned? */}
            <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800 space-y-3">
              <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                <span>Explainability: Key Risk Drivers</span>
              </h4>
              <div className="space-y-2">
                {result.reasons?.map((reason, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60 text-xs text-slate-300 flex items-start gap-2.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0 mt-1.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Model Breakdown & Weights */}
            <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800 space-y-4">
              <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-purple-400" />
                <span>Hybrid Scoring Telemetry</span>
              </h4>

              {/* Sub-Scores Comparison */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                  <div className="text-slate-400 text-[11px]">Deterministic Baseline</div>
                  <div className="text-lg font-mono font-bold text-slate-200 mt-0.5">
                    {result.breakdown.deterministic_score} <span className="text-xs text-slate-500">/100</span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Weight: 60%</div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                  <div className="text-slate-400 text-[11px]">Scikit-Learn ML Model</div>
                  <div className="text-lg font-mono font-bold text-purple-300 mt-0.5">
                    {result.breakdown.ml_predicted_score} <span className="text-xs text-slate-500">/100</span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Weight: 40%</div>
                </div>
              </div>

              {/* Feature Contributions Progress Bar */}
              {result.breakdown.feature_contributions && Object.keys(result.breakdown.feature_contributions).length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs text-slate-400 font-medium">Estimated Risk Factors Contribution</div>
                  <div className="space-y-1.5 text-[11px]">
                    {Object.entries(result.breakdown.feature_contributions).map(([feat, pct]) => (
                      <div key={feat} className="space-y-0.5">
                        <div className="flex justify-between text-slate-400">
                          <span className="capitalize">{feat.replace('_', ' ')}</span>
                          <span className="font-mono text-slate-300">{pct}%</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-700"
                            style={{ width: `${Math.min(100, pct)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 16-Feature Vector Accordion */}
          <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/30">
            <button
              onClick={() => setShowFeatures(!showFeatures)}
              className="w-full p-4 text-xs font-semibold text-slate-300 flex items-center justify-between hover:bg-slate-900/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                <span>Inspect 16-Dimensional ML Feature Vector</span>
              </div>
              {showFeatures ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
            </button>

            {showFeatures && (
              <div className="p-4 border-t border-slate-800/80 bg-slate-950/70 grid grid-cols-2 md:grid-cols-4 gap-2.5 text-xs font-mono">
                {Object.entries(result.breakdown.feature_metrics || {}).map(([key, val]) => (
                  <div key={key} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
                    <div className="text-[10px] text-slate-400 truncate" title={key}>{key}</div>
                    <div className="text-slate-200 font-bold mt-0.5">{val}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Scientific Methodology Disclaimer */}
          <div className="p-3.5 rounded-xl bg-slate-900/30 border border-slate-800/60 text-[11px] text-slate-500 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-400">Scientific Methodology: </span>
              {result.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
