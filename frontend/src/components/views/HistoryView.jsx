import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  RefreshCw,
  Eye,
  GitPullRequest,
  FileCode,
  ShieldAlert,
  ShieldCheck,
  Lock,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  Clock
} from 'lucide-react';
import { fetchAnalysisHistory } from '../../services/api';

export default function HistoryView({ onSelectAnalysis }) {
  const [history, setHistory] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [scanType, setScanType] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    const params = {
      page,
      page_size: pageSize
    };
    if (scanType) params.scan_type = scanType;
    if (riskLevel) params.risk_level = riskLevel;

    const res = await fetchAnalysisHistory(params);
    setLoading(false);
    if (res.success && res.data) {
      setHistory(res.data.records || []);
      setTotalCount(res.data.total_count || 0);
    } else {
      setError(res.error || 'Failed to fetch analysis audit history.');
    }
  };

  useEffect(() => {
    loadHistory();
  }, [page, pageSize, scanType, riskLevel]);

  // Filter client-side by search query if present
  const filteredHistory = history.filter((item) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (item.analysis_id && item.analysis_id.toLowerCase().includes(q)) ||
      (item.target_name && item.target_name.toLowerCase().includes(q)) ||
      (item.summary && item.summary.toLowerCase().includes(q)) ||
      (item.ai_mode && item.ai_mode.toLowerCase().includes(q))
    );
  });

  const getRiskBadge = (level, score) => {
    const l = (level || '').toUpperCase();
    let bg = 'bg-emerald-950/80 text-emerald-400 border-emerald-800';
    if (l === 'CRITICAL') bg = 'bg-red-950/80 text-red-400 border-red-800';
    else if (l === 'HIGH') bg = 'bg-orange-950/80 text-orange-400 border-orange-800';
    else if (l === 'MEDIUM') bg = 'bg-yellow-950/80 text-yellow-400 border-yellow-800';

    return (
      <span className={`px-2.5 py-1 rounded-md text-xs font-bold font-mono border ${bg} flex items-center gap-1.5 w-fit`}>
        <span>{l || 'LOW'}</span>
        <span className="opacity-70">({score})</span>
      </span>
    );
  };

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  return (
    <div className="space-y-6">
      {/* Header & Controls Bar */}
      <div className="p-6 rounded-2xl bg-gray-900/90 border border-gray-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-purple-950/80 text-purple-400 border border-purple-800 shadow-md">
              <History className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                Analysis Audit History
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-800">
                  {totalCount} Total Sessions
                </span>
              </h2>
              <p className="text-sm text-gray-400">
                Immutable zero-leak audit records of all code submissions and pull request scans.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={loadHistory}
            disabled={loading}
            className="btn btn-outline btn-sm flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Records</span>
          </button>
        </div>

        {/* Filter Toolbar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2 border-t border-gray-800">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-gray-500" />
            <input
              type="text"
              placeholder="Search ID, target, summary..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-gray-950 border border-gray-800 rounded-lg text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Scan Type Filter */}
          <select
            value={scanType}
            onChange={(e) => {
              setScanType(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 bg-gray-950 border border-gray-800 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-purple-500"
          >
            <option value="">All Scan Types</option>
            <option value="CODE_SNIPPET">Code Snippet Ingestion</option>
            <option value="GITHUB_PR">GitHub Pull Request</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskLevel}
            onChange={(e) => {
              setRiskLevel(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 bg-gray-950 border border-gray-800 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-purple-500"
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>

          {/* Page Size */}
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="px-3 py-2 bg-gray-950 border border-gray-800 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-purple-500"
          >
            <option value="5">5 per page</option>
            <option value="10">10 per page</option>
            <option value="25">25 per page</option>
            <option value="50">50 per page</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-2xl bg-gray-900/90 border border-gray-800 shadow-xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-400 flex flex-col items-center gap-3">
            <RefreshCw className="w-8 h-8 animate-spin text-purple-400" />
            <p className="text-sm">Querying audit session store...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-400">
            <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-red-500" />
            <p className="font-semibold">{error}</p>
            <button
              onClick={loadHistory}
              className="mt-3 px-4 py-1.5 bg-red-950/60 border border-red-800 rounded-lg text-xs font-semibold text-red-300 hover:bg-red-900/60"
            >
              Retry
            </button>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="p-12 text-center text-gray-500 space-y-2">
            <History className="w-10 h-10 mx-auto opacity-40" />
            <p className="font-semibold text-gray-300">No analysis sessions found.</p>
            <p className="text-xs">Adjust your search or filter parameters to view historical records.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-gray-950/80 border-b border-gray-800 text-xs font-bold text-gray-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Analysis Session</th>
                  <th className="py-3 px-4">Target / Scope</th>
                  <th className="py-3 px-4">Scan Type</th>
                  <th className="py-3 px-4">Risk Evaluation</th>
                  <th className="py-3 px-4 text-center">Findings</th>
                  <th className="py-3 px-4 text-center">Secrets Redacted</th>
                  <th className="py-3 px-4">AI Mode</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-sans">
                {filteredHistory.map((row) => (
                  <tr key={row.analysis_id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-mono text-xs font-bold text-purple-300 flex items-center gap-1.5">
                        {row.analysis_id}
                      </div>
                      <div className="text-[11px] text-gray-500 flex items-center gap-1 mt-0.5">
                        <Clock className="w-3 h-3" />
                        {new Date(row.timestamp).toLocaleString()}
                      </div>
                    </td>

                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="font-semibold text-gray-200 truncate" title={row.target_name}>
                        {row.target_name || 'Code Analysis Task'}
                      </div>
                      {row.summary && (
                        <div className="text-xs text-gray-500 truncate" title={row.summary}>
                          {row.summary}
                        </div>
                      )}
                    </td>

                    <td className="py-3.5 px-4">
                      {row.scan_type === 'GITHUB_PR' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-950/80 text-blue-400 border border-blue-800">
                          <GitPullRequest className="w-3.5 h-3.5" />
                          GitHub PR
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
                          <FileCode className="w-3.5 h-3.5" />
                          Code Snippet
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4">
                      {getRiskBadge(row.risk_level, row.risk_score)}
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <span className="font-mono font-bold text-gray-200">
                        {row.findings_count}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <span className={`font-mono font-bold ${row.secrets_redacted_count > 0 ? 'text-amber-400' : 'text-gray-500'}`}>
                        {row.secrets_redacted_count}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-gray-950 border border-gray-800 text-gray-300 font-mono">
                        <Lock className="w-3 h-3 text-cyan-400" />
                        {row.ai_mode || 'Local'}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <button
                        type="button"
                        onClick={() => onSelectAnalysis && onSelectAnalysis(row.analysis_id)}
                        className="px-3 py-1.5 rounded-lg bg-purple-900/40 hover:bg-purple-800/60 border border-purple-700/60 text-purple-200 text-xs font-semibold inline-flex items-center gap-1.5 transition-colors shadow-sm"
                        title="Open Deep Audit Inspection"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect Audit</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="p-4 bg-gray-950/80 border-t border-gray-800 flex items-center justify-between flex-wrap gap-4 text-xs text-gray-400">
          <div>
            Showing <span className="font-semibold text-gray-200">{filteredHistory.length}</span> of{' '}
            <span className="font-semibold text-gray-200">{totalCount}</span> records
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={page <= 1 || loading}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="p-1.5 rounded-lg bg-gray-900 border border-gray-800 hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed text-gray-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span>
              Page <span className="font-bold text-gray-200">{page}</span> of{' '}
              <span className="font-bold text-gray-200">{totalPages}</span>
            </span>
            <button
              type="button"
              disabled={page >= totalPages || loading}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="p-1.5 rounded-lg bg-gray-900 border border-gray-800 hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed text-gray-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
