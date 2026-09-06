import React from 'react';
import {
  Shield,
  LayoutDashboard,
  FileCode,
  GitPullRequest,
  AlertTriangle,
  FileSearch,
  ShieldCheck,
  BookOpen,
  History,
  Settings,
  Lock,
  ExternalLink,
  RefreshCw,
  EyeOff
} from 'lucide-react';

export default function Navbar({
  activeTab,
  onTabChange,
  healthData,
  latency,
  loading,
  error,
  onRefresh
}) {
  const isOnline = Boolean(healthData && !error);
  const statusColor = isOnline ? 'emerald' : 'rose';
  
  // Determine active AI Mode
  let activeAiMode = 'Private/Local LLM';
  if (healthData?.config?.ai_enabled === false) {
    activeAiMode = 'Disabled';
  } else if (healthData?.config?.llm_provider === 'external') {
    activeAiMode = 'External LLM';
  } else if (healthData?.config?.llm_provider === 'local') {
    activeAiMode = 'Private/Local LLM';
  }

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'analyze_code', label: 'Analyze Code', icon: FileCode },
    { id: 'pr_analysis', label: 'PR Analysis', icon: GitPullRequest },
    { id: 'findings', label: 'Findings', icon: AlertTriangle },
    { id: 'analysis_details', label: 'Analysis Details', icon: FileSearch },
    { id: 'security_privacy', label: 'Security & Privacy', icon: ShieldCheck },
    { id: 'knowledge_base', label: 'Knowledge Base', icon: BookOpen },
    { id: 'history', label: 'History', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="space-y-4 mb-6">
      {/* Top Banner & Telemetry Bar */}
      <div className="glass-panel" style={{ padding: '16px 24px', borderRadius: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          
          {/* Brand & Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)'
            }}>
              <Shield size={24} color="#10b981" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff' }}>
                  Privacy-Preserving AI Code Security
                </h1>
                <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>
                  v1.0.0
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                Modular Monolith &bull; Enterprise Code Risk Analysis & Remediation
              </p>
            </div>
          </div>

          {/* Prominent Privacy Indicator & Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            
            {/* AI Mode Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-900 border border-gray-800 shadow-inner">
              <span className="text-[11px] text-gray-400 font-bold uppercase tracking-wide">AI MODE:</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold font-mono ${
                activeAiMode === 'Disabled'
                  ? 'bg-gray-800 text-gray-400 border border-gray-700'
                  : activeAiMode === 'External LLM'
                  ? 'bg-blue-950 text-blue-400 border border-blue-800'
                  : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
              }`}>
                {activeAiMode}
              </span>
            </div>

            {/* Privacy Assurance Pill */}
            <div 
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-950/80 text-cyan-300 border border-cyan-800/80 text-xs font-medium"
              title="Guaranteed: Secrets detected and redacted before any AI analysis."
            >
              <EyeOff size={14} className="text-cyan-400" />
              <span className="hidden sm:inline">Secrets redacted before AI</span>
            </div>

            {/* Backend Connection Indicator */}
            <div 
              className={`badge badge-${statusColor}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 14px' }}
              id="backend-connection-badge"
            >
              <span className={`indicator-dot ${isOnline ? 'online' : 'offline'}`}></span>
              <span style={{ fontWeight: 600, fontSize: '0.8rem' }}>
                {isOnline ? `Online (${latency}ms)` : 'Offline'}
              </span>
            </div>

            {/* Quick Refresh */}
            <button 
              type="button"
              onClick={onRefresh} 
              className="btn btn-outline btn-icon"
              title="Refresh System Status"
              id="refresh-health-btn"
            >
              <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            </button>

            {/* Swagger Docs Link */}
            <a 
              href="http://127.0.0.1:8000/docs" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="btn btn-outline"
              style={{ fontSize: '0.8rem', padding: '6px 12px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <span>API Docs</span>
              <ExternalLink size={13} />
            </a>

          </div>
        </div>
      </div>

      {/* 9-Page Navigation Bar */}
      <nav className="glass-panel" style={{ padding: '8px 12px', borderRadius: '14px', overflowX: 'auto' }}>
        <div className="flex items-center gap-1 min-w-max">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onTabChange(item.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-950 font-bold'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800/60'
                }`}
                id={`nav-tab-${item.id}`}
              >
                <Icon size={15} className={isActive ? 'text-white' : 'text-gray-400'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
