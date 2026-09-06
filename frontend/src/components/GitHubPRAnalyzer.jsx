import React, { useState } from 'react';
import {
  GitPullRequest,
  GitBranch,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  FileCode,
  Key,
  Cpu,
  BookOpen,
  Lock,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
  Sparkles,
  Search,
  Code2
} from 'lucide-react';
import { analyzeGitHubPR, parseGitHubPRUrl } from '../services/api';

const PRESET_PRS = [
  {
    label: 'High-Risk PR (SQLi + Secrets)',
    url: 'https://github.com/test-org/vulnerable-service/pull/101',
    description: 'Simulates a PR introducing unsanitized SQL string concatenation and exposed AWS keys.',
  },
  {
    label: 'Clean PR (Safe Refactor)',
    url: 'https://github.com/test-org/clean-service/pull/45',
    description: 'Simulates a clean refactoring with boundary validations and zero exposed secrets.',
  },
  {
    label: 'Project Repository PR',
    url: 'https://github.com/anusha975/AI-Powered-Code-Risk-Bug-Detection-Platform/pull/1',
    description: 'Target repository PR for automated privacy-preserving security analysis.',
  },
];

export default function GitHubPRAnalyzer() {
  const [prUrl, setPrUrl] = useState('https://github.com/test-org/vulnerable-service/pull/101');
  const [githubToken, setGithubToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [analysisMode, setAnalysisMode] = useState('REDACTED_HYBRID');
  const [enableRAG, setEnableRAG] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [expandedFiles, setExpandedFiles] = useState({});

  const toggleFile = (filename) => {
    setExpandedFiles((prev) => ({
      ...prev,
      [filename]: !prev[filename],
    }));
  };

  const handleRunAudit = async (customUrl) => {
    const targetUrl = customUrl || prUrl;
    if (!targetUrl.trim()) {
      setError('Please provide a valid GitHub Pull Request URL or repository shorthand.');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      pr_url: targetUrl.trim(),
      analysis_mode: analysisMode,
      enable_rag: enableRAG,
    };

    const res = await analyzeGitHubPR(payload, githubToken);
    setLoading(false);

    if (res.success && res.data) {
      setResult(res.data);
      // Auto-expand first file
      if (res.data.files && res.data.files.length > 0) {
        setExpandedFiles({ [res.data.files[0].filename]: true });
      }
    } else {
      setError(res.error || 'Failed to analyze GitHub Pull Request.');
      setResult(null);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'CRITICAL':
        return '#ef4444';
      case 'HIGH':
        return '#f97316';
      case 'MEDIUM':
        return '#eab308';
      case 'LOW':
      default:
        return '#22c55e';
    }
  };

  const getSeverityBadge = (severity) => {
    const sev = (severity || '').toUpperCase();
    switch (sev) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-red-950/80 text-red-400 border border-red-800">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-orange-950/80 text-orange-400 border border-orange-800">HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-yellow-950/80 text-yellow-400 border border-yellow-800">MEDIUM</span>;
      case 'LOW':
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">LOW</span>;
    }
  };

  return (
    <section className="card" style={{ marginBottom: '2rem' }}>
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-950/70 text-cyan-400 border border-cyan-800/60 shadow-lg shadow-cyan-950/30">
            <GitPullRequest className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                MODULE 10
              </span>
              <span className="badge badge-active">ACTIVE</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                PASSIVE NON-EXECUTING
              </span>
            </div>
            <h2 className="text-xl font-bold text-white mt-1">
              GitHub Pull Request Security & Risk Analysis
            </h2>
            <p className="text-sm text-gray-400">
              Audit changed code, diff patches, secrets, and SAST vulnerabilities on GitHub PRs without cloning or executing repository code.
            </p>
          </div>
        </div>

        {/* Security Invariants Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gray-900/80 border border-gray-800 text-xs text-gray-300">
            <Lock className="w-3.5 h-3.5 text-cyan-400" />
            <span>Zero Repo Egress</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gray-900/80 border border-gray-800 text-xs text-gray-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>In-Memory Token</span>
          </div>
        </div>
      </div>

      {/* PR Preset Selector */}
      <div className="mt-5">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-2">
          Demo PR Scenarios & Presets
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {PRESET_PRS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setPrUrl(preset.url);
                handleRunAudit(preset.url);
              }}
              className={`p-3 rounded-xl border text-left transition-all ${
                prUrl === preset.url
                  ? 'bg-cyan-950/40 border-cyan-600 shadow-md shadow-cyan-950/30 text-white'
                  : 'bg-gray-900/60 border-gray-800 hover:border-gray-700 text-gray-300 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-2 text-xs font-bold text-cyan-400 mb-1">
                <GitBranch className="w-3.5 h-3.5" />
                <span>{preset.label}</span>
              </div>
              <div className="text-xs text-gray-400 line-clamp-2">{preset.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* PR Input & Configuration Form */}
      <div className="mt-5 p-4 rounded-xl bg-gray-950/60 border border-gray-800 space-y-4">
        {/* URL Input */}
        <div>
          <label className="text-xs font-semibold text-gray-300 block mb-1.5">
            GitHub Pull Request URL or Shorthand
          </label>
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={prUrl}
                onChange={(e) => setPrUrl(e.target.value)}
                placeholder="https://github.com/owner/repo/pull/123 or owner/repo#123"
                className="w-full px-4 py-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white text-sm font-mono focus:border-cyan-500 focus:outline-none pr-10"
              />
              <GitPullRequest className="w-4 h-4 text-gray-500 absolute right-3 top-3" />
            </div>
            <button
              type="button"
              disabled={loading}
              onClick={() => handleRunAudit()}
              className="px-5 py-2.5 rounded-lg font-bold text-sm bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-950/40 flex items-center gap-2 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Auditing PR...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Audit Pull Request</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Optional GitHub Token & Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 border-t border-gray-800/80">
          {/* GitHub PAT (Optional) */}
          <div>
            <label className="text-xs font-semibold text-gray-400 block mb-1">
              GitHub Token (Optional for Private Repos)
            </label>
            <div className="relative">
              <input
                type={showToken ? 'text' : 'password'}
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                placeholder="ghp_****************"
                className="w-full px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-700 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none pr-8"
              />
              <button
                type="button"
                onClick={() => setShowToken(!showToken)}
                className="absolute right-2.5 top-2 text-gray-500 hover:text-gray-300"
              >
                {showToken ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              </button>
            </div>
            <p className="text-[10px] text-gray-500 mt-1">
              🔒 In-memory only. Never persisted to database or logs.
            </p>
          </div>

          {/* Analysis Mode */}
          <div>
            <label className="text-xs font-semibold text-gray-400 block mb-1">
              Analysis Mode
            </label>
            <select
              value={analysisMode}
              onChange={(e) => setAnalysisMode(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-700 text-white text-xs focus:border-cyan-500 focus:outline-none"
            >
              <option value="REDACTED_HYBRID">Redacted Hybrid (Static + Sanitized AI)</option>
              <option value="LOCAL_STATIC_ONLY">Local Static Only (0% AI / 100% Deterministic)</option>
              <option value="SELF_HOSTED_LLM">Private / Self-Hosted Local LLM</option>
            </select>
            <p className="text-[10px] text-gray-500 mt-1">
              Controls whether sanitized diff context reaches LLM remediation.
            </p>
          </div>

          {/* RAG Augmentation Toggle */}
          <div>
            <label className="text-xs font-semibold text-gray-400 block mb-1">
              Engineering Knowledge RAG
            </label>
            <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer pt-1">
              <input
                type="checkbox"
                checked={enableRAG}
                onChange={(e) => setEnableRAG(e.target.checked)}
                className="rounded bg-gray-900 border-gray-700 text-cyan-500 focus:ring-0"
              />
              <span className="flex items-center gap-1">
                <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                Ground findings with standards & post-mortems
              </span>
            </label>
            <p className="text-[10px] text-gray-500 mt-1">
              Cites curated OWASP standards & incident post-mortems.
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mt-4 p-4 rounded-xl bg-red-950/50 border border-red-800 text-red-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs">
            <span className="font-bold">Analysis Failed: </span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Results Workspace */}
      {result && (
        <div className="mt-6 space-y-6">
          {/* PR Metadata Banner & Risk Overview */}
          <div className="p-5 rounded-2xl bg-gray-900/90 border border-gray-800 shadow-xl grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* PR Overview Details */}
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  PR #{result.pr_number}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono">
                  {result.repository}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-800/40">
                  {result.state.toUpperCase()}
                </span>
              </div>

              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>{result.pr_title}</span>
                {result.pr_url && (
                  <a
                    href={result.pr_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-gray-500 hover:text-cyan-400 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </h3>

              <div className="flex items-center gap-4 text-xs text-gray-400 flex-wrap">
                <span>Author: <strong className="text-gray-200">@{result.pr_author}</strong></span>
                <span>Branch: <code className="text-cyan-300">{result.head_branch}</code> → <code className="text-gray-300">{result.base_branch}</code></span>
                <span className="text-emerald-400 font-mono">+{result.additions}</span>
                <span className="text-red-400 font-mono">-{result.deletions}</span>
                <span>Files: <strong className="text-gray-200">{result.changed_files_count}</strong> ({result.scanned_files_count} scanned)</span>
              </div>

              {/* Explainable Risk Reasons */}
              {result.risk_reasons && result.risk_reasons.length > 0 && (
                <div className="pt-2 border-t border-gray-800">
                  <div className="text-xs font-semibold text-gray-400 mb-1.5">Risk Attribution Reasons:</div>
                  <ul className="space-y-1">
                    {result.risk_reasons.map((reason, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-start gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-orange-400 flex-shrink-0 mt-0.5" />
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Overall Risk Score Meter */}
            <div className="p-4 rounded-xl bg-gray-950/80 border border-gray-800 flex flex-col items-center justify-center text-center">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Overall PR Risk Score
              </div>

              <div
                className="text-4xl font-extrabold font-mono tracking-tight"
                style={{ color: getRiskColor(result.overall_risk_level) }}
              >
                {result.overall_risk_score}
                <span className="text-base text-gray-500 font-normal"> / 100</span>
              </div>

              <div className="mt-2">{getSeverityBadge(result.overall_risk_level)}</div>

              <div className="text-[11px] text-gray-500 mt-3 flex items-center gap-2">
                <span>Scan Time: {result.scan_latency_ms}ms</span>
                <span>•</span>
                <span>Audit ID: {result.analysis_id.slice(0, 8)}</span>
              </div>
            </div>
          </div>

          {/* Severity Counters Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-red-950/30 border border-red-900/60 text-center">
              <div className="text-2xl font-bold font-mono text-red-400">{result.severity_breakdown.critical}</div>
              <div className="text-xs font-semibold text-red-300 mt-0.5">Critical Findings</div>
            </div>
            <div className="p-3.5 rounded-xl bg-orange-950/30 border border-orange-900/60 text-center">
              <div className="text-2xl font-bold font-mono text-orange-400">{result.severity_breakdown.high}</div>
              <div className="text-xs font-semibold text-orange-300 mt-0.5">High Findings</div>
            </div>
            <div className="p-3.5 rounded-xl bg-yellow-950/30 border border-yellow-900/60 text-center">
              <div className="text-2xl font-bold font-mono text-yellow-400">{result.severity_breakdown.medium}</div>
              <div className="text-xs font-semibold text-yellow-300 mt-0.5">Medium Findings</div>
            </div>
            <div className="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-900/60 text-center">
              <div className="text-2xl font-bold font-mono text-cyan-400">{result.secrets_detected_count}</div>
              <div className="text-xs font-semibold text-cyan-300 mt-0.5">Secrets Redacted</div>
            </div>
          </div>

          {/* Changed Files & Diagnostics Accordion */}
          <div>
            <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <FileCode className="w-4 h-4 text-cyan-400" />
              <span>Changed Files & Security Diagnostics ({result.files.length})</span>
            </h4>

            <div className="space-y-3">
              {result.files.map((file, idx) => (
                <div
                  key={idx}
                  className="rounded-xl border border-gray-800 bg-gray-900/60 overflow-hidden transition-all"
                >
                  {/* File Header Row */}
                  <div
                    onClick={() => toggleFile(file.filename)}
                    className="p-3.5 flex items-center justify-between cursor-pointer hover:bg-gray-800/50 select-none flex-wrap gap-2"
                  >
                    <div className="flex items-center gap-2.5">
                      <FileCode className="w-4 h-4 text-gray-400" />
                      <span className="font-mono text-xs font-bold text-gray-200">{file.filename}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 uppercase">
                        {file.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-emerald-400">+{file.additions}</span>
                      <span className="text-xs font-mono text-red-400">-{file.deletions}</span>

                      {file.is_scanned ? (
                        <>
                          <span
                            className="text-xs font-mono font-bold px-2 py-0.5 rounded"
                            style={{
                              backgroundColor: `${getRiskColor(file.file_risk_level)}20`,
                              color: getRiskColor(file.file_risk_level),
                            }}
                          >
                            Risk: {file.file_risk_score}
                          </span>
                          {file.secrets_count > 0 && (
                            <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                              🔑 {file.secrets_count} Secret(s)
                            </span>
                          )}
                          {file.findings_count > 0 && (
                            <span className="text-xs px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 font-mono">
                              ⚠️ {file.findings_count} Issue(s)
                            </span>
                          )}
                        </>
                      ) : (
                        <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-500 font-mono">
                          SKIPPED (NON-CODE)
                        </span>
                      )}

                      {expandedFiles[file.filename] ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded File Details */}
                  {expandedFiles[file.filename] && (
                    <div className="p-4 border-t border-gray-800 bg-gray-950/70 space-y-4">
                      {/* Findings List */}
                      {file.findings && file.findings.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-gray-400 mb-2">Detected Findings:</div>
                          <div className="space-y-2">
                            {file.findings.map((f, fIdx) => (
                              <div
                                key={fIdx}
                                className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs space-y-1.5"
                              >
                                <div className="flex items-center justify-between gap-2 flex-wrap">
                                  <div className="flex items-center gap-2">
                                    {getSeverityBadge(f.severity)}
                                    <span className="font-mono text-cyan-400 font-bold">{f.issue_id}</span>
                                    <span className="text-gray-200 font-semibold">{f.title}</span>
                                  </div>
                                  <span className="text-gray-500 font-mono">
                                    Line {f.line_number || 'N/A'} • Analyzer: {f.analyzer}
                                  </span>
                                </div>
                                <div className="p-2 rounded bg-black/60 font-mono text-gray-300 text-[11px] overflow-x-auto whitespace-pre">
                                  {f.code_snippet}
                                </div>
                                <div className="text-gray-400 text-[11px]">
                                  💡 <strong>Guidance:</strong> {f.recommendation}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Redacted Secrets List */}
                      {file.secrets && file.secrets.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-cyan-400 mb-2 flex items-center gap-1.5">
                            <Key className="w-3.5 h-3.5" />
                            <span>Redacted Credentials ({file.secrets.length}):</span>
                          </div>
                          <div className="space-y-1.5">
                            {file.secrets.map((sec, sIdx) => (
                              <div
                                key={sIdx}
                                className="p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-800/40 text-xs flex items-center justify-between"
                              >
                                <div className="flex items-center gap-2">
                                  <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono text-[10px] font-bold">
                                    {sec.secret_type}
                                  </span>
                                  <span className="text-gray-300 font-mono text-[11px]">{sec.placeholder}</span>
                                </div>
                                <span className="text-gray-500 font-mono text-[10px]">
                                  Line {sec.line_number} • Confidence: {sec.confidence}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Patch Preview */}
                      {file.patch_snippet && (
                        <div>
                          <div className="text-xs font-semibold text-gray-400 mb-1.5">Diff Patch Preview:</div>
                          <pre className="p-3 rounded-lg bg-black/80 font-mono text-[11px] text-gray-300 overflow-x-auto whitespace-pre border border-gray-800">
                            {file.patch_snippet}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Tripartite AI Remediations */}
          {result.remediations && result.remediations.length > 0 && (
            <div className="p-5 rounded-2xl bg-gradient-to-b from-blue-950/20 to-gray-900 border border-blue-900/40">
              <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span>AI Developer Remediation Plans ({result.remediations.length})</span>
              </h4>

              <div className="space-y-4">
                {result.remediations.map((rem, rIdx) => (
                  <div
                    key={rIdx}
                    className="p-4 rounded-xl bg-gray-950/80 border border-gray-800 space-y-3"
                  >
                    {/* Header */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        {getSeverityBadge(rem.detected_fact.severity)}
                        <span className="font-mono text-cyan-400 font-bold">{rem.detected_fact.issue_id}</span>
                        <span className="text-white font-semibold text-xs">{rem.detected_fact.finding_title}</span>
                      </div>
                      <span className="text-gray-500 font-mono text-xs">
                        {rem.detected_fact.file}:{rem.detected_fact.line_number}
                      </span>
                    </div>

                    {/* Tripartite Breakdown Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {/* Interpretation */}
                      <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs">
                        <div className="font-semibold text-cyan-400 mb-1">🤖 AI Interpretation & Impact:</div>
                        <p className="text-gray-300 leading-relaxed text-[11px]">{rem.ai_interpretation.explanation}</p>
                        <p className="text-orange-400/90 mt-1.5 text-[11px]">
                          <strong>Risk:</strong> {rem.ai_interpretation.potential_impact}
                        </p>
                      </div>

                      {/* Recommendation */}
                      <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 text-xs">
                        <div className="font-semibold text-emerald-400 mb-1">🛡️ Recommended Remediation:</div>
                        <p className="text-gray-300 leading-relaxed text-[11px]">{rem.remediation_recommendation.step_by_step_guidance}</p>
                        <p className="text-gray-400 mt-1.5 text-[11px]">
                          <strong>Rationale:</strong> {rem.remediation_recommendation.why_it_matters}
                        </p>
                      </div>
                    </div>

                    {/* Safe Replacement Code */}
                    {rem.remediation_recommendation.safe_code_replacement && (
                      <div>
                        <div className="text-[11px] font-semibold text-emerald-400 mb-1 flex items-center gap-1.5">
                          <Code2 className="w-3.5 h-3.5" />
                          <span>Verified Safer Code Replacement:</span>
                        </div>
                        <pre className="p-3 rounded-lg bg-black/90 font-mono text-[11px] text-emerald-300 overflow-x-auto whitespace-pre border border-emerald-950">
                          {rem.remediation_recommendation.safe_code_replacement}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Supporting Engineering Knowledge (RAG) */}
          {result.supporting_documents && result.supporting_documents.length > 0 && (
            <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800">
              <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-cyan-400" />
                <span>Supporting Engineering Standards & Post-Mortems (RAG)</span>
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.supporting_documents.map((doc, dIdx) => (
                  <div
                    key={dIdx}
                    className="p-3.5 rounded-xl bg-gray-950/80 border border-gray-800 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-cyan-400 font-bold text-[11px]">{doc.doc_id}</span>
                      <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono text-[10px]">
                        Match: {Math.round(doc.relevance_score * 100)}%
                      </span>
                    </div>
                    <div className="font-semibold text-gray-200">{doc.title}</div>
                    <div className="text-gray-400 text-[11px] line-clamp-2">{doc.snippet}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Compliance Guarantee Banner */}
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/40 text-emerald-300 flex items-center gap-3 text-xs">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <div>
              <div className="font-bold">{result.privacy_guarantee}</div>
              <div className="text-emerald-400/80 text-[11px] mt-0.5">{result.security_notice}</div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
