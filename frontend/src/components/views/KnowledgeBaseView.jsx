import React from 'react';
import { BookOpen, Database, Sparkles, Shield, Lock, Search } from 'lucide-react';
import RAGKnowledgeWorkspace from '../RAGKnowledgeWorkspace';

export default function KnowledgeBaseView() {
  return (
    <div className="space-y-6">
      {/* Knowledge Base Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-950/40 via-gray-900 to-indigo-950/40 border border-amber-800/60 shadow-xl flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded bg-amber-900/80 text-amber-300 border border-amber-700">
              MODULE 9 KNOWLEDGE RAG
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800">
              Semantic Vector Indexing
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            Engineering Knowledge Base & Grounded RAG
          </h2>
          <p className="text-sm text-gray-300 max-w-3xl mt-1">
            Query curated security standards, CWE guidelines, and remediation playbooks. Vector embeddings match findings to verified engineering documentation without uploading proprietary source code.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gray-950/80 border border-gray-800 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-950 text-amber-400 border border-amber-800">
              <Database className="w-4 h-4" />
            </div>
            <div className="text-xs">
              <div className="font-bold text-gray-200">Vector Grounded</div>
              <div className="text-gray-500">Zero AI Hallucinations</div>
            </div>
          </div>
        </div>
      </div>

      {/* RAG Knowledge Workspace Component */}
      <RAGKnowledgeWorkspace />
    </div>
  );
}
