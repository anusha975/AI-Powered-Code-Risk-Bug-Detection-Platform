import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import { useHealthCheck } from './hooks/useHealthCheck';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null);

  const {
    healthData,
    latency,
    loading,
    error,
    lastUpdated,
    isPolling,
    setIsPolling,
    refetch
  } = useHealthCheck(5000);

  const handleSelectAnalysis = (analysisId) => {
    setSelectedAnalysisId(analysisId);
    setActiveTab('analysis_details');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigate = (tabId) => {
    setActiveTab(tabId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-container" style={{ maxWidth: '1440px', margin: '0 auto', padding: '0 20px 40px 20px' }}>
      {/* Top Navigation Bar with 9 Views */}
      <Navbar 
        activeTab={activeTab}
        onTabChange={handleNavigate}
        healthData={healthData}
        latency={latency}
        loading={loading}
        error={error}
        onRefresh={refetch}
      />

      {/* Dynamic 9-View Dashboard Router */}
      <Dashboard 
        activeTab={activeTab}
        onNavigate={handleNavigate}
        selectedAnalysisId={selectedAnalysisId}
        onSelectAnalysis={handleSelectAnalysis}
        healthData={healthData}
        latency={latency}
        loading={loading}
        error={error}
        lastUpdated={lastUpdated}
        isPolling={isPolling}
        onTogglePolling={() => setIsPolling(!isPolling)}
        onRefresh={refetch}
      />

      {/* Global Engineering Footer */}
      <footer style={{ marginTop: '50px', textAlign: 'center', fontSize: '0.8rem', color: '#64748b', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '20px' }}>
        <p>
          Privacy-Preserving AI Code Security & Risk Analysis Platform &bull; Production Modular Monolith &bull; Modules 1–11 Complete
        </p>
      </footer>
    </div>
  );
}
