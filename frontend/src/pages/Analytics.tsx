import React, { useState, useEffect } from 'react';
import { AnalyticsOverview, PlatformMetric, Trend } from '../types';
import { api } from '../services/api';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Legend 
} from 'recharts';
import { BarChart3, PieChart as PieIcon, Layers, Activity } from 'lucide-react';

export const Analytics: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [platforms, setPlatforms] = useState<PlatformMetric[]>([]);
  const [topTrends, setTopTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [ov, plat, trendsRes] = await Promise.all([
          api.getAnalyticsOverview(),
          api.getPlatformAnalytics(),
          api.getTop10Trends()
        ]);
        setOverview(ov);
        setPlatforms(plat.platforms);
        setTopTrends(trendsRes.trends);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-64 rounded-xl bg-surface/50 border border-border animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-64 rounded-xl bg-surface/50 border border-border animate-pulse" />
          <div className="h-64 rounded-xl bg-surface/50 border border-border animate-pulse" />
        </div>
      </div>
    );
  }

  // Chart Data Preparation
  const trendComparisonData = [...topTrends]
    .sort((a, b) => {
      if (a.current_rank != null && b.current_rank != null) {
        return a.current_rank - b.current_rank;
      }
      return b.current_score - a.current_score;
    })
    .slice(0, 8)
    .map((t) => ({
      name: t.name.length > 18 ? t.name.substring(0, 16) + '...' : t.name,
      score: t.current_score,
      momentum: t.momentum_score
    }));

  const isLive = overview?.data_mode === 'live_youtube' || overview?.data_mode === 'full_live' || overview?.data_mode === 'partial_live';
  const targetDistribution = isLive && overview?.platform_live_distribution && Object.keys(overview.platform_live_distribution).length > 0
    ? overview.platform_live_distribution
    : overview?.platform_distribution || {};

  const platformPieData = Object.entries(targetDistribution).map(([key, val]) => ({
    name: key.toUpperCase(),
    value: val
  }));

  const PLATFORM_COLORS = ['#ef4444', '#f97316', '#d946ef'];

  const categoryBarData = (overview?.category_distribution || []).map((c) => ({
    category: c.category,
    mentions: c.total_mentions,
    trends: c.trend_count
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <div>
        <h2 className="text-xl font-serif font-bold text-white">Cross-Platform Intelligence Analytics</h2>
        <p className="text-xs text-slate-400">
          Comparative velocity analytics, category distribution, and multi-platform ingestion telemetry.
        </p>
      </div>

      {/* Top Trends Velocity & Momentum Comparison */}
      <div className="glass-panel rounded-2xl p-6 border border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-accent-gold" />
            <h3 className="text-sm font-semibold text-white">Top 8 Trends: Overall Score vs Momentum Velocity</h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Scale 0 - 100</span>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trendComparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} interval={0} angle={-15} textAnchor="end" />
              <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#12161f', borderColor: '#202838', borderRadius: '8px', fontSize: '12px' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="score" name="Trend Score" fill="#e6c687" radius={[4, 4, 0, 0]} />
              <Bar dataKey="momentum" name="Momentum Velocity" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Two Column Grid: Platform Share & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Share Pie Chart */}
        <div className="glass-panel rounded-2xl p-6 border border-border flex flex-col">
          <div className="flex items-center space-x-2 mb-4">
            <PieIcon className="h-5 w-5 text-accent-gold" />
            <h3 className="text-sm font-semibold text-white">Social Source Share</h3>
            {isLive ? (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Live Stream ({overview?.live_records_count ?? 0})
              </span>
            ) : (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Demo Data
              </span>
            )}
          </div>

          <div className="h-64 w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={platformPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {platformPieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PLATFORM_COLORS[index % PLATFORM_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#12161f', borderColor: '#202838', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-center text-xs text-slate-400 font-mono">
            Total Content Posts Ingested: {overview?.total_collected_records ?? 0}
          </div>
        </div>

        {/* Category Distribution Bar Chart */}
        <div className="glass-panel rounded-2xl p-6 border border-border flex flex-col">
          <div className="flex items-center space-x-2 mb-4">
            <Layers className="h-5 w-5 text-accent-gold" />
            <h3 className="text-sm font-semibold text-white">Mentions by Fashion Category</h3>
          </div>

          <div className="h-64 w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryBarData} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="category" type="category" stroke="#64748b" fontSize={10} width={90} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#12161f', borderColor: '#202838', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="mentions" name="Total Mentions" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-center text-xs text-slate-400 font-mono">
            Active Categories Monitored: {categoryBarData.length}
          </div>
        </div>
      </div>
    </div>
  );
};
