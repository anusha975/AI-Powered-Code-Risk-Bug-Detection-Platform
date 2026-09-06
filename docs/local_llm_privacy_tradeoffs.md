# Private AI & Local LLM Privacy Tradeoffs & Architecture Specification

## 1. Executive Summary

Modern enterprise code security demands rigorous privacy protections. Proprietary source code contains sensitive business logic, algorithmic secrets, intellectual property, and architectural topologies. Transmitting raw source code or entire git repositories to third-party multi-tenant cloud AI vendors introduces severe compliance and security risks (including data retention, training leakage, unauthorized access, and cross-tenant exfiltration).

**Module 8: Private AI / Local LLM Support** provides an architectural abstraction enabling organizations to operate in two primary deployment modes alongside a deterministic offline baseline:
1. **Mode 1: External Cloud LLM** (Cloud TLS API e.g. OpenAI / Azure OpenAI with strict Secret Redaction & Context Window Minimization)
2. **Mode 2: Private / Local LLM** (On-premise / Air-gapped Host e.g. Ollama, vLLM, llama.cpp, LocalAI with **Zero External Egress**)
3. **Baseline: No-AI Local Static Mode** (100% Offline AST & Bandit SAST with Zero Model Invocations)

---

## 2. Architectural Comparison Matrix

| Dimension | Mode 1: External Cloud LLM | Mode 2: Private / Local LLM | Mode 3: No-AI Local Static |
|---|---|---|---|
| **Data Boundary** | External Cloud (TLS in transit) | **Internal Host / Intranet LAN** | **100% Local Machine** |
| **External Network Egress** | Yes (strictly sanitized $\pm 4$ line window) | **Zero (0 bytes egress)** | **Zero (0 bytes egress)** |
| **API Key Requirement** | Mandatory vendor API key | **None (No external key required)** | **None** |
| **Air-Gapped Operation** | Unsupported | **100% Air-Gapped Supported** | **100% Air-Gapped Supported** |
| **Secret Protection** | Pre-redacted as `[REDACTED_<TYPE>]` | Pre-redacted before local model ingestion | Pre-redacted at AST level |
| **Reasoning Capacity** | High (State-of-the-art multi-billion parameter models) | Moderate-High (Quantized 1B–70B open-weights) | Deterministic rule-based only |
| **Operational Hardware** | Minimal (Standard CPU) | **Requires Dedicated GPU / RAM** | Minimal (Standard CPU) |
| **Inference Latency** | Network + Queue (500ms – 2500ms) | Local Compute (100ms – 1500ms on GPU) | **Instantaneous (< 10ms)** |
| **Third-Party Data Retention Risk** | Dependent on vendor DPA / enterprise tier | **Zero vendor retention risk** | **Zero vendor retention risk** |
| **Cost Model** | Pay-per-token API fees | Fixed hardware capital / electricity | Zero compute cost |

---

## 3. Privacy & Security Tradeoffs

### A. Mode 1: External Cloud LLM
- **Strengths**:
  - Highest reasoning capability and nuanced understanding of complex multi-line flaws.
  - Zero local hardware infrastructure overhead (runs on standard commodity server or developer laptop).
  - Immediate availability of latest model weights without local download or maintenance.
- **Privacy & Security Risks**:
  - Requires internet access and external network egress.
  - Organization must trust the cloud vendor's data processing agreement (DPA) regarding non-training policies and retention periods.
  - Sensitive snippet structure (though redacted and isolated to $\pm 4$ lines) exits the company perimeter.
- **Platform Mitigations**:
  - **Module 3 Invariant**: High-entropy strings, AWS/OpenAI/GitHub keys, DB URIs, and JWTs are redacted *before* payload synthesis.
  - **Module 6 Invariant**: Context window is strictly bounded ($\pm 4$ lines around flagged line numbers). Unreferenced files are never sent.

### B. Mode 2: Private / Local LLM (Air-Gapped)
- **Strengths**:
  - **Zero Data Egress Guarantee**: Code snippets, identifiers, and comments never leave the local machine or enterprise virtual private cloud (VPC).
  - Works seamlessly in fully air-gapped defense, financial, or healthcare environments with disconnected networks.
  - Immune to third-party vendor outages, rate limits, pricing tier changes, or terms of service updates.
