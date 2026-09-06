import React from 'react';
import { Layers, FolderCode, Database, Shield, Cpu, ArrowRight } from 'lucide-react';
import { ARCHITECTURE_LAYERS } from '../utils/constants';

export default function ArchitectureCard() {
  return (
    <section className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{
          padding: '8px',
          borderRadius: '8px',
          background: 'rgba(139, 92, 246, 0.1)',
          border: '1px solid rgba(139, 92, 246, 0.3)'
        }}>
          <Layers size={20} color="#8b5cf6" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.15rem', color: '#ffffff' }}>Modular Monolith Architecture</h2>
          <p style={{ fontSize: '0.8rem' }}>Clean single-deploy architecture without microservices or Kafka overhead</p>
        </div>
      </div>

      {/* Layer Decomposition */}
      <div className="grid-2" style={{ gap: '14px' }}>
        {ARCHITECTURE_LAYERS.map((layer, index) => (
          <div 
            key={index}
            style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '10px',
              padding: '14px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FolderCode size={16} color="#8b5cf6" />
                <strong style={{ fontSize: '0.9rem', color: '#f1f5f9' }}>{layer.name}</strong>
              </div>
              <span className={`badge ${layer.status === 'ACTIVE' ? 'badge-emerald' : 'badge-violet'}`} style={{ fontSize: '0.65rem' }}>
                {layer.status}
              </span>
            </div>
            
            <div style={{ fontSize: '0.75rem', color: '#06b6d4', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
              {layer.module}
            </div>

            <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              {layer.description}
            </p>
          </div>
        ))}
      </div>

    </section>
  );
}
