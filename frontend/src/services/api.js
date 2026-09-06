/**
 * API Service Client for the Privacy-Preserving Security Platform.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/+$/, '')}/api`
  : '/api';

/**
 * Fetch live system health status and telemetry from backend.
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchHealth() {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errorText = await response.text();
      return {
        success: false,
        latencyMs,
        error: `Server responded with HTTP ${response.status}: ${errorText || response.statusText}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Network request failed. Is the FastAPI backend running?',
    };
  }
}

/**
 * Submit pasted source code for safe ingestion and validation.
 * @param {{ language?: string, filename?: string, content: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function submitCode(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/code/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to submit code for ingestion.',
    };
  }
}

/**
 * Upload a source code file for safe ingestion.
 * @param {File} file
 * @param {string} [language]
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function uploadCodeFile(file, language = '') {
  const startTime = performance.now();
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (language) {
      formData.append('language', language);
    }

    const response = await fetch(`${API_BASE_URL}/code/upload`, {
      method: 'POST',
      body: formData,
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to upload code file.',
    };
  }
}

/**
 * Scan source code for secrets and apply privacy-preserving redaction.
 * @param {{ language?: string, filename?: string, content: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function scanAndRedactSecrets(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/security/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to execute secret scan.',
    };
  }
}

/**
 * Execute local static code analysis (Python AST + Bandit).
 * @param {{ language?: string, filename?: string, content: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function runStaticAnalysis(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/analysis/static`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to run static code analysis.',
    };
  }
}

/**
 * Calculate Code Risk Score using Scikit-learn ML regression & deterministic heuristics.
 * @param {{ language?: string, filename?: string, content: string, findings?: any[], secrets_count?: number }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function calculateRiskScore(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/risk/score`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to calculate risk score.',
    };
  }
}

/**
 * Execute Privacy-Preserving AI Code Analysis (Module 6).
 * @param {{ language?: string, filename?: string, content: string, ai_enabled?: boolean }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function runAIAnalysis(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/ai/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to run privacy-aware AI analysis.',
    };
  }
}

/**
 * Retrieve recent privacy audit telemetry logs.
 * @param {number} [limit=20]
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchAIAuditLogs(limit = 20) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/ai/audit?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      return {
        success: false,
        latencyMs,
        error: `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to retrieve AI audit logs.',
    };
  }
}

/**
 * Generate Tripartite Developer Remediation Explanations (Module 7).
 * @param {{ language?: string, filename?: string, content: string, max_explanations?: number, provider_override?: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function generateDeveloperRemediation(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/remediation/explain`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to generate developer remediation explanations.',
    };
  }
}

/**
 * Fetch AI Providers Catalog & Health Status (Module 8).
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchAIProviders() {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/ai/providers`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to fetch AI providers catalog.',
    };
  }
}

/**
 * Test AI Provider Connectivity on demand (Module 8).
 * @param {{ provider_type: string, api_url?: string, model_name?: string, api_type?: string, api_key?: string, timeout_seconds?: number }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function testAIProviderConnection(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/ai/providers/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to test provider connection.',
    };
  }
}

/**
 * Fetch All Indexed Knowledge Documents (Module 9 RAG).
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchRAGDocuments() {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/rag/documents`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to fetch knowledge documents.',
    };
  }
}

/**
 * Execute Grounded RAG Query with AI Explanation (Module 9).
 * @param {{ query: string, top_k?: number, similarity_threshold?: number, source_type_filter?: string, provider_override?: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function queryRAG(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/rag/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to execute RAG query.',
    };
  }
}

/**
 * Execute Semantic Vector Similarity Search (Module 9).
 * @param {{ query: string, top_k?: number, similarity_threshold?: number, source_type_filter?: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function searchRAG(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/rag/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to execute semantic search.',
    };
  }
}

/**
 * Index a new Engineering Knowledge Document (Module 9).
 * @param {{ title: string, source_type: string, content: string, author?: string, tags?: string[], doc_id?: string }} payload
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function indexRAGDocument(payload) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/rag/documents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to index document.',
    };
  }
}

/**
 * Validate and Parse a GitHub Pull Request URL (Module 10).
 * @param {string} prUrl
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function parseGitHubPRUrl(prUrl) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/github/pr/parse-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ pr_url: prUrl }),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to parse GitHub PR URL.',
    };
  }
}

/**
 * Execute full Security and Risk Analysis on a GitHub Pull Request (Module 10).
 * @param {{ pr_url?: string, owner?: string, repo?: string, pull_number?: number, analysis_mode?: string, provider_override?: string, enable_rag?: boolean, max_files?: number }} payload
 * @param {string} [token] - Optional GitHub Personal Access Token (PAT)
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function analyzeGitHubPR(payload, token = '') {
  const startTime = performance.now();
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (token && token.trim()) {
      headers['X-GitHub-Token'] = token.trim();
    }

    const response = await fetch(`${API_BASE_URL}/github/pr/analyze`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        latencyMs,
        error: errJson.detail || `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to analyze GitHub Pull Request.',
    };
  }
}

/**
 * Fetch Live Dashboard Executive Telemetry & Overview Metrics (Module 11).
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchDashboardOverview() {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/overview`);
    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      return {
        success: false,
        latencyMs,
        error: `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to fetch dashboard overview.',
    };
  }
}

/**
 * Fetch Filtered Analysis History Logs (Module 11).
 * @param {{ analysis_type?: string, risk_level?: string, limit?: number, offset?: number }} [params]
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchAnalysisHistory(params = {}) {
  const startTime = performance.now();
  try {
    const query = new URLSearchParams();
    if (params.analysis_type) query.append('analysis_type', params.analysis_type);
    if (params.risk_level) query.append('risk_level', params.risk_level);
    if (params.limit) query.append('limit', String(params.limit));
    if (params.offset) query.append('offset', String(params.offset));

    const response = await fetch(`${API_BASE_URL}/analytics/history?${query.toString()}`);
    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      return {
        success: false,
        latencyMs,
        error: `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to fetch analysis history.',
    };
  }
}

/**
 * Fetch Deep-Dive Analysis Session Details by UUID (Module 11).
 * @param {string} analysisId
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchAnalysisDetail(analysisId) {
  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/history/${encodeURIComponent(analysisId)}`);
    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      return {
        success: false,
        latencyMs,
        error: response.status === 404 ? 'Analysis session not found' : `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to fetch analysis details.',
    };
  }
}

/**
 * Search and Filter Universal Findings Catalog (Module 11).
 * @param {{ severity?: string, category?: string, search?: string, limit?: number, offset?: number }} [params]
 * @returns {Promise<{success: boolean, data?: any, latencyMs?: number, error?: string}>}
 */
export async function fetchAggregatedFindings(params = {}) {
  const startTime = performance.now();
  try {
    const query = new URLSearchParams();
    if (params.severity) query.append('severity', params.severity);
    if (params.category) query.append('category', params.category);
    if (params.search) query.append('search', params.search);
    if (params.limit) query.append('limit', String(params.limit));
    if (params.offset) query.append('offset', String(params.offset));

    const response = await fetch(`${API_BASE_URL}/analytics/findings?${query.toString()}`);
    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      return {
        success: false,
        latencyMs,
        error: `HTTP Error ${response.status}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      latencyMs,
      data,
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      success: false,
      latencyMs,
      error: err instanceof Error ? err.message : 'Failed to fetch findings catalog.',
    };
  }
}




