import React from 'react';
import { Settings, Cpu, Sliders, Activity, ShieldCheck, Database, RefreshCw } from 'lucide-react';
import LocalAIConfigCard from '../LocalAIConfigCard';
import HealthMonitor from '../HealthMonitor';

export default function SettingsView({
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
    <div className="space-y-6">
      {/* Settings Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-gray-900 via-slate-900 to-zinc-900 border border-gray-700/80 shadow-xl flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
              CONFIGURATION & TELEMETRY
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800">
              Module 8 & 11 Controls
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            System Settings & AI Provider Config
          </h2>
          <p className="text-sm text-gray-300 max-w-3xl mt-1">
            Configure AI execution mode (Disabled / External LLM / Private Local LLM), test local Ollama/vLLM endpoints, and manage background health telemetry.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            className="btn btn-outline btn-sm flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Health</span>
          </button>
        </div>
      </div>

      {/* Module 8: Private AI & Local LLM Infrastructure Settings */}
      <LocalAIConfigCard />

      {/* Health & Infrastructure Telemetry Card */}
      <HealthMonitor
        healthData={healthData}
        latency={latency}
        loading={loading}
        error={error}
        lastUpdated={lastUpdated}
        isPolling={isPolling}
        onTogglePolling={onTogglePolling}
        onRefresh={onRefresh}
      />
    </div>
  );
}
