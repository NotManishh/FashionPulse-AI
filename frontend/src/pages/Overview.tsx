import React, { useState } from 'react';
import { Trend, AnalyticsOverview, NemotronPayload } from '../types';
import { MetricCard } from '../components/MetricCard';
import { TrendCard } from '../components/TrendCard';
import { TrendDetailModal } from '../components/TrendDetailModal';
import { NemotronPreviewModal } from '../components/NemotronPreviewModal';
import { api } from '../services/api';
import { 
  Flame, 
  TrendingUp, 
  Database, 
  Share2, 
  Sparkles, 
  Cpu, 
  Clock, 
  Info,
  AlertTriangle 
} from 'lucide-react';

interface OverviewProps {
  topTrends: Trend[];
  overview: AnalyticsOverview | null;
  loading: boolean;
  onRefresh: () => void;
}

export const Overview: React.FC<OverviewProps> = ({
  topTrends,
  overview,
  loading,
  onRefresh
}) => {
  const [selectedTrend, setSelectedTrend] = useState<Trend | null>(null);
  const [nemotronPayload, setNemotronPayload] = useState<NemotronPayload | null>(null);
  const [loadingNemotron, setLoadingNemotron] = useState(false);

  const handleOpenNemotron = async () => {
    setLoadingNemotron(true);
    try {
      const payload = await api.previewNemotronPayload();
      setNemotronPayload(payload);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingNemotron(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Status Notice Banners */}
      {overview?.data_mode === 'demo' && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start space-x-3 text-amber-200">
          <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <span className="font-semibold text-amber-300 uppercase tracking-wider font-mono">
              Development Demonstration Mode Active
            </span>
            <p className="text-amber-200/80 leading-relaxed">
              Social connectors are currently running in demo fallback mode because live credentials (Reddit, Instagram, YouTube) are unconfigured. Trends and scores are dynamically calculated using our mathematical intelligence engine over labelled sample observations. Check the <strong>Connectors</strong> tab to configure genuine API keys.
            </p>
          </div>
        </div>
      )}

      {overview?.data_mode !== 'demo' && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start space-x-3 text-emerald-200">
          <Sparkles className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <span className="font-semibold text-emerald-300 uppercase tracking-wider font-mono flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              YouTube Data API v3 Production Stream Active
            </span>
            <p className="text-emerald-200/90 leading-relaxed">
              <strong>YouTube Data API v3</strong> is actively streaming genuine social observations ({overview?.live_records_count ?? 0} live videos ingested). Trends and scores are computed strictly from real-world YouTube engagement evidence. (Reddit for Researchers and Meta Instagram Graph API are roadmapped as optional future extensions).
            </p>
          </div>
        </div>
      )}

      {/* Top Level Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Top Ranked Trends"
          value={topTrends.length}
          subtext="Derived dynamically from YouTube observations"
          icon={Flame}
          badge={{ text: '7-Day Window', variant: 'accent' }}
        />
        <MetricCard
          title="Observations Ingested"
          value={overview?.data_mode === 'demo' ? (overview?.total_collected_records ?? 0) : (overview?.live_records_count ?? 0)}
          subtext="Genuine YouTube video observations"
          icon={Database}
          badge={{ 
            text: overview?.data_mode === 'demo' ? 'Demo Data' : `Live (${overview?.live_records_count ?? 0} videos)`, 
            variant: overview?.data_mode === 'demo' ? 'warning' : 'positive' 
          }}
        />
        <MetricCard
          title="Active Connectors"
          value="1 / 1 (YouTube v3)"
          subtext="Primary production connector online"
          icon={Share2}
          badge={{ text: 'Production Active', variant: 'positive' }}
        />
        <MetricCard
          title="Emerging Velocity"
          value={overview?.emerging_trends_count ?? 0}
          subtext="Trends with acceleration > 40%"
          icon={TrendingUp}
          badge={{ text: 'High Momentum', variant: 'positive' }}
        />
      </div>

      {/* Top Ranked Fashion Trends Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-serif font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-accent-gold" />
              <span>Official Top {topTrends.length > 0 ? topTrends.length : 10} Fashion Trends</span>
            </h2>
            <p className="text-xs text-slate-400">
              Ranked dynamically by composite velocity, normalized engagement, and recency from YouTube social intelligence.
            </p>
          </div>

          <button
            onClick={handleOpenNemotron}
            disabled={loadingNemotron}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-accent-violet/20 hover:bg-accent-violet/30 text-accent-violet border border-accent-violet/40 transition-all active:scale-95 shadow-sm"
          >
            <Cpu className="h-4 w-4" />
            <span>{loadingNemotron ? 'Preparing Handoff...' : 'Preview Nemotron Payload'}</span>
          </button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 rounded-xl bg-surface/50 border border-border animate-pulse" />
            ))}
          </div>
        ) : topTrends.length === 0 ? (
          <div className="p-12 text-center glass-panel rounded-2xl border border-border">
            <Info className="h-10 w-10 text-slate-500 mx-auto mb-3" />
            <h4 className="text-base font-semibold text-white">No Trends Computed Yet</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Run content ingestion to fetch observations and trigger the trend intelligence clustering engine.
            </p>
            <button
              onClick={onRefresh}
              className="mt-4 px-4 py-2 rounded-lg text-xs font-semibold bg-accent-gold text-black hover:bg-amber-400 transition-colors"
            >
              Run Ingestion Now
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...topTrends]
              .sort((a, b) => {
                if (a.current_rank != null && b.current_rank != null) {
                  return a.current_rank - b.current_rank;
                }
                return (b.current_score - a.current_score) || 
                       (b.momentum_score - a.momentum_score) || 
                       (b.confidence - a.confidence);
              })
              .map((trend) => (
                <TrendCard
                  key={trend.id}
                  trend={trend}
                  onSelect={(t) => setSelectedTrend(t)}
                />
              ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <TrendDetailModal
        trend={selectedTrend}
        onClose={() => setSelectedTrend(null)}
      />

      <NemotronPreviewModal
        payload={nemotronPayload}
        onClose={() => setNemotronPayload(null)}
      />
    </div>
  );
};
