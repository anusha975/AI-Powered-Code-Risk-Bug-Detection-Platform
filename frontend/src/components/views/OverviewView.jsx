import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  AlertTriangle,
  FileCode,
  GitPullRequest,
  Lock,
  ArrowUpRight,
  RefreshCw,
  Clock,
  Key,
  Flame,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import { fetchDashboardOverview } from '../../services/api';

export default function OverviewView({ onNavigate, onSelectAnalysis }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadMetrics = async () => {
    setLoading(true);
    setError(null);
    const res = await fetchDashboardOverview();
    setLoading(false);
    if (res.success && res.data) {
      setMetrics(res.data);
    } else {
      setError(res.error || 'Failed to load telemetry metrics.');
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

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
      {/* Prominent Privacy Indicator Banner */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-cyan-950/40 to-blue-950/40 border border-emerald-800/60 shadow-lg flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-950 text-emerald-400 border border-emerald-700 shadow-md">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                AI MODE: {metrics?.active_ai_mode || 'Private/Local LLM'}
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800">
                100% Zero-Egress Guarded
              </span>
            </div>
            <p className="text-sm font-semibold text-gray-200 mt-1">
              {metrics?.privacy_assurance || 'Secrets detected and redacted before AI analysis.'}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={loadMetrics}
          disabled={loading}
          className="btn btn-outline btn-sm flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Top KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* KPI 1: Analyses Performed */}
        <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 font-semibold">
            <span>Analyses Performed</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono text-white mt-3">
            {loading ? '--' : metrics?.total_analyses_performed ?? 0}
          </div>
          <div className="text-[11px] text-gray-500 mt-2">Code snippets & PR audits</div>
        </div>

        {/* KPI 2: High-Risk Analyses */}
        <div className="p-4 rounded-xl bg-orange-950/20 border border-orange-900/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-orange-300 font-semibold">
            <span>High-Risk Analyses</span>
            <Flame className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono text-orange-400 mt-3">
            {loading ? '--' : metrics?.high_risk_analyses_count ?? 0}
          </div>
          <div className="text-[11px] text-orange-400/70 mt-2">Score ≥ 60.0 or High/Critical</div>
        </div>

        {/* KPI 3: Critical Findings */}
        <div className="p-4 rounded-xl bg-red-950/20 border border-red-900/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-red-300 font-semibold">
            <span>Critical Findings</span>
            <ShieldAlert className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono text-red-400 mt-3">
            {loading ? '--' : metrics?.critical_findings_count ?? 0}
          </div>
          <div className="text-[11px] text-red-400/70 mt-2">Immediate remediation needed</div>
        </div>

        {/* KPI 4: Average Risk Score */}
        <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 font-semibold">
            <span>Average Risk Score</span>
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
          </div>
          <div
            className="text-3xl font-extrabold font-mono mt-3"
            style={{ color: getRiskColor(metrics?.average_risk_score || 0) }}
          >
            {loading ? '--' : metrics?.average_risk_score ?? 0}
            <span className="text-xs text-gray-500 font-normal"> / 100</span>
          </div>
          <div className="text-[11px] text-gray-500 mt-2">Across all recorded scans</div>
        </div>

        {/* KPI 5: Secrets Redacted */}
        <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-900/50 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-cyan-300 font-semibold">
            <span>Secrets Redacted</span>
            <Key className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono text-cyan-400 mt-3">
            {loading ? '--' : metrics?.secrets_redacted_count ?? 0}
          </div>
          <div className="text-[11px] text-cyan-400/70 mt-2">0 bytes exposed to external LLMs</div>
        </div>
      </div>

      {/* Severity & Category Distribution Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              <span>Severity Breakdown</span>
            </h3>
            <span className="text-xs text-gray-500">Live static findings</span>
          </div>

          <div className="space-y-3">
            {['critical', 'high', 'medium', 'low'].map((sev) => {
              const count = metrics?.severity_distribution?.[sev] || 0;
              const total = Object.values(metrics?.severity_distribution || {}).reduce((a, b) => a + b, 0) || 1;
              const pct = Math.round((count / total) * 100);
              const color = sev === 'critical' ? '#ef4444' : sev === 'high' ? '#f97316' : sev === 'medium' ? '#eab308' : '#22c55e';

              return (
                <div key={sev} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold uppercase text-gray-300">{sev}</span>
                    <span className="font-mono text-gray-400">{count} issues ({pct}%)</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-gray-800 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${pct}%`, backgroundColor: color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Quick Launch & Category Overview */}
        <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span>Quick Actions & Workspaces</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => onNavigate('analyze-code')}
              className="p-3.5 rounded-xl bg-gray-950/80 border border-gray-800 hover:border-cyan-500 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between text-cyan-400 mb-1">
                <div className="flex items-center gap-2 text-xs font-bold">
                  <FileCode className="w-4 h-4" />
                  <span>Analyze Source Code</span>
                </div>
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400">Paste or upload code for local AST, SAST & secret analysis.</p>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('pr-analysis')}
              className="p-3.5 rounded-xl bg-gray-950/80 border border-gray-800 hover:border-cyan-500 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between text-cyan-400 mb-1">
                <div className="flex items-center gap-2 text-xs font-bold">
                  <GitPullRequest className="w-4 h-4" />
                  <span>Audit Pull Request</span>
                </div>
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400">Scan GitHub PR diff patches with zero repository code execution.</p>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('findings')}
              className="p-3.5 rounded-xl bg-gray-950/80 border border-gray-800 hover:border-cyan-500 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between text-cyan-400 mb-1">
                <div className="flex items-center gap-2 text-xs font-bold">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Findings Catalog</span>
                </div>
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400">Explore unified vulnerability catalog with instant search.</p>
            </button>

            <button
              type="button"
              onClick={() => onNavigate('knowledge-base')}
              className="p-3.5 rounded-xl bg-gray-950/80 border border-gray-800 hover:border-cyan-500 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between text-cyan-400 mb-1">
                <div className="flex items-center gap-2 text-xs font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Knowledge RAG</span>
                </div>
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-gray-400">Search curated OWASP standards & incident post-mortems.</p>
            </button>
          </div>
        </div>
      </div>

      {/* Recent Analyses Live Feed */}
      <div className="p-5 rounded-2xl bg-gray-900/80 border border-gray-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Recent Analysis Sessions</span>
          </h3>
          <button
            type="button"
            onClick={() => onNavigate('history')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
          >
            <span>View Full History</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {metrics?.recent_analyses && metrics.recent_analyses.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 font-semibold uppercase text-[10px]">
                  <th className="py-2.5 px-3">Target Name</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Risk Score</th>
                  <th className="py-2.5 px-3">Findings</th>
                  <th className="py-2.5 px-3">Secrets</th>
                  <th className="py-2.5 px-3">AI Mode</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {metrics.recent_analyses.map((session) => (
                  <tr
                    key={session.analysis_id}
                    className="hover:bg-gray-800/40 transition-colors"
                  >
                    <td className="py-3 px-3 font-mono font-bold text-gray-200">
                      {session.target_name}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[10px]">
                        {session.analysis_type}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className="font-mono font-bold px-2 py-0.5 rounded text-[11px]"
                        style={{
                          backgroundColor: `${getRiskColor(session.risk_score)}20`,
                          color: getRiskColor(session.risk_score),
                        }}
                      >
                        {session.risk_score} ({session.risk_level})
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-gray-300">
                      {session.findings_count}
                    </td>
                    <td className="py-3 px-3 font-mono text-cyan-400">
                      {session.secrets_count > 0 ? `🔑 ${session.secrets_count}` : '0'}
                    </td>
                    <td className="py-3 px-3 text-gray-400 text-[11px]">
                      {session.ai_mode}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        type="button"
                        onClick={() => {
                          if (onSelectAnalysis) onSelectAnalysis(session.analysis_id);
                          onNavigate('analysis-details');
                        }}
                        className="px-2.5 py-1 rounded bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 font-semibold text-[11px] transition-all cursor-pointer"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-gray-950/60 border border-gray-800 text-center text-xs text-gray-400">
            No analysis sessions recorded yet. Run a code scan or PR audit to generate telemetry.
          </div>
        )}
      </div>
    </div>
  );
}
