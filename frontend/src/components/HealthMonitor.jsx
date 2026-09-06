import React from 'react';
import { 
  Server, 
  Database, 
  ShieldCheck, 
  Clock, 
  Wifi, 
  WifiOff, 
  AlertTriangle, 
  CheckCircle2, 
  Zap,
  Terminal
} from 'lucide-react';

export default function HealthMonitor({ 
  healthData, 
  latency, 
  loading, 
  error, 
  lastUpdated, 
  isPolling, 
  onTogglePolling, 
  onRefresh 
}) {
  const isOnline = Boolean(healthData && !error);
  const dbConnected = healthData?.database?.status === 'CONNECTED';

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Section Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '8px',
            borderRadius: '8px',
            background: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.3)'
          }}>
            <Server size={20} color="#06b6d4" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>System Health & Telemetry</h2>
            <p style={{ fontSize: '0.8rem' }}>Real-time telemetry stream from <code>GET /api/health</code></p>
          </div>
        </div>

        {/* Polling Toggle & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: '#94a3b8', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={isPolling} 
              onChange={onTogglePolling}
              style={{ accentColor: '#10b981', cursor: 'pointer' }} 
            />
            <span>Auto-poll (5s)</span>
          </label>

          <button 
            onClick={onRefresh} 
            disabled={loading}
            className="btn btn-primary"
            style={{ fontSize: '0.8rem', padding: '6px 14px' }}
            id="ping-health-btn"
          >
            <Zap size={14} />
            <span>Ping Backend</span>
          </button>
        </div>
      </div>

      {/* Telemetry Grid */}
      <div className="grid-3" style={{ gap: '16px' }}>
        
        {/* Card 1: Backend Service Status */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>FASTAPI ENGINE</span>
            {isOnline ? (
              <span className="badge badge-emerald"><CheckCircle2 size={12} /> OPERATIONAL</span>
            ) : (
              <span className="badge badge-rose"><WifiOff size={12} /> OFFLINE</span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 700, color: isOnline ? '#10b981' : '#f43f5e' }}>
              {isOnline ? (healthData.status || 'OPERATIONAL') : 'DISCONNECTED'}
            </span>
            {latency !== null && (
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>({latency}ms RTT)</span>
            )}
          </div>

          <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>Environment: <strong style={{ color: '#cbd5e1' }}>{healthData?.environment || 'development'}</strong></div>
            <div>Uptime: <strong style={{ color: '#cbd5e1' }}>{healthData?.uptime_seconds ? `${healthData.uptime_seconds}s` : 'N/A'}</strong></div>
            <div>Version: <strong style={{ color: '#cbd5e1' }}>{healthData?.version || '1.0.0'}</strong></div>
          </div>
        </div>

        {/* Card 2: PostgreSQL Database Status */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>POSTGRESQL DB</span>
            {dbConnected ? (
              <span className="badge badge-emerald"><CheckCircle2 size={12} /> CONNECTED</span>
            ) : (
              <span className="badge badge-amber" title={healthData?.database?.message || 'Database not reachable'}><AlertTriangle size={12} /> STANDBY / OFF</span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 700, color: dbConnected ? '#10b981' : '#f59e0b' }}>
              {healthData?.database?.status || 'UNKNOWN'}
            </span>
            {healthData?.database?.latency_ms && (
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>({healthData.database.latency_ms}ms)</span>
            )}
          </div>

          <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>Engine: <strong style={{ color: '#cbd5e1' }}>{healthData?.database?.database_type || 'PostgreSQL'}</strong></div>
            <div>Host: <strong style={{ color: '#cbd5e1' }}>{healthData?.database?.host || 'localhost'}</strong></div>
            <div>Database: <strong style={{ color: '#cbd5e1' }}>{healthData?.database?.database_name || 'code_security_db'}</strong></div>
          </div>
        </div>

        {/* Card 3: Privacy Guardrails */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>PRIVACY POLICY</span>
            <span className="badge badge-cyan"><ShieldCheck size={12} /> ACTIVE</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 700, color: '#06b6d4' }}>
              {healthData?.privacy_guardrails?.analysis_mode || 'LOCAL_STATIC_ONLY'}
            </span>
          </div>

          <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div>Secret Redaction: <strong style={{ color: '#10b981' }}>{healthData?.privacy_guardrails?.secret_redaction_enforced ? 'ENFORCED' : 'OFF'}</strong></div>
            <div>Remote LLM Allowed: <strong style={{ color: healthData?.privacy_guardrails?.remote_llm_allowed ? '#f43f5e' : '#10b981' }}>{healthData?.privacy_guardrails?.remote_llm_allowed ? 'TRUE' : 'FALSE (BLOCKED)'}</strong></div>
            <div>Snippet Line Limit: <strong style={{ color: '#cbd5e1' }}>{healthData?.privacy_guardrails?.max_snippet_lines || 50} lines</strong></div>
          </div>
        </div>

      </div>

      {/* Offline/Error Notification */}
      {error && (
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          background: 'rgba(244, 63, 94, 0.08)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '0.85rem',
          color: '#fecdd3'
        }}>
          <AlertTriangle size={18} color="#f43f5e" />
          <div>
            <strong>Backend Connection Error:</strong> {error}
            <span style={{ display: 'block', fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
              Tip: Start the backend using: <code>cd backend; uvicorn app.main:app --reload</code>
            </span>
          </div>
        </div>
      )}

      {/* Sync Footer */}
      <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#64748b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Clock size={12} />
          <span>Last telemetry check: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}</span>
        </div>
        <div>
          <span>Target Endpoint: <code>/api/health</code></span>
        </div>
      </div>

    </section>
  );
}
