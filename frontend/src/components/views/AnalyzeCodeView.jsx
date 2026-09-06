import React, { useState } from 'react';
import { FileCode, Shield, Sparkles, Terminal, Activity, ArrowRight } from 'lucide-react';
import CodeIngestionCard from '../CodeIngestionCard';
import StaticAnalysisWorkspace from '../StaticAnalysisWorkspace';
import RiskScoringDashboard from '../RiskScoringDashboard';
import AIAnalysisWorkspace from '../AIAnalysisWorkspace';
import DeveloperRemediationCard from '../DeveloperRemediationCard';

export default function AnalyzeCodeView() {
  const [activeSubTab, setActiveSubTab] = useState('pipeline');

  return (
    <div className="space-y-6">
      {/* Studio Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-950/50 via-gray-900 to-cyan-950/50 border border-emerald-800/60 shadow-xl flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded bg-emerald-900/80 text-emerald-300 border border-emerald-700">
              MODULE 2-7 UNIFIED PIPELINE
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800">
              Zero Raw Code Exposure
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            Local Static Analysis & AI Remediation Studio
          </h2>
          <p className="text-sm text-gray-300 max-w-3xl mt-1">
            Analyze proprietary code locally via Python AST and Bandit SAST rules. Compute deterministic and ML risk scores, and generate privacy-safe tripartite remediations without transmitting sensitive code.
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-2 bg-gray-950/80 p-1.5 rounded-xl border border-gray-800">
          <button
            type="button"
            onClick={() => setActiveSubTab('pipeline')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'pipeline'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Full Analysis Pipeline
          </button>
          <button
            type="button"
            onClick={() => setActiveSubTab('ingestion')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'ingestion'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Ingestion & Secrets
          </button>
          <button
            type="button"
            onClick={() => setActiveSubTab('static')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'static'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Static AST / SAST
          </button>
          <button
            type="button"
            onClick={() => setActiveSubTab('risk')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'risk'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Risk Scoring & ML
          </button>
          <button
            type="button"
            onClick={() => setActiveSubTab('remediation')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'remediation'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            AI Remediations
          </button>
        </div>
      </div>

      {/* Content Rendering based on Sub-Tab */}
      {activeSubTab === 'pipeline' && (
        <div className="space-y-6">
          <CodeIngestionCard />
          <StaticAnalysisWorkspace />
          <RiskScoringDashboard />
          <AIAnalysisWorkspace />
          <DeveloperRemediationCard />
        </div>
      )}

      {activeSubTab === 'ingestion' && (
        <div className="space-y-6">
          <CodeIngestionCard />
        </div>
      )}

      {activeSubTab === 'static' && (
        <div className="space-y-6">
          <StaticAnalysisWorkspace />
        </div>
      )}

      {activeSubTab === 'risk' && (
        <div className="space-y-6">
          <RiskScoringDashboard />
        </div>
      )}

      {activeSubTab === 'remediation' && (
        <div className="space-y-6">
          <AIAnalysisWorkspace />
          <DeveloperRemediationCard />
        </div>
      )}
    </div>
  );
}
