import React from 'react';
import OverviewView from '../components/views/OverviewView';
import AnalyzeCodeView from '../components/views/AnalyzeCodeView';
import PRAnalysisView from '../components/views/PRAnalysisView';
import FindingsView from '../components/views/FindingsView';
import AnalysisDetailsView from '../components/views/AnalysisDetailsView';
import SecurityPrivacyView from '../components/views/SecurityPrivacyView';
import KnowledgeBaseView from '../components/views/KnowledgeBaseView';
import HistoryView from '../components/views/HistoryView';
import SettingsView from '../components/views/SettingsView';

export default function Dashboard({
  activeTab,
  onNavigate,
  selectedAnalysisId,
  onSelectAnalysis,
  healthData,
  latency,
  loading,
  error,
  lastUpdated,
  isPolling,
  onTogglePolling,
  onRefresh
}) {
  return (
    <main className="w-full">
      {activeTab === 'overview' && (
        <OverviewView
          onNavigate={onNavigate}
          onSelectAnalysis={onSelectAnalysis}
        />
      )}

      {activeTab === 'analyze_code' && (
        <AnalyzeCodeView />
      )}

      {activeTab === 'pr_analysis' && (
        <PRAnalysisView />
      )}

      {activeTab === 'findings' && (
        <FindingsView
          onSelectAnalysis={onSelectAnalysis}
        />
      )}

      {activeTab === 'analysis_details' && (
        <AnalysisDetailsView
          initialAnalysisId={selectedAnalysisId}
        />
      )}

      {activeTab === 'security_privacy' && (
        <SecurityPrivacyView />
      )}

      {activeTab === 'knowledge_base' && (
        <KnowledgeBaseView />
      )}

      {activeTab === 'history' && (
        <HistoryView
          onSelectAnalysis={onSelectAnalysis}
        />
      )}

      {activeTab === 'settings' && (
        <SettingsView
          healthData={healthData}
          latency={latency}
          loading={loading}
          error={error}
          lastUpdated={lastUpdated}
          isPolling={isPolling}
          onTogglePolling={onTogglePolling}
          onRefresh={onRefresh}
        />
      )}
    </main>
  );
}
