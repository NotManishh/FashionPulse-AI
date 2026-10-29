import React from 'react';
import { Trend } from '../types';
import { ScoreGauge } from './ScoreGauge';
import { PlatformBadge } from './PlatformBadge';
import { TrendingUp, Sparkles, ChevronRight, Hash, Clock } from 'lucide-react';

interface TrendCardProps {
  trend: Trend;
  onSelect: (trend: Trend) => void;
}

export const TrendCard: React.FC<TrendCardProps> = ({ trend, onSelect }) => {
  const isTop3 = trend.current_rank && trend.current_rank <= 3;
  const rankColors: Record<number, string> = {
    1: 'from-amber-400 to-yellow-600 text-black font-extrabold',
    2: 'from-slate-200 to-slate-400 text-black font-bold',
    3: 'from-amber-700 to-amber-900 text-white font-bold'
  };

  return (
    <div 
      onClick={() => onSelect(trend)}
      className="glass-panel group rounded-xl p-5 cursor-pointer transition-all duration-300 hover:border-accent-gold/40 hover:bg-surfaceHover relative overflow-hidden"
    >
      {/* Glow highlight for #1 */}
      {trend.current_rank === 1 && (
        <div className="absolute top-0 right-0 w-32 h-32 bg-accent-gold/5 rounded-full blur-2xl pointer-events-none" />
      )}

      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          {/* Rank Badge */}
          {trend.current_rank ? (
            <div className={`h-8 w-8 rounded-lg flex items-center justify-center text-sm shadow-md ${
              isTop3 
                ? `bg-gradient-to-br ${rankColors[trend.current_rank] || 'bg-surface text-white'}` 
                : 'bg-surface border border-border text-slate-300 font-mono'
            }`}>
              #{trend.current_rank}
            </div>
          ) : (
            <div className="h-8 w-8 rounded-lg bg-surface border border-border flex items-center justify-center text-slate-400">
              <Hash className="h-4 w-4" />
            </div>
          )}

          <div>
            <div className="flex items-center space-x-2 flex-wrap gap-y-1">
              <span className="text-[11px] font-mono uppercase tracking-wider text-accent-gold/90 font-medium">
                {trend.category}
              </span>
              {trend.is_demo ? (
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  Demo
                </span>
              ) : (
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Live
                </span>
              )}
              {trend.growth_status === 'rising' && (
                <span className="inline-flex items-center space-x-0.5 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  <TrendingUp className="h-2.5 w-2.5" />
                  <span>+{trend.growth_rate}%</span>
                </span>
              )}
              {trend.growth_status === 'emerging' && (
                <span className="inline-flex items-center space-x-0.5 text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30">
                  <Sparkles className="h-2.5 w-2.5" />
                  <span>Emerging</span>
                </span>
              )}
              {trend.growth_status === 'provisional' && (
                <span 
                  title="Historical baseline is provisional: calculated over single retrospective search window prior to keyword expansion"
                  className="inline-flex items-center space-x-0.5 text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30"
                >
                  <Clock className="h-2.5 w-2.5" />
                  <span>Provisional{trend.growth_rate !== null ? ` (+${trend.growth_rate}%)` : ''}</span>
                </span>
              )}
            </div>

            <h4 className="text-base font-semibold text-white group-hover:text-accent-gold transition-colors mt-0.5">
              {trend.name}
            </h4>
            <p className="text-xs text-slate-400 line-clamp-1 mt-1">
              {trend.description || `High volume aesthetic characterized by ${trend.supporting_keywords.slice(0, 2).join(', ')}.`}
            </p>
          </div>
        </div>

        {/* Score Visualizer */}
        <div className="hidden sm:block">
          <ScoreGauge score={trend.current_score} />
        </div>
      </div>

      {/* Footer Details: Platforms & Keywords */}
      <div className="mt-4 pt-3 border-t border-border/60 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
          {Object.entries(trend.platform_breakdown || {}).map(([plat, count]) => (
            count > 0 && <PlatformBadge key={plat} platform={plat} count={count} />
          ))}
        </div>

        <div className="flex items-center space-x-2 text-slate-400 group-hover:text-slate-200 text-xs">
          <span className="font-mono text-[11px]">{trend.mention_count} mentions</span>
          <ChevronRight className="h-4 w-4 transform group-hover:translate-x-0.5 transition-transform" />
        </div>
      </div>
    </div>
  );
};
