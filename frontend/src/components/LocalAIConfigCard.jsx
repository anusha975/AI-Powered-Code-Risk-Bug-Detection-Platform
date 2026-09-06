import React, { useState, useEffect } from 'react';
import {
  Server,
  ShieldCheck,
  Cpu,
  Globe,
  Lock,
  Zap,
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sliders,
  Layers,
  HardDrive,
  Info,
  Radio,
  Terminal,
  ExternalLink,
  ShieldAlert
} from 'lucide-react';
import { fetchAIProviders, testAIProviderConnection } from '../services/api';

const LOCAL_MODEL_PRESETS = [
  { id: 'llama3.2:1b', name: 'Llama 3.2 (1B)', tag: 'Ultra-Fast • Low VRAM (~1.5 GB)', protocol: 'ollama' },
  { id: 'qwen2.5-coder:7b', name: 'Qwen 2.5 Coder (7B)', tag: 'High Accuracy • Code Security (~5 GB VRAM)', protocol: 'ollama' },
  { id: 'deepseek-coder:6.7b', name: 'DeepSeek Coder (6.7B)', tag: 'AppSec Flaw Detection (~4.5 GB VRAM)', protocol: 'ollama' },
  { id: 'codellama:7b', name: 'CodeLlama (7B)', tag: 'Meta Code Security (~5 GB VRAM)', protocol: 'ollama' },
  { id: 'vllm-local', name: 'vLLM Local Server', tag: 'OpenAI-Compatible (/v1/chat/completions)', protocol: 'openai_compatible' }
];