- **Tradeoffs**:
  - Reasoning capacity is constrained by available hardware (a quantized 1B–7B model may produce simpler refactor suggestions than a frontier 400B cloud model).
  - Infrastructure maintenance overhead (managing model weights, GPU drivers, CUDA runtimes, server updates).

---

## 4. Inviolable Security Disclaimer: Local LLM Infrastructure Responsibility

> [!CAUTION]
> **A local or self-hosted LLM is NOT automatically secure.**
> Eliminating cloud transit eliminates external vendor exposure, but the hosting organization remains fully responsible for securing its local host and network environment.

Organizations deploying Mode 2 must enforce the following security controls:

1. **Host & Network Segmentation**:
   - Local LLM servers (e.g. Ollama on port `11434` or vLLM on port `8000`) should bind strictly to `127.0.0.1` (localhost) or an isolated, firewall-restricted internal management subnet.
   - Never expose unauthenticated local LLM server ports to public networks or untrusted company subnets.

2. **Model Weight Integrity & Supply Chain Provenance**:
   - Verify cryptographic checksums (SHA-256) of all downloaded GGUF/Safetensors model weights.
   - Download model weights strictly from verified, official vendor repositories (e.g. Meta, Qwen, DeepSeek official HuggingFace / Ollama registries).
   - Beware of unverified third-party fine-tunes that could contain backdoored weights or trojans.

3. **Prompt Injection & Execution Isolation**:
   - The platform strictly treats LLM responses as inert text strings and never executes generated code or command strings.
   - Local model output is parsed through the **Module 7 Response Validator** before being displayed to developers.

4. **Resource Quotas & Denial of Service (DoS) Hardening**:
   - Configure local inference engines with memory limits and concurrency bounds to prevent large prompt batches from exhausting host VRAM and triggering out-of-memory (OOM) kernel panics.

---

## 5. Supported Local Inference Engines & Connection Protocols

The platform's `LocalLLMProvider` dynamically supports the two predominant industry protocols:

### 1. Ollama Native Protocol (`LOCAL_LLM_API_TYPE=ollama`)
- Endpoint: `http://127.0.0.1:11434/api/generate` and `/api/tags`
- Supported Models:
  - `llama3.2:1b` / `llama3.2:3b` (Ultra-fast, low VRAM ~1.5–3 GB)
  - `qwen2.5-coder:7b` (Exceptional code reasoning, ~5 GB VRAM)
  - `deepseek-coder:6.7b` (Strong application security analysis, ~4.5 GB VRAM)
  - `codellama:7b` / `codellama:13b` (Meta's code security baseline)

### 2. OpenAI-Compatible Local Protocol (`LOCAL_LLM_API_TYPE=openai_compatible`)
- Endpoint: `http://127.0.0.1:8000/v1/chat/completions` and `/v1/models`
- Compatible Servers:
  - **vLLM** (High-throughput batched inference server)
  - **llama.cpp server** (`./server -m model.gguf --port 8080`)
  - **LocalAI** (Self-hosted OpenAI-compatible drop-in container)
  - **LM Studio / text-generation-webui**

---

## 6. Resilience & Graceful Fallback Guarantee

The platform guarantees uninterrupted workflow execution regardless of network or AI availability:

```
                  ┌────────────────────────────────────────┐
                  │ Is AI_ENABLED=true and Provider Ready? │
                  └───────────────────┬────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼ YES                     ▼ NO (Offline / Down)
              ┌─────────────────────┐   ┌──────────────────────────────┐
              │ Run Minimized LLM   │   │ Graceful Fallback:           │
              │ Pipeline            │   │ Return AST Findings, Risk    │
              │ (Local or Cloud)    │   │ Scores, & Offline Heuristic  │
              └─────────────────────┘   └──────────────────────────────┘
```

1. **No API Key Configured**: Static analysis, secret scanning, and ML risk scoring operate with 100% fidelity.
2. **Local Model Server Offline**: `LocalLLMProvider` catches connection refusals and returns safe offline heuristic explanations with diagnostic notices without raising uncaught exceptions.
3. **AI Disabled (`AI_ENABLED=false`)**: System returns clean static diagnostics with `AIStatus.AI_DISABLED`.
