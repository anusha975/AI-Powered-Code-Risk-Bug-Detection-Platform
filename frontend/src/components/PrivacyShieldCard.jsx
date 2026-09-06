import React, { useState } from 'react';
import { ShieldCheck, Lock, EyeOff, Cpu, FileCode2, Info } from 'lucide-react';
import { PRIVACY_PRINCIPLES } from '../utils/constants';

export default function PrivacyShieldCard() {
  const [selectedTag, setSelectedTag] = useState(null);

  const filteredPrinciples = selectedTag 
    ? PRIVACY_PRINCIPLES.filter(p => p.tag === selectedTag)
    : PRIVACY_PRINCIPLES;

  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '8px',
            borderRadius: '8px',
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)'
          }}>
            <ShieldCheck size={20} color="#10b981" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>10 Privacy-Preserving Guardrails</h2>
            <p style={{ fontSize: '0.8rem' }}>Strict architectural guarantees enforced across all analysis pipelines</p>
          </div>
        </div>

        {/* Filter Clear */}
        {selectedTag && (
          <button 
            onClick={() => setSelectedTag(null)}
            className="btn btn-outline"
            style={{ fontSize: '0.75rem', padding: '4px 10px' }}
          >
            Show All Principles ({PRIVACY_PRINCIPLES.length})
          </button>
        )}
      </div>

      {/* Principles List Grid */}
      <div className="grid-2" style={{ gap: '14px' }}>
        {filteredPrinciples.map((item) => (
          <div 
            key={item.id}
            onClick={() => setSelectedTag(selectedTag === item.tag ? null : item.tag)}
            style={{
              background: selectedTag === item.tag ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.02)',
              border: selectedTag === item.tag ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '10px',
              padding: '14px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  color: '#10b981'
                }}>
                  {item.id}
                </span>
                <strong style={{ fontSize: '0.9rem', color: '#f1f5f9' }}>{item.title}</strong>
              </div>
              <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>
                {item.tag}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.4' }}>
              {item.description}
            </p>
          </div>
        ))}
      </div>

      {/* Safety Summary Banner */}
      <div style={{
        marginTop: '16px',
        padding: '12px 16px',
        background: 'rgba(6, 182, 212, 0.05)',
        border: '1px solid rgba(6, 182, 212, 0.2)',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        fontSize: '0.8rem',
        color: '#94a3b8'
      }}>
        <Info size={18} color="#06b6d4" />
        <span>
          <strong>Zero Code Execution Guarantee:</strong> The platform will never invoke <code>eval()</code>, <code>exec()</code>, build scripts, or run unverified GitHub scripts during analysis.
        </span>
      </div>

    </section>
  );
}
