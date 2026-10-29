import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Overview } from './pages/Overview';
import { TrendExplorer } from './pages/TrendExplorer';
import { Analytics } from './pages/Analytics';
import { Connectors } from './pages/Connectors';
import { NemotronPanel } from './pages/NemotronPanel';
import { api } from './services/api';
import { Trend, AnalyticsOverview } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [topTrends, setTopTrends] = useState<Trend[]>([]);
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState(true);
  const [notification, setNotification] = useState<string | null>(null);
  const [refreshCounter, setRefreshCounter] = useState(0);

  const showNotification = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 4000);
  };

  const loadInitialData = async () => {
    try {
      const [health, trendsRes, ov] = await Promise.all([
        api.getHealth().catch(() => ({ status: 'degraded' })),
        api.getTop10Trends().catch(() => ({ trends: [], is_demo_mode: true })),
        api.getAnalyticsOverview().catch(() => null)
      ]);

      setIsBackendHealthy(health.status === 'healthy');
      setTopTrends((trendsRes as any).trends || []);
      setOverview(ov);
    } catch (err) {
      console.error(err);
      setIsBackendHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleTriggerIngestion = async () => {
    setIsRefreshing(true);
    try {
      const job = await api.triggerCollection({ platform: 'all', allow_demo_fallback: true });
      showNotification(`Ingestion finished! ${job.records_new} new social posts collected & trends updated.`);
      setRefreshCounter(prev => prev + 1);
      await loadInitialData();
    } catch (err: any) {
      showNotification(`Ingestion error: ${err.message}`);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0d11] text-[#f1f5f9]">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-xl glass-panel border border-accent-gold/40 shadow-2xl text-xs font-mono text-white animate-in slide-in-from-bottom duration-200">
          ✨ {notification}
        </div>
      )}

      {/* Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isDemoMode={overview?.is_demo_mode ?? true}
        dataMode={overview?.data_mode}
        onRefresh={handleTriggerIngestion}
        isRefreshing={isRefreshing}
        isBackendHealthy={isBackendHealthy}
      />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <Overview
            topTrends={topTrends}
            overview={overview}
            loading={loading}
            onRefresh={handleTriggerIngestion}
          />
        )}

        {activeTab === 'explorer' && <TrendExplorer />}

        {activeTab === 'analytics' && <Analytics />}

        {activeTab === 'connectors' && <Connectors refreshTrigger={refreshCounter} />}

        {activeTab === 'nemotron' && <NemotronPanel />}
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 text-center text-xs text-slate-500 font-mono">
        <p>FashionPulse AI &mdash; Live Social Media Trend Detection and Intelligence Platform</p>
        <p className="mt-1 text-[11px] text-slate-500">
          <span className="text-emerald-400 font-semibold">Active Engine:</span> YouTube Data API v3 (Live) &bull; 
          <span className="text-slate-400"> Planned Extensions:</span> Reddit for Researchers (BQAH), Meta Instagram Graph API (v26.0) &bull; NVIDIA Nemotron Adapter
        </p>
      </footer>
    </div>
  );
};
