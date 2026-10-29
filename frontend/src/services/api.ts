import {
  Top10TrendsResponse,
  Trend,
  TrendObservation,
  AllConnectorsStatus,
  AnalyticsOverview,
  PlatformMetric,
  NemotronPayload,
  NemotronHandoffResponse,
  CollectionJobResponse
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!resp.ok) {
    let errorDetail = `HTTP ${resp.status} ${resp.statusText}`;
    try {
      const errorJson = await resp.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return resp.json();
}

export const api = {
  // Trends
  getTop10Trends: () => fetchJson<Top10TrendsResponse>(`${API_BASE}/trends/top10`),
  
  getTrends: (params?: { category?: string; search?: string; status?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.category) query.set('category', params.category);
    if (params?.search) query.set('search', params.search);
    if (params?.status) query.set('status', params.status);
    if (params?.limit) query.set('limit', String(params.limit));
    return fetchJson<Trend[]>(`${API_BASE}/trends?${query.toString()}`);
  },

  getTrendById: (trendId: string) => fetchJson<Trend>(`${API_BASE}/trends/${trendId}`),

  getTrendHistory: (trendId: string) =>
    fetchJson<{ trend_id: string; trend_name: string; observations: TrendObservation[] }>(
      `${API_BASE}/trends/${trendId}/history`
    ),

  // Connectors
  getConnectorsStatus: (audit: boolean = false) =>
    fetchJson<AllConnectorsStatus>(`${API_BASE}/connectors/status${audit ? '?audit=true' : ''}`),

  // Collection
  triggerCollection: (payload: { platform?: string; allow_demo_fallback?: boolean } = {}) =>
    fetchJson<CollectionJobResponse>(`${API_BASE}/collection/run`, {
      method: 'POST',
      body: JSON.stringify({
        platform: payload.platform || 'all',
        allow_demo_fallback: payload.allow_demo_fallback ?? true
      }),
    }),

  // Analytics
  getAnalyticsOverview: () => fetchJson<AnalyticsOverview>(`${API_BASE}/analytics/overview`),

  getPlatformAnalytics: () =>
    fetchJson<{ platforms: PlatformMetric[] }>(`${API_BASE}/analytics/platforms`),

  // Nemotron
  previewNemotronPayload: () =>
    fetchJson<NemotronPayload>(`${API_BASE}/nemotron/preview`, { method: 'POST' }),

  sendToNemotron: () =>
    fetchJson<NemotronHandoffResponse>(`${API_BASE}/nemotron/send`, { method: 'POST' }),

  // System Health
  getHealth: () => fetchJson<{ status: string; service: string; environment: string }>('/health'),
};
