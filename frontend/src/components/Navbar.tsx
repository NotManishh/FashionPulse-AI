import React from 'react';
import { 
  Flame, 
  Compass, 
  BarChart3, 
  Share2, 
  Cpu, 
  RefreshCw, 
  ShieldCheck, 
  AlertTriangle 
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isDemoMode: boolean;
  dataMode?: 'live_youtube' | 'full_live' | 'partial_live' | 'demo';
  onRefresh: () => void;
  isRefreshing: boolean;
  isBackendHealthy: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isDemoMode,
  dataMode,
  onRefresh,
  isRefreshing,
  isBackendHealthy
}) => {
  const navItems = [
    { id: 'overview', label: 'Top 10 Trends', icon: Flame },
    { id: 'explorer', label: 'Trend Explorer', icon: Compass },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'connectors', label: 'Connectors', icon: Share2 },
    { id: 'nemotron', label: 'Nemotron AI', icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-[#0b0d11]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-accent-gold via-amber-500 to-accent-violet flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Flame className="h-5 w-5 text-black" />
          </div>
          <div>
            <span className="text-lg font-serif font-bold tracking-tight text-white flex items-center gap-1.5">
              FashionPulse <span className="text-xs font-sans font-semibold px-1.5 py-0.5 rounded bg-accent-gold/20 text-accent-gold border border-accent-gold/30">AI</span>
            </span>
            <p className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">Social Trend Intelligence</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-surface text-white border border-border shadow-sm shadow-black/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface/50'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-accent-gold' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status Indicators & Action */}
        <div className="flex items-center space-x-3">
          {/* Live vs Demo Badge */}
          {dataMode === 'live_youtube' || dataMode === 'full_live' || dataMode === 'partial_live' ? (
            <div 
              title="YouTube Data API v3 live social stream active" 
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>LIVE DATA (YouTube v3)</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
              <AlertTriangle className="h-3 w-3" />
              <span>DEMO MODE</span>
            </div>
          )}

          {/* Backend Status indicator */}
          <div 
            title={isBackendHealthy ? "Backend connected" : "Backend degraded"}
            className={`h-2.5 w-2.5 rounded-full ${isBackendHealthy ? 'bg-emerald-500' : 'bg-rose-500 animate-ping'}`}
          />

          {/* Trigger Ingestion button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surfaceHover hover:bg-border text-slate-200 border border-border transition-all active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-accent-gold' : 'text-slate-400'}`} />
            <span className="hidden sm:inline">Ingest Content</span>
          </button>
        </div>
      </div>
    </header>
  );
};
