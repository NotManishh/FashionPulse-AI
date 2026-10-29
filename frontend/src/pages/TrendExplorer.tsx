import React, { useState, useEffect } from 'react';
import { Trend } from '../types';
import { api } from '../services/api';
import { TrendCard } from '../components/TrendCard';
import { TrendDetailModal } from '../components/TrendDetailModal';
import { Search, Filter, RefreshCw } from 'lucide-react';

export const TrendExplorer: React.FC = () => {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [status, setStatus] = useState<string>('all');
  const [timeWindow, setTimeWindow] = useState<string>('7d');
  const [selectedTrend, setSelectedTrend] = useState<Trend | null>(null);

  const fetchTrends = async () => {
    setLoading(true);
    try {
      const data = await api.getTrends({
        category: category !== 'all' ? category : undefined,
        status: status !== 'all' ? status : undefined,
        search: search.trim() ? search.trim() : undefined,
        limit: 50
      });
      setTrends(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTrends();
    }, 200);
    return () => clearTimeout(timer);
  }, [category, status, search]);

  const categories = [
    { id: 'all', label: 'All Categories' },
    { id: 'Denim', label: 'Denim & Pants' },
    { id: 'Silhouettes', label: 'Silhouettes & Tops' },
    { id: 'Aesthetics', label: 'Aesthetics' },
    { id: 'Footwear', label: 'Footwear' },
    { id: 'Outerwear', label: 'Outerwear' },
    { id: 'Materials', label: 'Materials' },
  ];

  const statuses = [
    { id: 'all', label: 'All Statuses' },
    { id: 'rising', label: 'Rising (+40%)' },
    { id: 'emerging', label: 'Emerging' },
    { id: 'steady', label: 'Steady' },
    { id: 'peaking', label: 'Peaking' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-serif font-bold text-white">Trend Explorer</h2>
          <p className="text-xs text-slate-400">
            Browse and filter through all discovered fashion styles, silhouettes, and aesthetic movements.
          </p>
        </div>

        {/* Time Window Switcher */}
        <div className="flex items-center space-x-1 p-1 bg-surface rounded-lg border border-border self-start sm:self-auto text-xs font-mono">
          {['24h', '7d', '30d'].map((w) => (
            <button
              key={w}
              onClick={() => setTimeWindow(w)}
              className={`px-3 py-1 rounded transition-colors ${
                timeWindow === w
                  ? 'bg-accent-gold text-black font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {w.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel rounded-xl p-4 space-y-4 border border-border">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by trend name, keyword (e.g. wide-leg, quiet luxury, hoodie)..."
              className="w-full pl-10 pr-4 py-2 bg-surface rounded-lg border border-border text-xs text-white placeholder-slate-500 focus:outline-none focus:border-accent-gold transition-colors"
            />
          </div>

          {/* Category Dropdown */}
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-slate-400 shrink-0" />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="bg-surface border border-border text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-accent-gold"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Status Pills */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-500 text-xs font-mono mr-1">Status:</span>
          {statuses.map((s) => (
            <button
              key={s.id}
              onClick={() => setStatus(s.id)}
              className={`px-3 py-1 rounded-full text-xs font-mono whitespace-nowrap transition-all border ${
                status === s.id
                  ? 'bg-surface text-accent-gold border-accent-gold/50 shadow-sm'
                  : 'bg-surface/50 text-slate-400 border-border hover:text-slate-200'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Trend Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-36 rounded-xl bg-surface/50 border border-border animate-pulse" />
          ))}
        </div>
      ) : trends.length === 0 ? (
        <div className="p-12 text-center glass-panel rounded-2xl border border-border">
          <p className="text-sm text-slate-400">No fashion trends match the current filter criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {trends.map((trend) => (
            <TrendCard
              key={trend.id}
              trend={trend}
              onSelect={(t) => setSelectedTrend(t)}
            />
          ))}
        </div>
      )}

      {/* Modal */}
      <TrendDetailModal
        trend={selectedTrend}
        onClose={() => setSelectedTrend(null)}
      />
    </div>
  );
};
