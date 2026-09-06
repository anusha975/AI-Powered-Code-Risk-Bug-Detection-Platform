import React from 'react';
import { Shield, Lock, EyeOff, FileCheck2, Cpu, Database, CheckCircle2 } from 'lucide-react';
import PrivacyShieldCard from '../PrivacyShieldCard';
import SecretRedactorPlayground from '../SecretRedactorPlayground';
import ArchitectureCard from '../ArchitectureCard';
import ModuleRoadmap from '../ModuleRoadmap';

export default function SecurityPrivacyView() {
  return (
    <div className="space-y-6">
      {/* Security & Privacy Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-cyan-950/50 via-gray-900 to-emerald-950/50 border border-cyan-800/60 shadow-xl flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded bg-cyan-900/80 text-cyan-300 border border-cyan-700">
              PRIVACY ASSURANCE ENGINE
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800">
              10 Strict Inviolable Rules
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            Security, Privacy & Architectural Guardrails
          </h2>
          <p className="text-sm text-gray-300 max-w-3xl mt-1">
            Review the immutable zero-trust architecture, interactive Shannon entropy secret redaction playground, and verified compliance proofs guaranteeing no proprietary source code leaves perimeter boundary.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-gray-950/80 p-3 rounded-xl border border-gray-800">
          <div className="p-2 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-800">
            <EyeOff className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-gray-200">Zero Raw Secrets In Logs</div>
            <div className="text-[11px] text-gray-400">Strict one-way masking pipeline</div>
          </div>
        </div>
      </div>

      {/* 10 Inviolable Privacy Guardrails */}
      <PrivacyShieldCard />

      {/* Module 3 Secret Detection & Privacy Protection Playground */}
      <SecretRedactorPlayground />

      {/* Modular Monolith Architecture Explorer */}
      <ArchitectureCard />

      {/* System Engineering Roadmap */}
      <ModuleRoadmap />
    </div>
  );
}