export default function LocalAIConfigCard() {
  const [catalog, setCatalog] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Connection Tester State
  const [selectedMode, setSelectedMode] = useState('local'); // 'local', 'external', 'mock'
  const [customUrl, setCustomUrl] = useState('http://127.0.0.1:11434');
  const [selectedModel, setSelectedModel] = useState(LOCAL_MODEL_PRESETS[0].id);
  const [apiType, setApiType] = useState('ollama'); // 'ollama', 'openai_compatible'
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [showTradeoffs, setShowTradeoffs] = useState(false);

  const loadProviders = async () => {
    setLoading(true);
    setError(null);
    const res = await fetchAIProviders();
    setLoading(false);

    if (res.success && res.data) {
      setCatalog(res.data);
      if (res.data.active_provider) {
        setSelectedMode(res.data.active_provider);
      }
    } else {
      setError(res.error || 'Failed to query provider health.');
    }
  };

  useEffect(() => {
    loadProviders();
  }, []);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);

    const payload = {
      provider_type: selectedMode,
      api_url: selectedMode === 'local' ? customUrl : undefined,
      model_name: selectedMode === 'local' ? selectedModel : undefined,
      api_type: selectedMode === 'local' ? apiType : undefined,
      timeout_seconds: 4
    };

    const res = await testAIProviderConnection(payload);
    setTesting(false);

    if (res.success && res.data) {
      setTestResult(res.data);
    } else {
      setTestResult({
        success: false,
        status: 'ERROR',
        message: res.error || 'Connection attempt failed.',
        latency_ms: 0,
        air_gapped: selectedMode === 'local'
      });
    }
  };

  const handleModelPresetSelect = (preset) => {
    setSelectedModel(preset.id);
    setApiType(preset.protocol);
    if (preset.protocol === 'openai_compatible') {
      setCustomUrl('http://127.0.0.1:8000/v1');
    } else {
      setCustomUrl('http://127.0.0.1:11434');
    }
    setTestResult(null);
  };

  return (
    <div className="card glass-effect relative overflow-hidden border border-slate-700/60 p-6 md:p-8 space-y-6">
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-600/20 border border-emerald-500/30 text-emerald-400 shadow-inner">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-slate-100">
                Private AI &amp; Local LLM Infrastructure
              </h2>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Module 8 (Active)
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Multi-Mode Provider Layer &bull; Zero external egress with local Ollama, vLLM, or air-gapped intranet models
            </p>
          </div>
        </div>

        {/* Refresh Status */}
        <button
          onClick={loadProviders}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl text-xs font-semibold border border-slate-700 bg-slate-900/60 text-slate-300 hover:bg-slate-800 flex items-center gap-1.5 transition-all cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : 'text-slate-400'}`} />
          <span>Refresh Health</span>
        </button>
      </div>

      {/* 3 Deployment Mode Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {/* Mode 1: Local / Air-Gapped */}
        <div
          onClick={() => setSelectedMode('local')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer relative ${
            selectedMode === 'local'
              ? 'bg-emerald-950/30 border-emerald-500/50 shadow-lg shadow-emerald-500/10'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Mode 2: Private / Local LLM</span>
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              100% Air-Gapped
            </span>
          </div>
          <h3 className="font-bold text-slate-200 text-sm">Self-Hosted Intranet</h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Zero bytes egress. Queries local Ollama, vLLM, or llama.cpp process directly on host or corporate LAN.
          </p>
          <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Egress: 0 bytes</span>
            <span className="text-emerald-400 font-semibold">Privacy: 100/100</span>
          </div>
        </div>

        {/* Mode 2: External Cloud TLS */}
        <div
          onClick={() => setSelectedMode('external')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer relative ${
            selectedMode === 'external'
              ? 'bg-indigo-950/30 border-indigo-500/50 shadow-lg shadow-indigo-500/10'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-indigo-400" />
              <span>Mode 1: External Cloud LLM</span>
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Redacted &plusmn;4 Lines
            </span>
          </div>
          <h3 className="font-bold text-slate-200 text-sm">Cloud TLS Provider</h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Sends isolated snippets with masked secrets over TLS to OpenAI or cloud endpoints. Highest reasoning capacity.
          </p>
          <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Requires API Key</span>
            <span className="text-indigo-400 font-semibold">Privacy: 50/100</span>
          </div>
        </div>

        {/* Mode 3: Offline Mock / No-AI */}
        <div
          onClick={() => setSelectedMode('mock')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer relative ${
            selectedMode === 'mock'
              ? 'bg-cyan-950/30 border-cyan-500/50 shadow-lg shadow-cyan-500/10'
              : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
              <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
              <span>Baseline: Offline Mock / No-AI</span>
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Deterministic
            </span>
          </div>
          <h3 className="font-bold text-slate-200 text-sm">Deterministic Engine</h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Zero external hardware or runtime needed. Static AST visitor and ML risk scoring remain 100% active.
          </p>
          <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Zero Compute Latency</span>
            <span className="text-cyan-400 font-semibold">Privacy: 100/100</span>
          </div>
        </div>
      </div>

      {/* Local Provider Configuration & Connection Tester */}
      <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800/80 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-emerald-400" />
            <h3 className="font-bold text-slate-200 text-sm">
              Live Provider Endpoint Tester &amp; Model Probe
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            Targeting: <strong className="text-emerald-300">{selectedMode.toUpperCase()}</strong>
          </span>
        </div>

        {selectedMode === 'local' && (
          <div className="space-y-4">
            {/* Model Presets */}
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Recommended Local Models (Ollama / vLLM)
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {LOCAL_MODEL_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => handleModelPresetSelect(preset)}
                    className={`p-2.5 rounded-xl text-left text-xs transition-all border ${
                      selectedModel === preset.id
                        ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                    }`}
                  >
                    <div className="font-semibold text-slate-200">{preset.name}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{preset.tag}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* URL & Protocol Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="md:col-span-2 space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Local Server Base URL
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={customUrl}
                    onChange={(e) => setCustomUrl(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-700/80 text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500"
                    placeholder="http://127.0.0.1:11434"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Protocol Type
                </label>
                <select
                  value={apiType}
                  onChange={(e) => setApiType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-700/80 text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="ollama">Ollama Native (/api/generate)</option>
                  <option value="openai_compatible">OpenAI-Compatible (/v1/chat/completions)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Action Button & Test Result */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pt-2">
          <button
            onClick={handleTestConnection}
            disabled={testing}
            className="btn-primary flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold shadow-md shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all disabled:opacity-50 cursor-pointer"
          >
            {testing ? (
              <>
                <Activity className="w-4 h-4 animate-spin text-emerald-400" />
                <span>Probing Provider Endpoint...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 text-emerald-400" />
                <span>Test Live Connection &amp; Probe Models</span>
              </>
            )}
          </button>

          {testResult && (
            <div className={`p-3 rounded-xl border text-xs flex items-center gap-2.5 font-mono ${
              testResult.success
                ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
                : 'bg-amber-950/30 border-amber-800 text-amber-300'
            }`}>
              {testResult.success ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              )}
              <div>
                <div className="font-semibold font-sans">{testResult.message}</div>
                <div className="text-[11px] opacity-80 mt-0.5">
                  Latency: {testResult.latency_ms}ms &bull; Status: {testResult.status} &bull; Air-Gapped: {testResult.air_gapped ? 'YES' : 'NO'}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Privacy Tradeoff Inspector Drawer */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/30">
        <button
          onClick={() => setShowTradeoffs(!showTradeoffs)}
          className="w-full p-4 text-xs font-semibold text-slate-300 flex items-center justify-between hover:bg-slate-900/50 transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-emerald-400" />
            <span>Privacy Tradeoffs &amp; Organizational Responsibility Guide</span>
          </div>
          <span className="text-[11px] text-slate-500">
            {showTradeoffs ? 'Hide Privacy Matrix' : 'Inspect Architecture Tradeoffs'}
          </span>
        </button>

        {showTradeoffs && (
          <div className="p-5 border-t border-slate-800/80 bg-slate-950/70 space-y-4 text-xs">
            {/* Disclaimer Alert */}
            <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/40 text-amber-300 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold text-amber-200">Critical Infrastructure Security Responsibility</div>
                <div className="text-[11px] text-amber-300/90 mt-1 leading-relaxed">
                  A local LLM eliminates cloud data transit, but is <strong>NOT automatically secure</strong>.
                  Your organization remains responsible for firewall isolation, local endpoint authentication,
                  safeguarding downloaded model weight provenance (SHA-256), and server host privilege controls.
                </div>
              </div>
            </div>

            {/* Comparison Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse font-sans text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="pb-2 font-semibold">Dimension</th>
                    <th className="pb-2 font-semibold text-emerald-400">Mode 2: Local / Air-Gapped</th>
                    <th className="pb-2 font-semibold text-indigo-400">Mode 1: External Cloud TLS</th>
                    <th className="pb-2 font-semibold text-cyan-400">Mode 3: Offline Heuristic</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
                  <tr>
                    <td className="py-2.5 font-semibold text-slate-400">Data Boundary</td>
                    <td className="py-2.5 font-mono text-emerald-300">Internal Host / LAN</td>
                    <td className="py-2.5 font-mono text-indigo-300">Cloud Provider VPC</td>
                    <td className="py-2.5 font-mono text-cyan-300">100% In-Memory</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 font-semibold text-slate-400">External Egress</td>
                    <td className="py-2.5 text-emerald-400 font-bold">Zero (0 bytes)</td>
                    <td className="py-2.5 text-slate-300">Sanitized &plusmn;4 line window</td>
                    <td className="py-2.5 text-cyan-400 font-bold">Zero (0 bytes)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 font-semibold text-slate-400">API Key Need</td>
                    <td className="py-2.5 text-slate-300">None</td>
                    <td className="py-2.5 text-slate-300">Mandatory Vendor Key</td>
                    <td className="py-2.5 text-slate-300">None</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 font-semibold text-slate-400">Hardware Req</td>
                    <td className="py-2.5 text-slate-300">Dedicated GPU / 8-16 GB RAM</td>
                    <td className="py-2.5 text-slate-300">Standard CPU</td>
                    <td className="py-2.5 text-slate-300">Minimal CPU</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 font-semibold text-slate-400">Offline/Airgap</td>
                    <td className="py-2.5 text-emerald-400 font-bold">100% Supported</td>
                    <td className="py-2.5 text-slate-500">Requires Internet</td>
                    <td className="py-2.5 text-cyan-400 font-bold">100% Supported</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
