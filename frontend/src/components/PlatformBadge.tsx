import React from 'react';

interface PlatformBadgeProps {
  platform: string;
  count?: number;
  size?: 'sm' | 'md';
}

export const PlatformBadge: React.FC<PlatformBadgeProps> = ({ platform, count, size = 'sm' }) => {
  const p = platform.toLowerCase();

  const styles: Record<string, { bg: string; text: string; border: string; label: string }> = {
    reddit: {
      bg: 'bg-orange-500/10',
      text: 'text-orange-400',
      border: 'border-orange-500/30',
      label: 'Reddit'
    },
    instagram: {
      bg: 'bg-fuchsia-500/10',
      text: 'text-fuchsia-400',
      border: 'border-fuchsia-500/30',
      label: 'Instagram'
    },
    youtube: {
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      border: 'border-red-500/30',
      label: 'YouTube'
    }
  };

  const current = styles[p] || {
    bg: 'bg-slate-500/10',
    text: 'text-slate-400',
    border: 'border-slate-500/30',
    label: platform
  };

  const sizeClass = size === 'sm' ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span className={`inline-flex items-center space-x-1 rounded-full font-mono font-medium border ${current.bg} ${current.text} ${current.border} ${sizeClass}`}>
      <span>{current.label}</span>
      {count !== undefined && (
        <span className="opacity-80">({count})</span>
      )}
    </span>
  );
};
