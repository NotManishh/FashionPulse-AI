import React from 'react';

interface ScoreGaugeProps {
  score: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, label = "Trend Score", size = 'md' }) => {
  const normalized = Math.min(100, Math.max(0, score));
  
  let colorClass = 'text-emerald-400 stroke-emerald-400';
  let bgClass = 'stroke-emerald-950/40';
  if (normalized < 50) {
    colorClass = 'text-accent-violet stroke-accent-violet';
    bgClass = 'stroke-purple-950/40';
  } else if (normalized < 75) {
    colorClass = 'text-amber-400 stroke-amber-400';
    bgClass = 'stroke-amber-950/40';
  }

  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalized / 100) * circumference;

  return (
    <div className="flex items-center space-x-3">
      <div className="relative inline-flex items-center justify-center">
        <svg className="w-12 h-12 transform -rotate-90">
          <circle
            cx="24"
            cy="24"
            r={radius}
            className={`fill-none stroke-current ${bgClass}`}
            strokeWidth="3.5"
          />
          <circle
            cx="24"
            cy="24"
            r={radius}
            className={`fill-none stroke-current transition-all duration-700 ease-out ${colorClass}`}
            strokeWidth="3.5"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute text-[12px] font-mono font-bold text-white">
          {score.toFixed(0)}
        </span>
      </div>
      <div>
        <p className="text-[10px] uppercase font-mono tracking-wider text-slate-400">{label}</p>
        <p className={`text-xs font-semibold ${colorClass.split(' ')[0]}`}>
          {score >= 80 ? 'Peak Velocity' : score >= 60 ? 'High Momentum' : 'Emerging'}
        </p>
      </div>
    </div>
  );
};
