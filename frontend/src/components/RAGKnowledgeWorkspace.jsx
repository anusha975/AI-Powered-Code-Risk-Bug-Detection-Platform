import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  FileText,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  Tag,
  Plus,
  Sparkles,
  Layers,
  History,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  Activity,
  Sliders,
  Database,
  HelpCircle,
  Copy,
  Check
} from 'lucide-react';
import { fetchRAGDocuments, queryRAG, indexRAGDocument } from '../services/api';

const QUICK_QUERIES = [
  { label: 'SQL Injection Standards', query: 'How do I prevent SQL injection in Python database queries?' },
  { label: 'Safe eval() Alternatives', query: 'What are the safe alternatives to dynamic eval and exec in Python?' },
  { label: 'Billing Incident (INC-2024-001)', query: 'What was the root cause and remediation for the billing API incident (INC-2024-001)?' },
  { label: 'Command Injection Post-Mortem', query: 'What was the post-mortem for the network traceroute command injection incident?' },
  { label: 'Pickle Deserialization RCE', query: 'Why is pickle.loads unsafe for untrusted input and what should be used instead?' },
  { label: 'Unrelated Query (Missing Evidence Test)', query: 'How to bake a sourdough pizza with active dry yeast?' }
];

export default function RAGKnowledgeWorkspace() {
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);

  // Query State
  const [searchQuery, setSearchQuery] = useState(QUICK_QUERIES[0].query);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [querying, setQuerying] = useState(false);
  const [ragResult, setRagResult] = useState(null);
  const [queryError, setQueryError] = useState(null);

  // New Document Drawer State
  const [showIndexForm, setShowIndexForm] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newSourceType, setNewSourceType] = useState('SECURITY_GUIDELINE');
  const [newContent, setNewContent] = useState('');
  const [newAuthor, setNewAuthor] = useState('Security Engineering');
  const [indexing, setIndexing] = useState(false);
  const [indexSuccessMsg, setIndexSuccessMsg] = useState(null);

  const [copiedSnippetId, setCopiedSnippetId] = useState(null);

  const loadDocuments = async () => {
    setLoadingDocs(true);
    const res = await fetchRAGDocuments();
    setLoadingDocs(false);
    if (res.success && res.data) {
      setDocuments(res.data);
      if (res.data.length > 0 && !selectedDoc) {
        setSelectedDoc(res.data[0]);
      }
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleRunRAGQuery = async (queryText = searchQuery) => {
    if (!queryText.trim()) return;

    setQuerying(true);
    setQueryError(null);
    setRagResult(null);

    const payload = {
      query: queryText,
      top_k: 3,
      similarity_threshold: 0.30,
      source_type_filter: categoryFilter || undefined
    };

    const res = await queryRAG(payload);
    setQuerying(false);

    if (res.success && res.data) {
      setRagResult(res.data);
    } else {
      setQueryError(res.error || 'Failed to execute grounded RAG query.');
    }
  };

  const handleIndexSubmit = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;

    setIndexing(true);
    setIndexSuccessMsg(null);

    const res = await indexRAGDocument({
      title: newTitle,
      source_type: newSourceType,
      content: newContent,
      author: newAuthor
    });
    setIndexing(false);

    if (res.success) {
      setIndexSuccessMsg(res.data.message || 'Document indexed successfully into vector store!');
      setNewTitle('');
      setNewContent('');
      loadDocuments();
      setTimeout(() => {
        setIndexSuccessMsg(null);
        setShowIndexForm(false);
      }, 2500);
    }
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedSnippetId(id);
    setTimeout(() => setCopiedSnippetId(null), 2000);
  };

  const getCategoryBadge = (category) => {
    switch (category) {
      case 'SECURITY_GUIDELINE':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'HISTORICAL_INCIDENT':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'CODING_STANDARD':
        return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case 'ARCHITECTURE_DOC':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="card glass-effect relative overflow-hidden border border-slate-700/60 p-6 md:p-8 space-y-6">
      {/* Ambient background glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-600/20 border border-cyan-500/30 text-cyan-400 shadow-inner">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-slate-100">
                Privacy-Aware Engineering Knowledge RAG
              </h2>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Module 9 (Active)
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Semantic vector retrieval over OWASP guidelines &amp; historical post-mortems with strict source attribution &bull; Zero code ingestion
            </p>
          </div>
        </div>

        {/* Index Document Button */}
        <button
          onClick={() => setShowIndexForm(!showIndexForm)}
          className="px-4 py-2.5 rounded-xl text-xs font-semibold border border-cyan-500/40 bg-cyan-950/40 text-cyan-300 hover:bg-cyan-900/50 flex items-center gap-2 transition-all cursor-pointer shadow-sm"
        >
          <Plus className="w-4 h-4 text-cyan-400" />
          <span>{showIndexForm ? 'Close Document Indexer' : 'Index Engineering Doc'}</span>
        </button>
      </div>

      {/* Index Document Form Drawer */}
      {showIndexForm && (
        <form onSubmit={handleIndexSubmit} className="p-5 rounded-2xl bg-slate-900/70 border border-cyan-500/30 space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Index New Engineering Document into Vector Database</span>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">In-Memory Semantic Vector Store</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="md:col-span-2 space-y-1">
              <label className="text-xs text-slate-400 font-semibold">Document Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Cryptographic Key Derivation Standard"
                required
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold">Knowledge Category</label>
              <select
                value={newSourceType}
                onChange={(e) => setNewSourceType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="SECURITY_GUIDELINE">Security Guideline</option>
                <option value="HISTORICAL_INCIDENT">Historical Incident</option>
                <option value="CODING_STANDARD">Coding Standard</option>
                <option value="ARCHITECTURE_DOC">Architecture Doc</option>
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-semibold">Document Content (Markdown)</label>
            <textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              rows={5}
              placeholder="# Standard Title&#10;&#10;## Overview&#10;Describe the guidelines or incident post-mortem here..."
              required
              className="w-full p-3 rounded-xl bg-slate-950 border border-slate-700 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 resize-y leading-relaxed"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            {indexSuccessMsg ? (
              <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{indexSuccessMsg}</span>
              </span>
            ) : <span />}

            <button
              type="submit"
              disabled={indexing}
              className="btn-primary px-5 py-2 rounded-xl text-xs font-semibold shadow-md shadow-cyan-500/20 disabled:opacity-50 cursor-pointer"
            >
              {indexing ? 'Embedding & Indexing...' : 'Index & Embed Chunks'}
            </button>
          </div>
        </form>
      )}

      {/* Search Bar & Quick Preset Queries */}
      <div className="space-y-3">
        <div className="flex flex-col md:flex-row gap-2.5">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleRunRAGQuery()}
              placeholder="Ask a question about security guidelines, coding standards, or incident retrospectives..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950/80 border border-slate-700/80 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 shadow-inner"
            />
          </div>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-slate-700/80 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Categories</option>
            <option value="SECURITY_GUIDELINE">Security Guidelines</option>
            <option value="HISTORICAL_INCIDENT">Historical Incidents</option>
            <option value="CODING_STANDARD">Coding Standards</option>
            <option value="ARCHITECTURE_DOC">Architecture Docs</option>
          </select>

          {/* Trigger Button */}
          <button
            onClick={() => handleRunRAGQuery()}
            disabled={querying}
            className="btn-primary flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl text-xs font-semibold shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all disabled:opacity-50 cursor-pointer shrink-0"
          >
            {querying ? (
              <>
                <Activity className="w-4 h-4 animate-spin text-cyan-400" />
                <span>Retrieving &amp; Grounding...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span>Search Knowledge Base</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Query Pills */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Suggested Engineering Inquiries:
          </span>
          <div className="flex flex-wrap gap-2">
            {QUICK_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setSearchQuery(q.query);
                  handleRunRAGQuery(q.query);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all cursor-pointer"
              >
                {q.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Query Error */}
      {queryError && (
        <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold">RAG Query Error</div>
            <div className="text-xs text-red-400/90 mt-0.5">{queryError}</div>
          </div>
        </div>
      )}

      {/* RAG Response Card */}
      {ragResult && (
        <div className="p-6 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-5 animate-fadeIn">
          {/* Response Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                  ragResult.is_evidence_found
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                }`}>
                  {ragResult.is_evidence_found ? 'GROUNDED EVIDENCE FOUND' : 'NO EVIDENCE FOUND'}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Latency: {ragResult.retrieval_latency_ms}ms &bull; Sources: {ragResult.sources.length}
                </span>
              </div>
              <div className="text-xs text-slate-300 font-semibold pt-1">
                Query: &ldquo;{ragResult.query}&rdquo;
              </div>
            </div>

            {ragResult.is_evidence_found && (
              <div className="text-right">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">Top Relevance</div>
                <div className="text-sm font-bold text-cyan-400">
                  {(ragResult.confidence_score * 100).toFixed(0)}% Match
                </div>
              </div>
            )}
          </div>

          {/* Grounded AI Answer / Missing Evidence Notice */}
          <div className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Grounded Knowledge Response</span>
            </div>

            {ragResult.is_evidence_found ? (
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-200 leading-relaxed space-y-2">
                <p className="whitespace-pre-line">{ragResult.answer}</p>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/40 text-xs text-amber-300 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-amber-200">{ragResult.answer}</div>
                  <div className="text-[11px] text-amber-300/80 mt-1">
                    No approved security guidelines or historical incident post-mortems matched this query with sufficient similarity. The platform strictly prohibits hallucinating non-existent documentation.
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Attributed Sources Breakdown */}
          {ragResult.sources?.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                <span>Attributed Source Documents ({ragResult.sources.length})</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {ragResult.sources.map((src, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 space-y-2.5 text-xs"
                  >
                    <div className="flex items-start justify-between gap-2 border-b border-slate-800/80 pb-2">
                      <div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getCategoryBadge(src.source_type)}`}>
                          {src.source_type}
                        </span>
                        <h4 className="font-bold text-slate-200 text-xs mt-1.5">{src.title}</h4>
                        <div className="text-[10px] text-slate-500 font-mono">
                          ID: {src.doc_id} &bull; Section: {src.section}
                        </div>
                      </div>
                      <span className="px-2 py-1 rounded bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 text-[11px] font-mono font-bold shrink-0">
                        {(src.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="relative">
                      <pre className="p-3 rounded-lg bg-slate-950 border border-slate-900 text-[11px] text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-36 overflow-y-auto">
                        {src.snippet}
                      </pre>
                      <button
                        onClick={() => handleCopy(src.snippet, src.chunk_id)}
                        className="absolute top-2 right-2 p-1.5 rounded-md bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer"
                        title="Copy Excerpt"
                      >
                        {copiedSnippetId === src.chunk_id ? (
                          <Check className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Privacy Guarantee Note */}
          <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-900/30 text-[11px] text-slate-400 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>{ragResult.privacy_guarantee}</span>
          </div>
        </div>
      )}

      {/* Knowledge Document Library Browser */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>Pre-Seeded Knowledge Library ({documents.length} Documents)</span>
          </div>
          <span className="text-[11px] text-slate-500">
            OWASP Standards &bull; Python Secure Standards &bull; Incident Retrospectives
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Document List */}
          <div className="md:col-span-1 space-y-2 max-h-80 overflow-y-auto pr-1">
            {documents.map((doc) => (
              <button
                key={doc.doc_id}
                onClick={() => setSelectedDoc(doc)}
                className={`w-full p-3 rounded-xl text-left text-xs transition-all border cursor-pointer ${
                  selectedDoc?.doc_id === doc.doc_id
                    ? 'bg-cyan-950/40 border-cyan-500/50 text-cyan-200 shadow-sm shadow-cyan-500/10'
                    : 'bg-slate-900/40 border-slate-800/80 text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${getCategoryBadge(doc.source_type)}`}>
                    {doc.source_type}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">{doc.doc_id}</span>
                </div>
                <div className="font-semibold text-slate-200 truncate">{doc.title}</div>
                <div className="text-[10px] text-slate-500 mt-1 truncate">Author: {doc.author}</div>
              </button>
            ))}
          </div>

          {/* Document Content Viewer */}
          <div className="md:col-span-2 p-5 rounded-xl bg-slate-950/80 border border-slate-800/80 overflow-y-auto max-h-80 font-mono text-xs">
            {selectedDoc ? (
              <div className="space-y-3 font-sans">
                <div className="flex items-start justify-between border-b border-slate-800 pb-2">
                  <div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getCategoryBadge(selectedDoc.source_type)}`}>
                      {selectedDoc.source_type}
                    </span>
                    <h3 className="font-bold text-slate-200 text-sm mt-1.5">{selectedDoc.title}</h3>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      ID: <code>{selectedDoc.doc_id}</code> &bull; Author: {selectedDoc.author}
                    </div>
                  </div>
                </div>
                <div className="p-3.5 rounded-lg bg-slate-900/50 border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed max-h-52 overflow-y-auto">
                  {selectedDoc.content}
                </div>
              </div>
            ) : (
              <div className="text-slate-500 text-center py-10 font-sans">Select a document from the catalog to inspect.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
