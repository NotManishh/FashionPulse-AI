import React, { useState, useEffect } from 'react';
import { AllConnectorsStatus, ConnectorStatus } from '../types';
import { api } from '../services/api';
import { 
  Share2, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  ExternalLink, 
  Key, 
  ShieldCheck, 
  HelpCircle,
  RefreshCw 
} from 'lucide-react';

interface ConnectorsProps {
  refreshTrigger?: number;
}

export const Connectors: React.FC<ConnectorsProps> = ({ refreshTrigger }) => {
  const [data, setData] = useState<AllConnectorsStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadStatus = async (audit: boolean = false) => {
    try {
      const res = await api.getConnectorsStatus(audit);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadStatus(false);
  }, [refreshTrigger]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadStatus(true);
  };

  const getPlatformDetails = (platform: string) => {
    switch (platform) {
      case 'reddit':
        return {
          title: 'Reddit (Reddit for Researchers / BQAH)',
          description: 'Official academic research adapter via Google BigQuery Analytics Hub (BQAH). Cadence: monthly batch update with 6-month historical lag (not real-time).',
          portalUrl: 'https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki',
          authType: 'Google BigQuery Analytics Hub (@redditresearchers.com)',
          requiredEnv: ['ENABLE_REDDIT_RFR_INGESTION', 'RFR_GCP_PROJECT_ID', 'RFR_DATASET_NAME']
        };
      case 'instagram':
        return {
          title: 'Meta Graph API (Instagram v26.0)',
          description: 'Official Meta Graph API v26.0 hashtag discovery endpoint. Requires Instagram Public Content Access (IPCA) feature approval.',
          portalUrl: 'https://developers.facebook.com/apps/',
          authType: 'Meta User/Page Token (v26.0) + IG Business Account ID',
          requiredEnv: ['INSTAGRAM_API_VERSION', 'INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_BUSINESS_ACCOUNT_ID']
        };
      case 'youtube':
        return {
          title: 'YouTube Data API v3',
          description: 'Google Cloud API key with 2-phase batching (dedicated 100 searches/day bucket + 10k general units/day pool).',
          portalUrl: 'https://console.cloud.google.com/apis/credentials',
          authType: 'Google Cloud API Key',
          requiredEnv: ['YOUTUBE_API_KEY']
        };
      default:
        return {
          title: platform,
          description: '',
          portalUrl: '#',
          authType: 'API Key',
          requiredEnv: []
        };
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-serif font-bold text-white flex items-center gap-2">
            <Share2 className="h-5 w-5 text-accent-gold" />
            <span>Social Media Platform Connectors</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time authorization status and credential auditing for YouTube Data API v3 and optional roadmapped connectors.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface hover:bg-surfaceHover text-slate-300 border border-border self-start sm:self-auto transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin text-accent-gold' : ''}`} />
          <span>Audit Status</span>
        </button>
      </div>

      {/* Active Production Connector */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-white font-mono">
              Active Production Connector (Primary Ingestion Source)
            </h3>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
            Sole Active Workflow
          </span>
        </div>

        {(() => {
          const ytConnector = data?.connectors.find(c => c.platform === 'youtube');
          if (!ytConnector) return null;
          const info = getPlatformDetails('youtube');

          return (
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-emerald-500/30 bg-surface/80 shadow-lg shadow-emerald-950/20">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div className="space-y-3 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      Primary Pipeline
                    </span>
                    <h3 className="text-xl font-bold text-white">{info.title}</h3>
                    <span className="inline-flex items-center space-x-1 text-xs font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>{ytConnector.has_live_data ? 'Live Ingesting (Active Stream)' : 'API Validated'}</span>
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {info.description} Powering all real-time fashion trend discovery, engagement weighting, and Top 10 candidate rankings.
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                  <a
                    href={info.portalUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg text-xs font-medium bg-surfaceHover hover:bg-border text-slate-200 border border-border transition-colors"
                  >
                    <span>Google Cloud Console</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>

              {/* Ingestion Telemetry Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-border">
                <div className="p-3.5 rounded-xl bg-surface/50 border border-border">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Live Ingested</span>
                  <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5">
                    {ytConnector.live_records_ingested ?? 0} live
                  </div>
                  <span className="text-[10px] text-slate-400">Stored live videos</span>
                </div>

                <div className="p-3.5 rounded-xl bg-surface/50 border border-border">
                  <span className="text-[10px] font-mono uppercase text-slate-400">API Status</span>
                  <div className="text-base font-semibold font-mono text-emerald-400 mt-0.5">
                    {ytConnector.is_authorized ? 'Verified 200 OK' : 'Awaiting Check'}
                  </div>
                  <span className="text-[10px] text-slate-400">Google Cloud v3</span>
                </div>

                <div className="p-3.5 rounded-xl bg-surface/50 border border-border">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Daily Quota Tier</span>
                  <div className="text-base font-semibold font-mono text-white mt-0.5">
                    100 search / 10k units
                  </div>
                  <span className="text-[10px] text-slate-400">Midnight PT reset</span>
                </div>

                <div className="p-3.5 rounded-xl bg-surface/50 border border-border">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Last Ingestion</span>
                  <div className="text-base font-semibold font-mono text-slate-200 mt-0.5">
                    {ytConnector.last_success_at ? new Date(ytConnector.last_success_at).toLocaleTimeString() : 'Active'}
                  </div>
                  <span className="text-[10px] text-slate-400">Automated cadence</span>
                </div>
              </div>
            </div>
          );
        })()}
      </div>

      {/* Future Integrations Section */}
      <div className="space-y-4 pt-4 border-t border-border">
        <div>
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-slate-400" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono">
              Future Integrations (Optional / Non-blocking)
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Reddit for Researchers (BQAH) and Meta Graph API (v26.0) are roadmapped platforms. Historical database records are preserved and do not affect the live YouTube pipeline.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data?.connectors
            .filter(c => c.platform !== 'youtube')
            .map((connector) => {
              const info = getPlatformDetails(connector.platform);
              return (
                <div
                  key={connector.platform}
                  className="glass-panel rounded-2xl p-6 border border-border flex flex-col justify-between space-y-5 opacity-90 hover:opacity-100 transition-opacity"
                >
                  <div>
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                          Roadmapped Integration
                        </span>
                        <h4 className="text-base font-bold text-white mt-0.5">{info.title}</h4>
                      </div>

                      {connector.platform === 'reddit' ? (
                        <span className="inline-flex items-center space-x-1 text-xs font-mono px-2 py-0.5 rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/20">
                          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                          <span>Disabled (Pending RFR)</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 text-xs font-mono px-2 py-0.5 rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/20">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          <span>Optional (Unconfigured)</span>
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400 mt-3 leading-relaxed">
                      {info.description}
                    </p>

                    {/* Preserved Telemetry Stats */}
                    <div className="mt-4 pt-4 border-t border-border space-y-2 text-xs">
                      <div className="flex items-center justify-between text-slate-400">
                        <span>Workflow Status:</span>
                        <span className="font-mono text-slate-400">Excluded from Live Pipeline</span>
                      </div>

                      <div className="flex items-center justify-between text-slate-400">
                        <span>Historical Records:</span>
                        <span className="font-mono text-slate-300">
                          {connector.demo_records_ingested ?? 0} demo records preserved
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-slate-400">
                        <span>Authentication Method:</span>
                        <span className="font-mono text-slate-400 truncate max-w-[220px]" title={info.authType}>
                          {info.authType}
                        </span>
                      </div>
                    </div>
                  </div>

                  <a
                    href={info.portalUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center space-x-2 w-full py-2 rounded-lg text-xs font-medium bg-surfaceHover hover:bg-border text-slate-400 hover:text-slate-200 border border-border transition-colors"
                  >
                    <span>Documentation Portal</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
              );
            })}
        </div>
      </div>

      {/* Safe Configuration & Credential Setup Guide */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-border space-y-5">
        <div className="flex items-center space-x-2">
          <Key className="h-5 w-5 text-accent-gold" />
          <h3 className="text-base font-bold text-white">Application Configuration & Credential Setup</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
          FashionPulse AI runs in full production mode using YouTube Data API v3 as the sole required social connector. All keys reside securely in the root <code className="text-accent-gold font-mono bg-black/40 px-1.5 py-0.5 rounded">.env</code> file.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2">
          {/* Primary YouTube */}
          <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-3 md:col-span-1">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-emerald-300 uppercase font-mono">1. YouTube Data API v3</h4>
              <span className="text-[10px] font-mono uppercase bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded">Required</span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              Google Cloud API key. The only required key for live social ingestion, trend extraction, and ranking.
            </p>
            <pre className="text-[10px] font-mono text-emerald-300 bg-black/70 p-2.5 rounded border border-emerald-500/20">
YOUTUBE_API_KEY=AIzaSy...
            </pre>
          </div>

          {/* Optional Reddit */}
          <div className="p-5 rounded-xl bg-surface/50 border border-border space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-300 uppercase font-mono">2. Reddit (RFR BigQuery)</h4>
              <span className="text-[10px] font-mono uppercase bg-slate-700/40 text-slate-400 px-1.5 py-0.5 rounded">Optional</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Disabled by default. Academic research via BigQuery Analytics Hub. Cadence: monthly refresh with 6-month historical lag.
            </p>
            <pre className="text-[10px] font-mono text-slate-400 bg-black/60 p-2.5 rounded">
ENABLE_REDDIT_RFR_INGESTION=false
RFR_GCP_PROJECT_ID=
RFR_DATASET_NAME=
            </pre>
          </div>

          {/* Optional Instagram */}
          <div className="p-5 rounded-xl bg-surface/50 border border-border space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-300 uppercase font-mono">3. Instagram API (v26.0)</h4>
              <span className="text-[10px] font-mono uppercase bg-slate-700/40 text-slate-400 px-1.5 py-0.5 rounded">Optional</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Meta Graph API v26.0. Requires Instagram Public Content Access (IPCA) feature approval.
            </p>
            <pre className="text-[10px] font-mono text-slate-400 bg-black/60 p-2.5 rounded">
INSTAGRAM_API_VERSION=v26.0
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
