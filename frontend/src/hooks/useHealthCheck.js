import { useState, useEffect, useCallback } from 'react';
import { fetchHealth } from '../services/api';

/**
 * Custom React hook for live health check and telemetry monitoring.
 * @param {number} pollIntervalMs Polling interval in milliseconds (default: 5000ms)
 */
export function useHealthCheck(pollIntervalMs = 5000) {
  const [healthData, setHealthData] = useState(null);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isPolling, setIsPolling] = useState(true);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    const result = await fetchHealth();
    
    if (result.success) {
      setHealthData(result.data);
      setLatency(result.latencyMs);
      setError(null);
    } else {
      setError(result.error);
      setLatency(result.latencyMs);
    }

    setLastUpdated(new Date());
    setLoading(false);
  }, []);

  useEffect(() => {
    // Initial fetch
    checkHealth();

    if (!isPolling) return;

    const interval = setInterval(() => {
      checkHealth();
    }, pollIntervalMs);

    return () => clearInterval(interval);
  }, [checkHealth, isPolling, pollIntervalMs]);

  return {
    healthData,
    latency,
    loading,
    error,
    lastUpdated,
    isPolling,
    setIsPolling,
    refetch: checkHealth,
  };
}
