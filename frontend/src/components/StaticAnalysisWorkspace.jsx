import React, { useState } from 'react';
import { 
  Code2, 
  Bug, 
  AlertOctagon, 
  AlertTriangle, 
  ShieldCheck, 
  Info, 
  CheckCircle2, 
  RefreshCw, 
  Terminal, 
  Zap, 
  Filter, 
  Cpu, 
  Layers,
  HelpCircle
} from 'lucide-react';
import { runStaticAnalysis } from '../services/api';

const PRESET_ANALYSIS_SAMPLES = {
  rce: {
    title: "Code Execution (eval / exec)",
    filename: "dynamic_evaluator.py",
    language: "python",
    code: `def execute_dynamic_expression(user_formula: str, context_data: dict):
    """Dynamically evaluates mathematical expression from user."""
    # Critical Risk: Arbitrary Code Execution
    result = eval(user_formula)
    
    if "admin" in context_data:
        exec(f"process_admin_privileges('{context_data['admin']}')")
        
    return result`
  },
  injection: {
    title: "Command & SQL Injection",
    filename: "database_and_system.py",
    language: "python",
    code: `import os
import subprocess

def query_user_profile(db_cursor, user_id: str, host: str):
    # High Risk: SQL Injection via f-string formatting
    query = f"SELECT * FROM users WHERE id = '{user_id}' AND is_active = 1"
    db_cursor.execute(query)
    
    # Critical Risk: Command Injection via shell=True and os.system
    os.system(f"ping -c 1 {host}")
    subprocess.Popen(f"nslookup {host}", shell=True)
    
    return db_cursor.fetchall()`
  },
  deserialization: {
    title: "Unsafe Deserialization",
    filename: "session_serializer.py",
    language: "python",
    code: `import pickle
import yaml

def restore_session_state(raw_session_bytes: bytes, yaml_config_str: str):
    # Critical Risk: Insecure Python Object Unpickling
    session_obj = pickle.loads(raw_session_bytes)
    
    # High Risk: PyYAML load without SafeLoader
    config_data = yaml.load(yaml_config_str)
    
    return session_obj, config_data`
  },
  exceptions: {
    title: "Flawed Exception Handling",
    filename: "payment_handler.py",
    language: "python",
    code: `def process_transaction(order_id: str, amount: float):
    try:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        # Perform payment logic
        return {"order_id": order_id, "status": "COMPLETED"}
    except Exception:
        # High Risk: Silent Exception Swallowing
        pass`
  },
  crypto: {
    title: "Weak Crypto & Insecure SSL",
    filename: "crypto_manager.py",
    language: "python",
    code: `import hashlib
import ssl

def generate_checksum_and_connect(payload: bytes):
    # Medium Risk: Deprecated MD5 and SHA-1 collision vulnerabilities
    md5_hash = hashlib.md5(payload).hexdigest()
    sha1_hash = hashlib.sha1(payload).hexdigest()
    
    # High Risk: Disabled SSL Certificate Validation
    insecure_ctx = ssl._create_unverified_context()
    
    return md5_hash, sha1_hash`
  },
  nested: {
    title: "Deeply Nested Code",
    filename: "validation_tree.py",
    language: "python",
    code: `def validate_multi_tier_access(user, account, role, permissions):
    # Code Quality Smell: Deeply Nested Control Flow
    if user.is_authenticated:
        if account.is_active:
            if role.name == 'ADMIN':
                if 'SUPER_WRITE' in permissions:
                    for perm in permissions:
                        if perm.startswith('SEC_'):
                            return True
    return False`
  },
  clean: {
    title: "Clean Secure Code",
    filename: "pricing_calculator.py",
    language: "python",
    code: `from typing import List

def compute_discounted_total(items: List[dict], discount_rate: float) -> float:
    """Calculates total price safely using parameterized inputs."""
    if not 0.0 <= discount_rate <= 1.0:
        raise ValueError("Discount rate must be between 0.0 and 1.0")
        
    subtotal = sum(item.get('price', 0.0) * item.get('quantity', 1) for item in items)
    discount_amount = subtotal * discount_rate
    return round(subtotal - discount_amount, 2)`
  }
};

