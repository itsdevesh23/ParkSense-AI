import React from 'react';
import { Info, Sparkles, ShieldCheck } from 'lucide-react';

export const DemoBanner: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-950 to-slate-900 text-white px-4 py-2.5 text-xs border-b border-blue-950/40 shadow-inner">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center p-1 rounded bg-blue-500/20 text-blue-300">
            <Sparkles className="w-3.5 h-3.5" />
          </span>
          <span className="font-semibold text-blue-200 uppercase tracking-wider text-[11px]">Academic Project:</span>
          <span className="text-slate-200">
            <strong>ParkSense AI</strong> — Federated Multi-Lot Smart Parking Forecasting (Birmingham IoT Testbed)
          </span>
        </div>
        <div className="flex items-center gap-4 text-slate-300 text-[11px]">
          <span className="flex items-center gap-1 text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            30 Edge Nodes Active
          </span>
          <span className="hidden sm:inline text-slate-400">|</span>
          <span className="hidden sm:flex items-center gap-1 text-slate-300">
            <Info className="w-3.5 h-3.5 text-blue-400" />
            Simulated Edge Data Locality & Benchmark Replay
          </span>
        </div>
      </div>
    </div>
  );
};
