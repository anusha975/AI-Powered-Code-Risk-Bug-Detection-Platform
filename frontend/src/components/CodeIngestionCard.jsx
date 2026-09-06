import React, { useState } from 'react';
import { 
  FileCode2, 
  UploadCloud, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  ShieldCheck, 
  Hash, 
  Layers, 
  FileText, 
  ArrowRight,
  Sparkles,
  Terminal,
  RefreshCw
} from 'lucide-react';
import { submitCode, uploadCodeFile } from '../services/api';

const SAMPLE_SNIPPETS = {
  python: {
    filename: "payment_service.py",
    language: "python",
    code: `def process_payment(account_id: str, amount: float):\n    """Process payment transaction with verification."""\n    if amount <= 0:\n        raise ValueError("Invalid payment amount")\n    \n    transaction_id = f"tx_{account_id}_9821"\n    return {\n        "status": "APPROVED",\n        "transaction_id": transaction_id,\n        "amount": amount\n    }`
  },
  java: {
    filename: "OrderController.java",
    language: "java",
    code: `package com.security.platform;\n\npublic class OrderController {\n    public static void main(String[] args) {\n        System.out.println("Processing secure order payload");\n    }\n}`
  },
  javascript: {
    filename: "auth_middleware.js",
    language: "javascript",
    code: `const crypto = require('crypto');\n\nfunction verifySignature(payload, signature, secret) {\n    const hash = crypto.createHmac('sha256', secret).update(payload).digest('hex');\n    return hash === signature;\n}`
  },
  typescript: {
    filename: "user_repository.ts",
    language: "typescript",
    code: `export interface UserProfile {\n    id: string;\n    username: string;\n    role: 'admin' | 'developer' | 'auditor';\n}\n\nexport const fetchProfile = (id: string): UserProfile => ({\n    id,\n    username: 'sec_dev',\n    role: 'developer'\n});`
  }
};

