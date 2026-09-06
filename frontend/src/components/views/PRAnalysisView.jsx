import React from 'react';
import { GitPullRequest, Shield, Lock, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import GitHubPRAnalyzer from '../GitHubPRAnalyzer';

export default function PRAnalysisView() {
  return (
    <div className="space-y-6">
      {/* PR Analysis Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/50 via-gray-900 to-purple-950/50 border border-blue-800/60 shadow-xl flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded bg-blue-900/80 text-blue-300 border border-blue-700">
              MODULE 10 PULL REQUEST ENGINE
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800">
              GitHub Diff & Patch Scanning
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            GitHub Pull Request Security & Risk Analysis
          </h2>
          <p className="text-sm text-gray-300 max-w-3xl mt-1">
            Inspect live GitHub pull requests and diff patches with strict privacy guardrails. Zero repo cloning, in-memory patch parsing, local AST/SAST analysis, secret redaction, and RAG-augmented composite risk scoring.
          </p>
        </div>

        {/* Security Badges */}
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gray-950/80 border border-gray-800 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-800">
              <Shield className="w-4 h-4" />
            </div>
            <div className="text-xs">
              <div className="font-bold text-gray-200">No Repo Cloning</div>
              <div className="text-gray-500">In-memory diff evaluation</div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-gray-950/80 border border-gray-800 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
              <Lock className="w-4 h-4" />
            </div>
            <div className="text-xs">
              <div className="font-bold text-gray-200">Zero Token Leaks</div>
              <div className="text-gray-500">Encrypted token lifecycle</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main PR Scanner Component */}
      <GitHubPRAnalyzer />
    </div>
  );
}
