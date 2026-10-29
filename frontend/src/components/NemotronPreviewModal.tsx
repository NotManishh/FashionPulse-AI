import React, { useState } from 'react';
import { NemotronPayload, NemotronHandoffResponse } from '../types';
import { api } from '../services/api';
import { 
  X, 
  Copy, 
  Check, 
  Send, 
  Cpu, 
  AlertCircle, 
  CheckCircle2, 
  Loader2 
} from 'lucide-react';

interface NemotronPreviewModalProps {
  payload: NemotronPayload | null;
  onClose: () => void;
}

export const NemotronPreviewModal: React.FC<NemotronPreviewModalProps> = ({ payload, onClose }) => {
  const [copied, setCopied] = useState(false);
  const [dispatching, setDispatching] = useState(false);
  const [handoffResult, setHandoffResult] = useState<NemotronHandoffResponse | null>(null);

  if (!payload) return null;

  const jsonString = JSON.stringify(payload, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
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
        handoff_id: 'error',
        status: 'failed',
        error_detail: err.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setDispatching(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-panel w-full max-w-4xl rounded-2xl border border-slate-700 max-h-[90vh] flex flex-col shadow-2xl p-6 relative">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-accent-violet/20 text-accent-violet border border-accent-violet/30">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2 flex-wrap">
                <span>NVIDIA Nemotron Handoff Payload</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-accent-violet/20 text-accent-violet border border-accent-violet/30">
                  {payload.trends.length} Trends Structured
                </span>
                {payload.data_mode === 'live_youtube' ? (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Live YouTube Production Stream
                  </span>
                ) : payload.data_mode === 'full_live' ? (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Live Data (Full)
                  </span>
                ) : payload.data_mode === 'partial_live' ? (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    Partial Live ({payload.source_platforms.join(', ')})
                  </span>
                ) : (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    Demo Mode
                  </span>
                )}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Generated: {new Date(payload.generated_at).toLocaleString()} | Sources: {payload.source_platforms.join(', ')} | Observations: {payload.total_observations_analyzed}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-surface text-slate-400 hover:text-white hover:bg-surfaceHover transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Handoff Result Banner if dispatched */}
        {handoffResult && (
          <div className={`mt-4 p-4 rounded-xl border flex items-start space-x-3 text-xs ${
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
                Status: {handoffResult.status.toUpperCase()}
              </p>
              {handoffResult.endpoint_used && (
                <p className="font-mono text-[11px] opacity-80">Endpoint: {handoffResult.endpoint_used}</p>
              )}
              {handoffResult.response_summary && (
                <p className="font-mono text-[11px]">{handoffResult.response_summary}</p>
              )}
              {handoffResult.error_detail && (
                <p className="font-mono text-[11px] text-rose-200">{handoffResult.error_detail}</p>
              )}
            </div>
          </div>
        )}

        {/* JSON Code Viewer */}
        <div className="mt-4 flex-1 overflow-hidden flex flex-col rounded-xl border border-border bg-[#08090d]">
          <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-surface/50 text-xs font-mono text-slate-400">
            <span>payload.json</span>
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-surface border border-border hover:text-white transition-colors"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? 'Copied' : 'Copy JSON'}</span>
            </button>
          </div>
          <pre className="p-4 overflow-y-auto font-mono text-xs text-slate-300 leading-relaxed max-h-[48vh]">
            <code>{jsonString}</code>
          </pre>
        </div>

        {/* Footer Actions */}
        <div className="mt-5 pt-4 border-t border-border flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Complies with downstream Nemotron inference schema (Section 6).
          </p>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-surface border border-border transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleDispatch}
              disabled={dispatching}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold bg-accent-violet hover:bg-purple-600 text-white shadow-lg shadow-purple-500/20 transition-all active:scale-95 disabled:opacity-50"
            >
              {dispatching ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Send to Nemotron</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
