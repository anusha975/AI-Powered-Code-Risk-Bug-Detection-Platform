import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Lock, 
  EyeOff, 
  Key, 
  CheckCircle2, 
  AlertTriangle, 
  Terminal, 
  RefreshCw, 
  FileCode2,
  Sparkles,
  ArrowRight,
  Database,
  Hash
} from 'lucide-react';
import { scanAndRedactSecrets } from '../services/api';

const PRESET_SECRET_SAMPLES = {
  aws: {
    title: "AWS & S3 Credentials",
    filename: "s3_uploader.py",
    language: "python",
    code: `import boto3

# Sensitive Cloud Keys
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def upload_to_s3(bucket: str, file_path: str):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    return s3.upload_file(file_path, bucket, 'remote.dat')`
  },
  database: {
    title: "PostgreSQL URI with Password",
    filename: "database_config.py",
    language: "python",
    code: `from sqlalchemy import create_engine

# High Risk Database Connection String
DATABASE_URI = "postgresql://postgres:SuperSecretP@ssw0rd99!@db.prod.internal:5432/finance_db"
engine = create_engine(DATABASE_URI)

def get_connection():
    return engine.connect()`
  },
  jwt: {
    title: "OpenAI Key & JWT Token",
    filename: "auth_service.js",
    language: "javascript",
    code: `const jwt = require('jsonwebtoken');

// SaaS and Bearer Credentials
const OPENAI_API_KEY = "sk-proj-abc123456789012345678901234567890123456789012345";
const AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

function authenticateUser(req) {
    return jwt.verify(AUTH_TOKEN, 'app_secret');
}`
  },
  private_key: {
    title: "RSA Private Key Block",
    filename: "crypto_service.py",
    language: "python",
    code: `SERVER_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Y3y1AbcDefGhIjKlMnOpQrStUvWxYz01234567890
-----END RSA PRIVATE KEY-----"""

def sign_payload(data: str):
    # Uses private key for digital signature
    return True`
  },
  multi: {
    title: "Multi-Secret Cloud Service",
    filename: "cloud_service.py",
    language: "python",
    code: `import os

# Multiple Credential Types
AWS_KEY = "AKIA1234567890ABCDEF"
GITHUB_PAT = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
STRIPE_SECRET = "sk_test_51MockDemoKey00000000000000000000"
DB_URL = "mysql://admin:P@ssword2026!@prod-db.internal:3306/users"

def execute():
    pass`
  },
  clean: {
    title: "Clean Code (No Secrets)",
    filename: "math_utils.py",
    language: "python",
    code: `def calculate_hypotenuse(a: float, b: float) -> float:
    """Calculate hypotenuse of right triangle."""
    return (a**2 + b**2) ** 0.5

class GeometryHelper:
    def circle_area(self, radius: float) -> float:
        return 3.14159 * (radius ** 2)`
  }
};