export default function StaticAnalysisWorkspace() {
  const [selectedPreset, setSelectedPreset] = useState('rce');
  const [filename, setFilename] = useState(PRESET_ANALYSIS_SAMPLES.rce.filename);
  const [content, setContent] = useState(PRESET_ANALYSIS_SAMPLES.rce.code);
  const [selectedSeverityFilter, setSelectedSeverityFilter] = useState('ALL');
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('ALL');

  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSelectPreset = (key) => {
    const sample = PRESET_ANALYSIS_SAMPLES[key];
    setSelectedPreset(key);
    setFilename(sample.filename);
    setContent(sample.code);
    setError(null);
    setAnalysisResult(null);
  };

  const handleRunAnalysis = async (e) => {
    e.preventDefault();
    if (!content.trim()) {
      setError("Please provide Python source code to analyze.");
      return;
    }

    setLoading(true);
    setError(null);

    const res = await runStaticAnalysis({
      filename,
      language: "python",
      content
    });

    if (res.success) {
      setAnalysisResult(res.data);
    } else {
      setError(res.error);
    }
    setLoading(false);
  };

  const filteredFindings = analysisResult?.findings?.filter((finding) => {
    const matchSeverity = selectedSeverityFilter === 'ALL' || finding.severity === selectedSeverityFilter;
    const matchCategory = selectedCategoryFilter === 'ALL' || finding.category === selectedCategoryFilter;
    return matchSeverity && matchCategory;
  }) || [];

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '8px',
            borderRadius: '8px',
            background: 'rgba(139, 92, 246, 0.1)',
            border: '1px solid rgba(139, 92, 246, 0.3)'
          }}>
            <Code2 size={20} color="#8b5cf6" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>Local Static Code Analysis Engine</h2>
              <span className="badge badge-violet" style={{ fontSize: '0.65rem' }}>MODULE 4 ACTIVE</span>
            </div>
            <p style={{ fontSize: '0.8rem' }}>Python AST visitor &bull; Bandit SAST integration &bull; Zero code execution &bull; Offline analysis</p>
          </div>
        </div>

        {/* Engine Badges */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <span className="badge badge-cyan">AST Scanner</span>
          <span className="badge badge-violet">Bandit SAST</span>
          <span className="badge badge-emerald">Zero-LLM Mode</span>
        </div>
      </div>

      {/* Preset Scenarios */}
      <div style={{ marginBottom: '16px' }}>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>
          Load Static Analysis Test Scenarios:
        </span>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {Object.entries(PRESET_ANALYSIS_SAMPLES).map(([key, sample]) => (
            <button
              key={key}
              type="button"
              onClick={() => handleSelectPreset(key)}
              className="btn btn-outline"
              style={{
                fontSize: '0.75rem',
                padding: '5px 10px',
                borderColor: selectedPreset === key ? 'rgba(139, 92, 246, 0.5)' : 'var(--border-subtle)',
                background: selectedPreset === key ? 'rgba(139, 92, 246, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                color: selectedPreset === key ? '#c084fc' : '#94a3b8'
              }}
            >
              {sample.title}
            </button>
          ))}
        </div>
      </div>

      {/* Code Input Form */}
      <form onSubmit={handleRunAnalysis} style={{ marginBottom: '20px' }}>
        <div style={{ position: 'relative', marginBottom: '12px' }}>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={9}
            placeholder="Enter Python code to inspect statically..."
            style={{
              width: '100%',
              background: 'rgba(9, 13, 22, 0.9)',
              color: '#a78bfa',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.85rem',
              lineHeight: '1.5',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              padding: '14px',
              outline: 'none',
              resize: 'vertical',
              boxShadow: 'inset 0 2px 8px rgba(0, 0, 0, 0.5)'
            }}
          />
        </div>

        {/* Action Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            Inspects: RCE (eval/exec), Command Injection, SQL Injection, Deserialization, Weak Hashes, Exception Smells, Complexity
          </span>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
              color: '#ffffff',
              boxShadow: '0 4px 14px rgba(139, 92, 246, 0.35)'
            }}
            id="run-static-analysis-btn"
          >
            {loading ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Zap size={16} />}
            <span>{loading ? 'Analyzing AST & SAST Rules...' : 'Run Local Static Analysis'}</span>
          </button>
        </div>
      </form>

      {/* Error Alert */}
      {error && (
        <div style={{
          marginBottom: '16px',
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
          <div>{error}</div>
        </div>
      )}

      {/* Analysis Results Display */}
      {analysisResult && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 0 35px rgba(139, 92, 246, 0.1)'
        }}>
          
          {/* Summary Metric Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '46px',
                height: '46px',
                borderRadius: '10px',
                background: analysisResult.summary.risk_score > 50 
                  ? 'rgba(244, 63, 94, 0.15)' 
                  : analysisResult.summary.risk_score > 20 
                    ? 'rgba(245, 158, 11, 0.15)' 
                    : 'rgba(16, 185, 129, 0.15)',
                border: `1px solid ${
                  analysisResult.summary.risk_score > 50 
                    ? 'rgba(244, 63, 94, 0.4)' 
                    : analysisResult.summary.risk_score > 20 
                      ? 'rgba(245, 158, 11, 0.4)' 
                      : 'rgba(16, 185, 129, 0.4)'
                }`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
              }}>
                <span style={{
                  fontSize: '1rem',
                  fontWeight: 800,
                  color: analysisResult.summary.risk_score > 50 
                    ? '#f43f5e' 
                    : analysisResult.summary.risk_score > 20 
                      ? '#f59e0b' 
                      : '#10b981'
                }}>
                  {analysisResult.summary.risk_score}
                </span>
              </div>
              <div>
                <strong style={{ fontSize: '1rem', color: '#f8fafc' }}>
                  Static Analysis Completed ({analysisResult.summary.total_issues} issues identified)
                </strong>
                <span style={{ display: 'block', fontSize: '0.75rem', color: '#94a3b8' }}>
                  Session ID: <code>{analysisResult.analysis_id}</code> &bull; File: <code>{analysisResult.filename}</code>
                </span>
              </div>
            </div>

            {/* Severity Pill Counts */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-rose">Critical: {analysisResult.summary.critical_count}</span>
              <span className="badge badge-amber">High: {analysisResult.summary.high_count}</span>
              <span className="badge badge-cyan">Medium: {analysisResult.summary.medium_count}</span>
              <span className="badge badge-violet">Low: {analysisResult.summary.low_count}</span>
            </div>
          </div>

          {/* Findings Filter Bar */}
          {analysisResult.summary.total_issues > 0 && (
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '8px',
              padding: '8px 12px',
              marginBottom: '16px',
              flexWrap: 'wrap',
              gap: '10px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Filter size={14} color="#94a3b8" />
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Filter Severity:</span>
                {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
                  <button
                    key={sev}
                    type="button"
                    onClick={() => setSelectedSeverityFilter(sev)}
                    style={{
                      padding: '3px 8px',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      border: 'none',
                      background: selectedSeverityFilter === sev ? 'rgba(139, 92, 246, 0.25)' : 'transparent',
                      color: selectedSeverityFilter === sev ? '#c084fc' : '#64748b'
                    }}
                  >
                    {sev}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Category:</span>
                {['ALL', 'SECURITY', 'ERROR_HANDLING', 'CODE_QUALITY', 'INSECURE_CONFIG'].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategoryFilter(cat)}
                    style={{
                      padding: '3px 8px',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      border: 'none',
                      background: selectedCategoryFilter === cat ? 'rgba(6, 182, 212, 0.25)' : 'transparent',
                      color: selectedCategoryFilter === cat ? '#22d3ee' : '#64748b'
                    }}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Findings List */}
          {filteredFindings.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '16px' }}>
              {filteredFindings.map((finding, idx) => {
                const isCrit = finding.severity === 'CRITICAL';
                const isHigh = finding.severity === 'HIGH';
                const isMed = finding.severity === 'MEDIUM';

                const badgeClass = isCrit ? 'badge-rose' : isHigh ? 'badge-amber' : isMed ? 'badge-cyan' : 'badge-violet';

                return (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(9, 13, 22, 0.85)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '10px',
                      padding: '14px'
                    }}
                  >
                    {/* Finding Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className={`badge ${badgeClass}`} style={{ fontSize: '0.65rem' }}>
                          {finding.severity}
                        </span>
                        <strong style={{ fontSize: '0.9rem', color: '#f1f5f9' }}>
                          {finding.title}
                        </strong>
                      </div>
                      
                      <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.75rem', color: '#06b6d4', fontFamily: 'var(--font-mono)' }}>
                          Line {finding.line_number}
                        </span>
                        <span className="badge badge-violet" style={{ fontSize: '0.65rem' }}>
                          {finding.analyzer}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                          {(finding.confidence * 100).toFixed(0)}% Conf
                        </span>
                      </div>
                    </div>

                    {/* Code Snippet Highlight */}
                    <div style={{
                      background: 'rgba(0, 0, 0, 0.4)',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '0.78rem',
                      fontFamily: 'var(--font-mono)',
                      color: isCrit || isHigh ? '#fca5a5' : '#e2e8f0',
                      borderLeft: `3px solid ${isCrit ? '#f43f5e' : isHigh ? '#f59e0b' : '#38bdf8'}`,
                      marginBottom: '8px',
                      overflowX: 'auto'
                    }}>
                      <code>{finding.code_snippet}</code>
                    </div>

                    {/* Remediation Recommendation */}
                    <div style={{ fontSize: '0.78rem', color: '#cbd5e1', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                      <span style={{ color: '#10b981', fontWeight: 700 }}>Recommendation:</span>
                      <span>{finding.recommendation}</span>
                    </div>

                  </div>
                );
              })}
            </div>
          ) : analysisResult.summary.total_issues === 0 ? (
            <div style={{
              padding: '14px 18px',
              background: 'rgba(16, 185, 129, 0.05)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.85rem',
              color: '#a7f3d0',
              marginBottom: '16px'
            }}>
              <CheckCircle2 size={18} color="#10b981" />
              <span>Clean Code: Zero syntactic security vulnerabilities, injection patterns, or complexity smells detected!</span>
            </div>
          ) : (
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', padding: '12px', textAlign: 'center' }}>
              No findings match the current filter selection.
            </div>
          )}

          {/* Scientific Disclaimer Banner */}
          <div style={{
            padding: '10px 14px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.75rem',
            color: '#94a3b8'
          }}>
            <HelpCircle size={16} color="#64748b" />
            <span>
              <strong>Static Analysis Boundary Notice:</strong> {analysisResult.disclaimer}
            </span>
          </div>

        </div>
      )}

    </section>
  );
}
