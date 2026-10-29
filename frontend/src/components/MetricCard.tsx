import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant: 'positive' | 'warning' | 'neutral' | 'accent';
  };
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  badge
}) => {
  const badgeClasses = {
    positive: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    neutral: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
    accent: 'bg-accent-violet/15 text-accent-violet border-accent-violet/30'
  };

  return (
    <div className="glass-panel rounded-xl p-5 relative overflow-hidden transition-all hover:border-slate-700/80">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-mono uppercase tracking-wider text-slate-400">{title}</p>
          <div className="flex items-baseline space-x-2">
            <h3 className="text-2xl font-bold font-sans text-white tracking-tight">{value}</h3>
            {badge && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${badgeClasses[badge.variant]}`}>
                {badge.text}
              </span>
            )}
          </div>
          {subtext && <p className="text-xs text-slate-500">{subtext}</p>}
        </div>
        <div className="p-2.5 rounded-lg bg-surface border border-border text-slate-300">
          <Icon className="h-5 w-5 text-accent-gold" />
        </div>
      </div>
    </div>
  );
};
