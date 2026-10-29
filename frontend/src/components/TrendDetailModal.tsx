import React, { useEffect, useState } from 'react';
import { Trend, TrendObservation } from '../types';
import { api } from '../services/api';
import { PlatformBadge } from './PlatformBadge';
import { ScoreGauge } from './ScoreGauge';
import { 
  X, 
  ExternalLink, 
  Calendar, 
  Tag, 
  Activity, 
  ShieldAlert, 
  TrendingUp, 
  CheckCircle2 
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface TrendDetailModalProps {
  trend: Trend | null;
  onClose: () => void;
}

export const TrendDetailModal: React.FC<TrendDetailModalProps> = ({ trend, onClose }) => {
  const [history, setHistory] = useState<TrendObservation[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (trend) {
      setLoading(true);
      api.getTrendHistory(trend.id)
        .then((res) => setHistory(res.observations || []))
        .catch(() => setHistory([]))
        .finally(() => setLoading(false));
    }
  }, [trend]);

  if (!trend) return null;

  const chartData = (history.length > 0 ? history : [
    { observation_window_start: trend.first_seen, trend_score: trend.current_score * 0.85, mention_count: Math.round(trend.mention_count * 0.7) },
    { observation_window_start: trend.last_seen, trend_score: trend.current_score, mention_count: trend.mention_count }
  ]).map((item, idx) => ({
    time: `Snapshot ${idx + 1}`,
    score: item.trend_score,
    mentions: item.mention_count
  }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-panel w-full max-w-3xl rounded-2xl border border-slate-700 max-h-[90vh] overflow-y-auto shadow-2xl p-6 sm:p-8 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-lg bg-surface text-slate-400 hover:text-white hover:bg-surfaceHover transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-border pb-5">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono uppercase tracking-wider text-accent-gold font-semibold">
                {trend.category}
              </span>
              {trend.current_rank && (
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-accent-gold/20 text-accent-gold border border-accent-gold/30">
                  Rank #{trend.current_rank}
                </span>
              )}
              {trend.is_demo ? (
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  Demo Data
                </span>
              ) : (
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Live Social
                </span>
              )}
            </div>
            <h2 className="text-2xl font-serif font-bold text-white mt-1">{trend.name}</h2>
          </div>

          <ScoreGauge score={trend.current_score} label="Overall Score" />
        </div>

        {/* Narrative Description */}
        <div className="mt-5">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">Intelligence Narrative</h4>
          <p className="text-sm text-slate-300 leading-relaxed bg-surface/60 p-4 rounded-xl border border-border">
            {trend.description || `Emerging silhouette and aesthetic trend detected with high cross-platform resonance across ${Object.keys(trend.platform_breakdown || {}).join(', ')}.`}
          </p>
        </div>

        {/* Trend Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
          <div className="bg-surface/40 p-3 rounded-lg border border-border">
            <span className="text-[10px] font-mono text-slate-400 uppercase">Momentum</span>
            <p className="text-lg font-bold text-white mt-0.5">{trend.momentum_score.toFixed(1)} / 100</p>
          </div>
          <div className="bg-surface/40 p-3 rounded-lg border border-border">
            <span className="text-[10px] font-mono text-slate-400 uppercase">Total Mentions</span>
            <p className="text-lg font-bold text-white mt-0.5">{trend.mention_count}</p>
          </div>
          <div className="bg-surface/40 p-3 rounded-lg border border-border">
            <span className="text-[10px] font-mono text-slate-400 uppercase">Confidence</span>
            <p className="text-lg font-bold text-emerald-400 mt-0.5">{(trend.confidence * 100).toFixed(0)}%</p>
          </div>
          <div className="bg-surface/40 p-3 rounded-lg border border-border">
            <span className="text-[10px] font-mono text-slate-400 uppercase">
              {trend.growth_status === 'provisional' ? 'Growth (Provisional)' : 'Growth Rate'}
            </span>
            <p className="text-lg font-bold text-accent-gold mt-0.5">
              {trend.growth_rate != null 
                ? (trend.growth_rate > 0 ? `+${trend.growth_rate}%` : `${trend.growth_rate}%`)
                : 'New Arrival'}
            </p>
          </div>
        </div>

        {/* Historical Velocity Chart */}
        <div className="mt-6">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
            <span>Historical Score Trajectory</span>
            <span className="text-[10px] text-slate-500 font-sans">Window: {trend.time_window}</span>
          </h4>
          <div className="h-44 w-full bg-surface/30 rounded-xl p-2 border border-border">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="scoreGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#e6c687" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#e6c687" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#12161f', borderColor: '#202838', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="score" stroke="#e6c687" strokeWidth={2} fillOpacity={1} fill="url(#scoreGlow)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Platform Breakdown & Keywords */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">Cross-Platform Distribution</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(trend.platform_breakdown || {}).map(([plat, cnt]) => (
                <PlatformBadge key={plat} platform={plat} count={cnt} size="md" />
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">Supporting Keywords & Synonyms</h4>
            <div className="flex flex-wrap gap-1.5">
              {trend.supporting_keywords.map((kw, i) => (
                <span key={i} className="text-xs font-mono px-2 py-0.5 rounded bg-surface border border-border text-slate-300">
                  #{kw}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Permitted References */}
        {trend.representative_references && trend.representative_references.length > 0 && (
          <div className="mt-6">
            <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">Permitted Source References</h4>
            <div className="space-y-1.5">
              {trend.representative_references.map((ref, i) => (
                <a
                  key={i}
                  href={ref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 text-xs text-accent-gold hover:underline bg-surface/30 p-2 rounded border border-border/70"
                >
                  <ExternalLink className="h-3 w-3 shrink-0" />
                  <span className="truncate">{ref}</span>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Data Limitation Notice */}
        <div className="mt-6 p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 flex items-start space-x-2 text-xs text-amber-300/80">
          <ShieldAlert className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
          <p>
            Observations reflect public social discussions from permitted API endpoints. Scoring weights emphasize velocity and cross-platform presence. Sample size: {trend.mention_count} posts.
          </p>
        </div>
      </div>
    </div>
  );
};