export default function CodeIngestionCard() {
  const [activeTab, setActiveTab] = useState('paste'); // 'paste' | 'upload'
  const [language, setLanguage] = useState('');
  const [filename, setFilename] = useState('payment_service.py');
  const [content, setContent] = useState(SAMPLE_SNIPPETS.python.code);
  const [selectedFile, setSelectedFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleLoadSample = (sampleKey) => {
    const sample = SAMPLE_SNIPPETS[sampleKey];
    setLanguage(sample.language);
    setFilename(sample.filename);
    setContent(sample.code);
    setError(null);
  };

  const handlePasteSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) {
      setError("Please provide source code content before submitting.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const res = await submitCode({
      language: language || undefined,
      filename: filename || undefined,
      content
    });

    if (res.success) {
      setResult(res.data);
    } else {
      setError(res.error);
    }
    setLoading(false);
  };

  const handleFileUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select a file to upload (.py, .java, .js, .jsx, .ts, .tsx).");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const res = await uploadCodeFile(selectedFile, language || undefined);

    if (res.success) {
      setResult(res.data);
    } else {
      setError(res.error);
    }
    setLoading(false);
  };

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '8px',
            borderRadius: '8px',
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)'
          }}>
            <FileCode2 size={20} color="#10b981" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>Secure Code Ingestion Layer</h2>
              <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>MODULE 2 ACTIVE</span>
            </div>
            <p style={{ fontSize: '0.8rem' }}>Safe code ingestion with path traversal defense, file validation, and zero execution</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.04)', borderRadius: '8px', padding: '4px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => { setActiveTab('paste'); setError(null); }}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              background: activeTab === 'paste' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
              color: activeTab === 'paste' ? '#10b981' : '#94a3b8',
              transition: 'all 0.2s'
            }}
          >
            Paste Source Code
          </button>
          <button
            onClick={() => { setActiveTab('upload'); setError(null); }}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              background: activeTab === 'upload' ? 'rgba(6, 182, 212, 0.2)' : 'transparent',
              color: activeTab === 'upload' ? '#06b6d4' : '#94a3b8',
              transition: 'all 0.2s'
            }}
          >
            Upload File
          </button>
        </div>
      </div>

      {/* Safety Notice */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: 'rgba(16, 185, 129, 0.04)',
        border: '1px solid rgba(16, 185, 129, 0.2)',
        borderRadius: '8px',
        padding: '10px 14px',
        marginBottom: '18px',
        fontSize: '0.78rem',
        color: '#94a3b8'
      }}>
        <ShieldCheck size={16} color="#10b981" />
        <span>
          <strong>Zero Execution Sandbox:</strong> Uploaded or pasted code is treated strictly as static text data. It is never imported, compiled, or executed.
        </span>
      </div>

      {/* Tab 1: Paste Code */}
      {activeTab === 'paste' && (
        <form onSubmit={handlePasteSubmit}>
          
          {/* Controls Bar: Language & Filename & Sample Buttons */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '12px' }}>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
              
              {/* Language Selector */}
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.9)',
                    color: '#f8fafc',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '0.8rem',
                    outline: 'none'
                  }}
                >
                  <option value="">Auto-Detect</option>
                  <option value="python">Python (.py)</option>
                  <option value="java">Java (.java)</option>
                  <option value="javascript">JavaScript (.js, .jsx)</option>
                  <option value="typescript">TypeScript (.ts, .tsx)</option>
                </select>
              </div>

              {/* Filename Input */}
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Filename</label>
                <input
                  type="text"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="e.g. payment_service.py"
                  style={{
                    background: 'rgba(15, 23, 42, 0.9)',
                    color: '#f8fafc',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '0.8rem',
                    minWidth: '220px',
                    outline: 'none'
                  }}
                />
              </div>

            </div>

            {/* Quick Sample Presets */}
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Samples:</span>
              <button type="button" onClick={() => handleLoadSample('python')} className="btn btn-outline" style={{ fontSize: '0.7rem', padding: '4px 8px' }}>Python</button>
              <button type="button" onClick={() => handleLoadSample('java')} className="btn btn-outline" style={{ fontSize: '0.7rem', padding: '4px 8px' }}>Java</button>
              <button type="button" onClick={() => handleLoadSample('javascript')} className="btn btn-outline" style={{ fontSize: '0.7rem', padding: '4px 8px' }}>JavaScript</button>
              <button type="button" onClick={() => handleLoadSample('typescript')} className="btn btn-outline" style={{ fontSize: '0.7rem', padding: '4px 8px' }}>TypeScript</button>
            </div>
          </div>

          {/* Code Textarea */}
          <div style={{ position: 'relative', marginBottom: '16px' }}>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your source code here..."
              rows={10}
              style={{
                width: '100%',
                background: 'rgba(9, 13, 22, 0.85)',
                color: '#38bdf8',
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
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
              <span>Lines: {content.split('\n').length} &bull; Characters: {content.length.toLocaleString()}</span>
              <span>Max Limit: 500,000 characters</span>
            </div>
          </div>

          {/* Submit Action */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              id="submit-code-btn"
            >
              {loading ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <ArrowRight size={16} />}
              <span>{loading ? 'Validating Code...' : 'Safely Ingest & Validate Code'}</span>
            </button>
          </div>

        </form>
      )}

      {/* Tab 2: File Upload */}
      {activeTab === 'upload' && (
        <form onSubmit={handleFileUploadSubmit}>
          
          <div style={{ marginBottom: '16px' }}>
            <div style={{
              border: '2px dashed rgba(6, 182, 212, 0.4)',
              borderRadius: '12px',
              padding: '36px 20px',
              textAlign: 'center',
              background: 'rgba(6, 182, 212, 0.02)',
              cursor: 'pointer',
              position: 'relative'
            }}>
              <input
                type="file"
                accept=".py,.java,.js,.jsx,.mjs,.cjs,.ts,.tsx,.mts,.cts"
                onChange={(e) => {
                  if (e.target.files?.[0]) {
                    setSelectedFile(e.target.files[0]);
                    setError(null);
                  }
                }}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  opacity: 0,
                  cursor: 'pointer'
                }}
              />
              <UploadCloud size={42} color="#06b6d4" style={{ margin: '0 auto 10px auto' }} />
              <h3 style={{ fontSize: '1rem', color: '#f8fafc', marginBottom: '4px' }}>
                {selectedFile ? selectedFile.name : 'Drag & Drop your source file here'}
              </h3>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                Supported: <code>.py</code>, <code>.java</code>, <code>.js</code>, <code>.jsx</code>, <code>.ts</code>, <code>.tsx</code> (Max: 2 MB)
              </p>
              {selectedFile && (
                <div style={{ marginTop: '12px' }}>
                  <span className="badge badge-cyan">
                    Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Submit Upload */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button
              type="submit"
              disabled={loading || !selectedFile}
              className="btn btn-primary"
              id="upload-file-btn"
            >
              {loading ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <ArrowRight size={16} />}
              <span>{loading ? 'Uploading & Validating...' : 'Upload & Validate File'}</span>
            </button>
          </div>

        </form>
      )}

      {/* Error Alert */}
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
            <strong>Ingestion Rejected:</strong> {error}
          </div>
        </div>
      )}

      {/* Ingestion Success Metadata Inspector */}
      {result && (
        <div style={{
          marginTop: '20px',
          background: 'rgba(16, 185, 129, 0.03)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '12px',
          padding: '18px',
          boxShadow: '0 0 25px rgba(16, 185, 129, 0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={18} color="#10b981" />
              <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>Source Code Successfully Ingested & Validated</strong>
            </div>
            <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>
              STATUS: {result.status}
            </span>
          </div>

          <div className="grid-2" style={{ gap: '12px', marginBottom: '12px' }}>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              <div>Session ID: <code style={{ color: '#06b6d4' }}>{result.submission_id}</code></div>
              <div>Detected Language: <strong style={{ color: '#f8fafc', textTransform: 'capitalize' }}>{result.language}</strong></div>
              <div>Original Filename: <span style={{ color: '#cbd5e1' }}>{result.filename}</span></div>
              <div>Sanitized Safe Filename: <strong style={{ color: '#10b981' }}>{result.sanitized_filename}</strong></div>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              <div>Line Count: <strong style={{ color: '#f8fafc' }}>{result.line_count} lines</strong></div>
              <div>Character Count: <strong style={{ color: '#f8fafc' }}>{result.character_count.toLocaleString()}</strong></div>
              <div>Payload Size: <strong style={{ color: '#f8fafc' }}>{result.size_bytes.toLocaleString()} bytes</strong></div>
              <div>Timestamp: <span style={{ color: '#cbd5e1' }}>{new Date(result.created_at).toLocaleString()}</span></div>
            </div>
          </div>

          {/* Cryptographic SHA-256 Fingerprint */}
          <div style={{
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '6px',
            padding: '8px 12px',
            fontSize: '0.75rem',
            fontFamily: 'var(--font-mono)',
            color: '#a7f3d0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            wordBreak: 'break-all'
          }}>
            <Hash size={14} color="#10b981" />
            <span>SHA-256: {result.sha256_hash}</span>
          </div>

        </div>
      )}

    </section>
  );
}