export default function SecretRedactorPlayground() {
  const [selectedPreset, setSelectedPreset] = useState('aws');
  const [filename, setFilename] = useState(PRESET_SECRET_SAMPLES.aws.filename);
  const [content, setContent] = useState(PRESET_SECRET_SAMPLES.aws.code);
  const [viewTab, setViewTab] = useState('sanitized'); // 'sanitized' | 'original' | 'diff'

  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSelectPreset = (key) => {
    const sample = PRESET_SECRET_SAMPLES[key];
    setSelectedPreset(key);
    setFilename(sample.filename);
    setContent(sample.code);
    setError(null);
    setScanResult(null);
  };

  const handleScanAndRedact = async (e) => {
    e.preventDefault();
    if (!content.trim()) {
      setError("Please provide source code to scan.");
      return;
    }

    setLoading(true);
    setError(null);

    const res = await scanAndRedactSecrets({
      filename,
      content
    });

    if (res.success) {
      setScanResult(res.data);
    } else {
      setError(res.error);
    }
    setLoading(false);
  };

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '8px',
            borderRadius: '8px',
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)'
          }}>
            <ShieldAlert size={20} color="#f59e0b" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>Secret Detection &amp; Privacy Protection Engine</h2>
              <span className="badge badge-amber" style={{ fontSize: '0.65rem' }}>MODULE 3 ACTIVE</span>
            </div>
            <p style={{ fontSize: '0.8rem' }}>Multi-pass entropy &amp; pattern scanner &bull; Automatic zero-leak placeholder redaction</p>
          </div>
        </div>

        {/* Security Badge */}
        <div className="badge badge-emerald" style={{ padding: '6px 12px' }}>
          <Lock size={12} />
          <span>Zero Secret Leakage Guarantee</span>
        </div>
      </div>

      {/* Preset Buttons */}
      <div style={{ marginBottom: '16px' }}>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>
          Load Test Scenarios:
        </span>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {Object.entries(PRESET_SECRET_SAMPLES).map(([key, sample]) => (
            <button
              key={key}
              type="button"
              onClick={() => handleSelectPreset(key)}
              className="btn btn-outline"
              style={{
                fontSize: '0.75rem',
                padding: '5px 10px',
                borderColor: selectedPreset === key ? 'rgba(245, 158, 11, 0.5)' : 'var(--border-subtle)',
                background: selectedPreset === key ? 'rgba(245, 158, 11, 0.1)' : 'rgba(255, 255, 255, 0.02)',
                color: selectedPreset === key ? '#f59e0b' : '#94a3b8'
              }}
            >
              {sample.title}
            </button>
          ))}
        </div>
      </div>

      {/* Code Input & Editor Form */}
      <form onSubmit={handleScanAndRedact} style={{ marginBottom: '20px' }}>
        <div style={{ position: 'relative', marginBottom: '12px' }}>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={8}
            placeholder="Paste code containing credentials or secrets..."
            style={{
              width: '100%',
              background: 'rgba(9, 13, 22, 0.9)',
              color: '#fde047',
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

        {/* Scan & Redact Button */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            Targets: AWS, GitHub, Stripe, OpenAI, JWT, DB URIs, Private Keys, Passwords, High-Entropy Strings
          </span>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: '#451a03',
              boxShadow: '0 4px 14px rgba(245, 158, 11, 0.3)'
            }}
            id="scan-secrets-btn"
          >
            {loading ? <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <EyeOff size={16} />}
            <span>{loading ? 'Scanning & Redacting...' : 'Scan & Redact Secrets'}</span>
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

      {/* Scan Results & Redaction View */}
      {scanResult && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '12px',
          padding: '18px',
          boxShadow: '0 0 30px rgba(245, 158, 11, 0.08)'
        }}>
          
          {/* Results Summary Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <CheckCircle2 size={20} color="#10b981" />
              <div>
                <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>
                  Privacy Sanitization Completed
                </strong>
                <span style={{ display: 'block', fontSize: '0.75rem', color: '#94a3b8' }}>
                  Scan ID: <code>{scanResult.scan_id}</code>
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <span className={`badge ${scanResult.secrets_detected_count > 0 ? 'badge-amber' : 'badge-emerald'}`}>
                {scanResult.secrets_detected_count} SECRETS DETECTED &amp; REDACTED
              </span>
            </div>
          </div>

          {/* Findings Table (If any) */}
          {scanResult.findings.length > 0 ? (
            <div style={{ marginBottom: '18px' }}>
              <h4 style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '8px' }}>Detected Secret Findings:</h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8' }}>
                      <th style={{ padding: '8px' }}>Line</th>
                      <th style={{ padding: '8px' }}>Secret Class</th>
                      <th style={{ padding: '8px' }}>Confidence</th>
                      <th style={{ padding: '8px' }}>Status</th>
                      <th style={{ padding: '8px' }}>Substituted Placeholder</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scanResult.findings.map((f, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                        <td style={{ padding: '8px', color: '#f59e0b', fontWeight: 600 }}>Line {f.line_number}</td>
                        <td style={{ padding: '8px', color: '#f8fafc' }}>
                          <span className="badge badge-amber" style={{ fontSize: '0.65rem' }}>{f.secret_type}</span>
                        </td>
                        <td style={{ padding: '8px', color: '#10b981' }}>{f.confidence}</td>
                        <td style={{ padding: '8px' }}>
                          <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>{f.redaction_status}</span>
                        </td>
                        <td style={{ padding: '8px', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                          <code>{f.placeholder}</code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div style={{
              padding: '10px 14px',
              background: 'rgba(16, 185, 129, 0.05)',
              border: '1px solid rgba(16, 185, 129, 0.2)',
              borderRadius: '8px',
              fontSize: '0.8rem',
              color: '#a7f3d0',
              marginBottom: '16px'
            }}>
              Clean Source Code: No sensitive credentials or high-entropy tokens detected.
            </div>
          )}

          {/* Sanitized Code Viewer */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 600 }}>
                Sanitized Source Code (Safe for AI Processing):
              </span>
              <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
                All secret occurrences masked with placeholders
              </span>
            </div>
            
            <pre style={{
              background: 'rgba(9, 13, 22, 0.9)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '8px',
              padding: '14px',
              color: '#34d399',
              fontSize: '0.82rem',
              lineHeight: '1.5',
              overflowX: 'auto',
              maxHeight: '260px'
            }}>
              <code>{scanResult.sanitized_content}</code>
            </pre>
          </div>

          {/* Privacy Proof Banner */}
          <div style={{
            marginTop: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.75rem',
            color: '#94a3b8'
          }}>
            <Lock size={14} color="#10b981" />
            <span>
              <strong>Zero Leakage Verified:</strong> Raw secrets were completely expunged during the redaction phase and do not exist in this payload.
            </span>
          </div>

        </div>
      )}

    </section>
  );
}
