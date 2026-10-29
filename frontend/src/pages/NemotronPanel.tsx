import React, { useState, useEffect } from 'react';
import { NemotronPayload, NemotronHandoffResponse } from '../types';
import { api } from '../services/api';
import { 
  Cpu, 
  Send, 
  Copy, 
  Check, 
  AlertCircle, 
  CheckCircle2, 
  Loader2, 
  RefreshCw, 
  ExternalLink,
  Code2
} from 'lucide-react';

export const NemotronPanel: React.FC = () => {
  const [payload, setPayload] = useState<NemotronPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [dispatching, setDispatching] = useState(false);
  const [handoffResult, setHandoffResult] = useState<NemotronHandoffResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const loadPreview = async () => {
    setLoading(true);
    try {
      const res = await api.previewNemotronPayload();
      setPayload(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPreview();
  }, []);

  const handleCopy = () => {
    if (!payload) return;
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDispatch = async () => {
    setDispatching(true);
    try {
      const res = await api.sendToNemotron();
      setHandoffResult(res);
    } catch (err: any) {
      setHandoffResult({
        handoff_id: 'err',
        status: 'failed',
        error_detail: err.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setDispatching(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-serif font-bold text-white flex items-center gap-2">
            <Cpu className="h-5 w-5 text-accent-violet" />
            <span>NVIDIA Nemotron Model Integration</span>
          </h2>
          <p className="text-xs text-slate-400">
            Automated intelligence handoff preparing structured multi-platform trends for downstream LLM reasoning.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={loadPreview}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface hover:bg-surfaceHover text-slate-300 border border-border transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Regenerate Payload</span>
          </button>

          <button
            onClick={handleDispatch}
            disabled={dispatching || !payload}
            className="flex items-center space-x-2 px-4 py-1.5 rounded-lg text-xs font-semibold bg-accent-violet hover:bg-purple-600 text-white shadow-lg shadow-purple-500/20 transition-all active:scale-95 disabled:opacity-50"
          >
            {dispatching ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Dispatching...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Dispatch to Model</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Adapter Configuration & Handoff Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel rounded-xl p-5 border border-border">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Target Model</span>
          <p className="text-base font-bold text-white mt-1">nvidia/nemotron-4-340b</p>
          <p className="text-xs text-slate-400 mt-1">High-capacity reasoning & forecast adapter</p>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-border">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Trends Prepared</span>
          <p className="text-base font-bold text-accent-gold mt-1">
            {payload?.trends.length || 0} Trends Top-Ranked
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Source: {payload?.data_mode === 'live_youtube' ? `Live YouTube Production (${payload?.source_platforms.join(', ')})` : payload?.data_mode === 'full_live' ? 'Full Live (3/3)' : payload?.data_mode === 'partial_live' ? `Partial Live (${payload?.source_platforms.join(', ')})` : 'Demo Fallback'}
          </p>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-border">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Endpoint Status</span>
          <p className="text-base font-bold text-amber-400 mt-1">
            Awaiting Endpoint URL
          </p>
          <p className="text-xs text-slate-400 mt-1">Ready to receive NEMOTRON_ENDPOINT_URL</p>
        </div>
      </div>

      {/* Handoff Status Result Banner */}
      {handoffResult && (
        <div className={`p-4 rounded-xl border flex items-start space-x-3 text-xs ${
          handoffResult.status === 'sent'
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
        }`}>
          {handoffResult.status === 'sent' ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
          )}
          <div className="space-y-1">
            <p className="font-bold uppercase tracking-wider">
              {handoffResult.status === 'sent' ? 'Nemotron Request Succeeded' : 'Nemotron Not Configured / Unreachable'}
            </p>
            {handoffResult.error_detail && (
              <p className="font-mono text-[11px] text-rose-200">{handoffResult.error_detail}</p>
            )}
            {handoffResult.response_summary && (
              <p className="font-mono text-[11px] text-emerald-200">{handoffResult.response_summary}</p>
            )}
          </div>
        </div>
      )}

      {/* Payload Code Preview */}
      <div className="glass-panel rounded-2xl border border-border overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-surface/50 text-xs font-mono text-slate-400">
          <div className="flex items-center space-x-2">
            <Code2 className="h-4 w-4 text-accent-violet" />
            <span>nemotron_trend_payload.json</span>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 px-3 py-1 rounded bg-surface border border-border hover:text-white transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Payload'}</span>
          </button>
        </div>

        <pre className="p-6 overflow-y-auto font-mono text-xs text-slate-300 leading-relaxed max-h-[60vh] bg-[#07090d]">
          <code>{JSON.stringify(payload, null, 2)}</code>
        </pre>
      </div>
    </div>
  );
};
