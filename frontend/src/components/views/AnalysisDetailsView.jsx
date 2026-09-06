import React, { useState, useEffect } from 'react';
import {
  FileCode,
  ArrowLeft,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Key,
  Sparkles,
  BookOpen,
  Code2,
  Clock,
  CheckCircle2,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { fetchAnalysisDetail, fetchAnalysisHistory } from '../../services/api';

export default function AnalysisDetailsView({ analysisId, onNavigate }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDetail = async (id) => {
    setLoading(true);
    setError(null);

    let targetId = id;
    if (!targetId) {
      // Fetch latest history session as fallback
      const histRes = await fetchAnalysisHistory({ limit: 1 });
      if (histRes.success && histRes.data && histRes.data.length > 0) {
        targetId = histRes.data[0].analysis_id;
      }
    }

    if (!targetId) {
      setLoading(false);
      setError('No analysis session selected.');
      return;
    }

    const res = await fetchAnalysisDetail(targetId);
    setLoading(false);
    if (res.success && res.data) {
      setDetail(res.data);
    } else {
      setError(res.error || 'Failed to load analysis details.');
    }
  };

  useEffect(() => {
    loadDetail(analysisId);
  }, [analysisId]);

  const getRiskColor = (score) => {
    if (score >= 80) return '#ef4444';
    if (score >= 60) return '#f97316';
    if (score >= 30) return '#eab308';
    return '#22c55e';
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
    <div className="space-y-6">
      {/* Navigation Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => onNavigate('overview')}
            className="p-2 rounded-xl bg-gray-900 border border-gray-800 text-gray-400 hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                AUDIT SESSION
              </span>
              <span className="text-xs text-gray-500 font-mono">ID: {detail?.analysis_id || analysisId || '--'}</span>
            </div>
            <h2 className="text-xl font-bold text-white mt-1">
              {detail?.target_name || 'Analysis Session Diagnostics'}
            </h2>
          </div>
        </div>

        <button
          type="button"
          onClick={() => loadDetail(analysisId)}
          disabled={loading}
          className="btn btn-outline btn-sm flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Reload Details</span>
        </button>
      </div>

      {loading ? (
        <div className="p-12 rounded-2xl bg-gray-900/60 border border-gray-800 text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
          <p className="text-xs text-gray-400">Loading comprehensive session diagnostics...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-red-950/40 border border-red-800 text-red-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <div>
            <div className="font-bold">Inspection Error:</div>
            <div className="text-red-400/80">{error}</div>
          </div>
        </div>
      ) : detail ? (
        <div className="space-y-6">
          {/* Executive Overview & Risk Score Banner */}
          <div className="p-5 rounded-2xl bg-gray-900/90 border border-gray-800 shadow-xl grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-xs">
                  {detail.analysis_type}
                </span>
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono text-xs border border-cyan-800">
                  AI MODE: {detail.ai_mode}
                </span>
                <span className="text-xs text-gray-500 font-mono">
                  {new Date(detail.timestamp).toLocaleString()}
                </span>
              </div>

              <div className="text-xs text-gray-400 space-y-1">
                <div>Language: <strong className="text-gray-200 uppercase">{detail.language || 'Python'}</strong></div>
                <div>Scan Latency: <strong className="text-gray-200">{detail.scan_latency_ms}ms</strong></div>
              </div>

              {/* Risk Reasons */}
              {detail.risk_reasons && detail.risk_reasons.length > 0 && (
                <div className="pt-2 border-t border-gray-800 space-y-1">
                  <div className="text-xs font-semibold text-gray-400">Risk Attribution Drivers:</div>
                  <ul className="space-y-1">
                    {detail.risk_reasons.map((reason, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-start gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-orange-400 flex-shrink-0 mt-0.5" />
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Risk Gauge */}
            <div className="p-4 rounded-xl bg-gray-950/80 border border-gray-800 flex flex-col items-center justify-center text-center">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Session Risk Score
              </div>
              <div
                className="text-4xl font-extrabold font-mono tracking-tight"
                style={{ color: getRiskColor(detail.risk_score) }}
              >
                {detail.risk_score}
                <span className="text-base text-gray-500 font-normal"> / 100</span>
              </div>
              <div className="mt-2">{getSeverityBadge(detail.risk_level)}</div>
              <div className="text-[11px] text-gray-500 mt-2">
                {detail.findings.length} findings • {detail.secrets.length} secrets redacted
              </div>
            </div>
          </div>

          {/* Sanitized Source Code / Diff Preview */}
          {detail.sanitized_content && (
            <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-cyan-400" />
                  <span>Sanitized Source Content / Diff</span>
                </h4>
                <span className="text-[11px] text-cyan-400 font-mono">🔒 In-Place Redacted</span>
              </div>
              <pre className="p-3.5 rounded-xl bg-black/90 font-mono text-xs text-gray-200 overflow-x-auto whitespace-pre border border-gray-800">
                {detail.sanitized_content}
              </pre>
            </div>
          )}

          {/* Line-Mapped Findings List */}
          <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800 space-y-4">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              <span>Diagnostic Findings ({detail.findings.length})</span>
            </h4>

            {detail.findings.length > 0 ? (
              <div className="space-y-3">
                {detail.findings.map((f, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-gray-950/80 border border-gray-800 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        {getSeverityBadge(f.severity)}
                        <span className="font-mono text-cyan-400 font-bold">{f.issue_id}</span>
                        <span className="text-gray-100 font-bold">{f.title}</span>
                      </div>
                      <span className="text-gray-500 font-mono">
                        Line {f.line_number || 'N/A'} • Analyzer: {f.analyzer}
                      </span>
                    </div>

                    {f.code_snippet && (
                      <pre className="p-2.5 rounded bg-black/60 font-mono text-[11px] text-gray-300 overflow-x-auto whitespace-pre border border-gray-800/80">
                        {f.code_snippet}
                      </pre>
                    )}

                    <div className="text-gray-300 text-[11px]">
                      💡 <strong>Recommendation:</strong> {f.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-gray-950/50 text-center text-xs text-gray-500">
                Zero security vulnerabilities detected in this scan session.
              </div>
            )}
          </div>

          {/* Redacted Secrets Summary */}
          {detail.secrets.length > 0 && (
            <div className="p-5 rounded-2xl bg-cyan-950/20 border border-cyan-900/50 space-y-3">
              <h4 className="text-sm font-bold text-cyan-300 flex items-center gap-2">
                <Key className="w-4 h-4 text-cyan-400" />
                <span>Intercepted & Redacted Credentials ({detail.secrets.length})</span>
              </h4>
              <p className="text-[11px] text-gray-400">
                The actual credential values were wiped in memory and never persisted or transmitted.
              </p>

              <div className="space-y-2">
                {detail.secrets.map((sec, sIdx) => (
                  <div
                    key={sIdx}
                    className="p-3 rounded-lg bg-gray-950 border border-cyan-900/40 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono font-bold text-[10px]">
                        {sec.secret_type}
                      </span>
                      <span className="font-mono text-gray-300 text-[11px]">{sec.placeholder}</span>
                    </div>
                    <span className="text-gray-500 font-mono text-[10px]">
                      Line {sec.line_number} • Confidence: {sec.confidence}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tripartite AI Remediations */}
          {detail.remediations && detail.remediations.length > 0 && (
            <div className="p-5 rounded-2xl bg-gradient-to-b from-blue-950/20 to-gray-900 border border-blue-900/40 space-y-4">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span>AI Developer Remediation Plans ({detail.remediations.length})</span>
              </h4>

              <div className="space-y-4">
                {detail.remediations.map((rem, rIdx) => (
                  <div
                    key={rIdx}
                    className="p-4 rounded-xl bg-gray-950/80 border border-gray-800 space-y-3 text-xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {getSeverityBadge(rem.detected_fact.severity)}
                        <span className="font-mono text-cyan-400 font-bold">{rem.detected_fact.issue_id}</span>
                        <span className="text-white font-bold">{rem.detected_fact.finding_title}</span>
                      </div>
                      <span className="text-gray-500 font-mono">
                        Line {rem.detected_fact.line_number}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 space-y-1">
                        <div className="font-semibold text-cyan-400">🤖 AI Interpretation:</div>
                        <p className="text-gray-300 leading-relaxed text-[11px]">{rem.ai_interpretation.explanation}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 space-y-1">
                        <div className="font-semibold text-emerald-400">🛡️ Recommended Fix:</div>
                        <p className="text-gray-300 leading-relaxed text-[11px]">{rem.remediation_recommendation.step_by_step_guidance}</p>
                      </div>
                    </div>

                    {rem.remediation_recommendation.safe_code_replacement && (
                      <div>
                        <div className="text-[11px] font-semibold text-emerald-400 mb-1 flex items-center gap-1.5">
                          <Code2 className="w-3.5 h-3.5" />
                          <span>Verified Safe Code Replacement:</span>
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

          {/* Supporting RAG Knowledge Documents */}
          {detail.supporting_documents && detail.supporting_documents.length > 0 && (
            <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800 space-y-3">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-cyan-400" />
                <span>Supporting Engineering Standards & Post-Mortems (RAG)</span>
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {detail.supporting_documents.map((doc, dIdx) => (
                  <div
                    key={dIdx}
                    className="p-3.5 rounded-xl bg-gray-950/80 border border-gray-800 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-cyan-400 font-bold">{doc.doc_id}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300">
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

          {/* Compliance Banner */}
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/40 text-emerald-300 flex items-center gap-3 text-xs">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <div className="font-bold">{detail.privacy_guarantee}</div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
