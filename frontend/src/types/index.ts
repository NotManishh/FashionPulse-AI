export interface Trend {
  id: string;
  name: string;
  category: string;
  description?: string;
  current_rank?: number | null;
  current_score: number;
  confidence: number;
  momentum_score: number;
  growth_rate?: number | null;
  growth_status: 'rising' | 'steady' | 'peaking' | 'emerging' | 'provisional' | 'insufficient_data';
  mention_count: number;
  total_engagement: number;
  platform_breakdown: Record<string, number>;
  first_seen: string;
  last_seen: string;
  time_window: string;
  supporting_keywords: string[];
  representative_references: string[];
  is_active: boolean;
  is_demo?: boolean;
  updated_at: string;
}

export interface TrendObservation {
  id: string;
  observation_window_start: string;
  observation_window_end: string;
  mention_count: number;
  engagement_score: number;
  trend_score: number;
  platform: string;
  recorded_at: string;
}

export interface Top10TrendsResponse {
  generated_at: string;
  time_window: string;
  total_trends_found: number;
  is_demo_mode: boolean;
  data_mode?: 'live_youtube' | 'full_live' | 'partial_live' | 'demo';
  live_records_count?: number;
  demo_records_count?: number;
  trends: Trend[];
}

export interface ConnectorStatus {
  platform: 'reddit' | 'instagram' | 'youtube';
  is_configured: boolean;
  is_authorized: boolean;
  has_live_data?: boolean;
  live_records_ingested?: number;
  demo_records_ingested?: number;
  status_tier?: 'production' | 'future_integration';
  last_success_at?: string | null;
  last_error_at?: string | null;
  last_error_message?: string | null;
  total_records_ingested: number;
  rate_limit_info: Record<string, any>;
  updated_at: string;
}

export interface AllConnectorsStatus {
  connectors: ConnectorStatus[];
  active_count: number;
  all_configured: boolean;
  primary_platform?: string;
}

export interface CategoryMetric {
  category: string;
  trend_count: number;
  total_mentions: number;
  average_score: number;
}

export interface PlatformMetric {
  platform: string;
  total_posts: number;
  fashion_relevant_posts: number;
  average_engagement: number;
  last_collected_at?: string | null;
}

export interface AnalyticsOverview {
  total_collected_records: number;
  total_active_trends: number;
  active_connectors_count: number;
  last_collection_time?: string | null;
  latest_update_timestamp: string;
  is_demo_mode: boolean;
  data_mode?: 'live_youtube' | 'full_live' | 'partial_live' | 'demo';
  live_records_count?: number;
  demo_records_count?: number;
  platform_distribution: Record<string, number>;
  platform_live_distribution?: Record<string, number>;
  platform_demo_distribution?: Record<string, number>;
  category_distribution: CategoryMetric[];
  emerging_trends_count: number;
  peaking_trends_count: number;
  average_confidence_score: number;
}

export interface NemotronTrendItem {
  rank: number;
  trend_name: string;
  trend_score: number;
  confidence: number;
  momentum_score: number;
  mention_count: number;
  platform_breakdown: Record<string, number>;
  growth_rate?: number | null;
  category?: string | null;
  supporting_keywords: string[];
  is_demo?: boolean;
}

export interface NemotronPayload {
  generated_at: string;
  time_window: string;
  source_platforms: string[];
  total_observations_analyzed: number;
  data_mode?: 'live_youtube' | 'full_live' | 'partial_live' | 'demo';
  live_observations_count?: number;
  demo_observations_count?: number;
  trends: NemotronTrendItem[];
  metadata: Record<string, any>;
}

export interface NemotronHandoffResponse {
  handoff_id: string;
  status: 'sent' | 'failed' | 'simulated' | 'previewed';
  endpoint_used?: string | null;
  status_code?: number | null;
  response_summary?: string | null;
  error_detail?: string | null;
  timestamp: string;
}

export interface CollectionJobResponse {
  job_id: string;
  platform: string;
  status: string;
  records_collected: number;
  records_new: number;
  error_message?: string | null;
  started_at: string;
  completed_at?: string | null;
  is_demo: boolean;
}
