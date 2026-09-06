import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Search,
  Filter,
  FileCode,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ExternalLink,
  Code2,
  Sparkles,
  Key
} from 'lucide-react';
import { fetchAggregatedFindings } from '../../services/api';

export default function FindingsView({ onNavigate, onSelectAnalysis }) {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [expandedFindings, setExpandedFindings] = useState({});

  const loadFindings = async () => {
    setLoading(true);
    setError(null);
    const res = await fetchAggregatedFindings({
      severity: selectedSeverity || undefined,
      category: selectedCategory || undefined,
      search: searchQuery || undefined,
      limit: 100,
    });
    setLoading(false);
    if (res.success && res.data) {
      setFindings(res.data);
      // Auto-expand first finding
      if (res.data.length > 0) {
        setExpandedFindings({ [res.data[0].finding_id]: true });
      }
    } else {
      setError(res.error || 'Failed to load findings catalog.');
    }
  };

  useEffect(() => {
    loadFindings();
  }, [selectedSeverity, selectedCategory]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadFindings();
  };

  const toggleFinding = (id) => {
    setExpandedFindings((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
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
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 pb-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-red-950/70 text-red-400 border border-red-800/60 shadow-lg shadow-red-950/30">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Universal Findings Catalog</h2>
            <p className="text-sm text-gray-400">
              Aggregated vulnerability inventory across all local static scans, SAST checks, and secret scans.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={loadFindings}
          disabled={loading}
          className="btn btn-outline btn-sm flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Findings</span>
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by vulnerability title, rule ID (e.g. SEC-EVAL-001), filename, or code snippet..."
              className="w-full px-4 py-2 rounded-lg bg-gray-950 border border-gray-700 text-white text-xs font-mono focus:border-cyan-500 focus:outline-none pr-9"
            />
            <Search className="w-4 h-4 text-gray-500 absolute right-3 top-2.5" />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg font-bold text-xs bg-cyan-600 hover:bg-cyan-500 text-white transition-all cursor-pointer"
          >
            Search
          </button>
        </form>

        {/* Severity & Category Filters */}
        <div className="flex items-center justify-between flex-wrap gap-3 pt-2 border-t border-gray-800/60 text-xs">
          {/* Severity Pills */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-gray-400 font-semibold mr-1">Severity:</span>
            {['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
              <button
                key={sev}
                type="button"
                onClick={() => setSelectedSeverity(sev)}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer text-xs ${
                  selectedSeverity === sev
                    ? 'bg-cyan-950 text-cyan-300 border border-cyan-700 shadow-sm'
                    : 'bg-gray-950/60 text-gray-400 hover:text-gray-200 border border-gray-800'
                }`}
              >
                {sev || 'ALL'}
              </button>
            ))}
          </div>

          {/* Category Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-gray-400 font-semibold">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1 rounded-lg bg-gray-950 border border-gray-700 text-white text-xs focus:border-cyan-500 focus:outline-none"
            >
              <option value="">All Categories</option>
              <option value="SECURITY">Security (AST/SAST)</option>
              <option value="SECRETS">Secrets & Credentials</option>
              <option value="CODE_QUALITY">Code Quality</option>
              <option value="COMPLEXITY">Complexity</option>
              <option value="ERROR_HANDLING">Error Handling</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/50 border border-red-800 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Findings List */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-8 rounded-xl bg-gray-900/60 border border-gray-800 text-center space-y-3">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto" />
            <p className="text-xs text-gray-400">Querying findings inventory...</p>
          </div>
        ) : findings.length > 0 ? (
          findings.map((finding) => (
            <div
              key={finding.finding_id}
              className="rounded-xl border border-gray-800 bg-gray-900/80 overflow-hidden transition-all shadow-md"
            >
              {/* Finding Header */}
              <div
                onClick={() => toggleFinding(finding.finding_id)}
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-800/50 select-none flex-wrap gap-2"
              >
                <div className="flex items-center gap-3">
                  {getSeverityBadge(finding.severity)}
                  <span className="font-mono text-cyan-400 font-bold text-xs">{finding.issue_id}</span>
                  <span className="text-sm font-bold text-gray-100">{finding.title}</span>
                </div>

                <div className="flex items-center gap-3 text-xs text-gray-400">
                  <span className="font-mono bg-gray-950 px-2 py-0.5 rounded border border-gray-800">
                    {finding.file}:{finding.line_number || 'N/A'}
                  </span>
                  <span className="text-gray-500 font-mono text-[11px]">
                    Analyzer: {finding.analyzer}
                  </span>
                  {expandedFindings[finding.finding_id] ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </div>

              {/* Finding Expanded Detail */}
              {expandedFindings[finding.finding_id] && (
                <div className="p-4 border-t border-gray-800 bg-gray-950/70 space-y-3 text-xs">
                  {/* Code Snippet */}
                  {finding.code_snippet && (
                    <div>
                      <div className="text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1.5">
                        <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Sanitized Code Snippet:</span>
                      </div>
                      <pre className="p-3 rounded-lg bg-black/80 font-mono text-xs text-gray-200 overflow-x-auto whitespace-pre border border-gray-800">
                        {finding.code_snippet}
                      </pre>
                    </div>
                  )}

                  {/* Recommendation Guidance */}
                  <div className="p-3 rounded-lg bg-gray-900 border border-gray-800 space-y-1">
                    <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Remediation Guidance:</span>
                    </div>
                    <p className="text-gray-300 leading-relaxed text-xs">{finding.recommendation}</p>
                  </div>

                  {/* Footer & Action */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-800/60 text-[11px] text-gray-500">
                    <span>Detected: {new Date(finding.timestamp).toLocaleString()} • Confidence: {Math.round(finding.confidence * 100)}%</span>
                    <button
                      type="button"
                      onClick={() => {
                        if (onSelectAnalysis) onSelectAnalysis(finding.analysis_id);
                        onNavigate('analysis-details');
                      }}
                      className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 cursor-pointer"
                    >
                      <span>Open Full Analysis Session</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="p-8 rounded-xl bg-gray-900/40 border border-gray-800 text-center space-y-2">
            <ShieldAlert className="w-8 h-8 text-gray-600 mx-auto" />
            <h4 className="text-sm font-bold text-gray-300">No matching findings found</h4>
            <p className="text-xs text-gray-500">Try adjusting your search query or severity filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}
