import React from 'react';
import { api } from '../../api';
import {
  Download,
  FileSpreadsheet,
  FileText,
  ShieldCheck,
  CheckCircle2,
  Database,
  BarChart3,
  ExternalLink
} from 'lucide-react';

export const AdminReportsView: React.FC = () => {
  const exports = [
    {
      title: 'Full 30-Lot Live Occupancy & Forecast Report',
      description: 'Current real-time occupancy and 30m / 60m projected vacant bays across all 30 Birmingham parking facilities.',
      filename: 'parksense_master_occupancy.csv',
      url: api.getReportDownloadUrl('occupancy'),
      records: '30 facilities',
      badge: 'Live Replay',
    },
    {
      title: '30-Minute Horizon (y30) Benchmark Table',
      description: 'Official 6-model benchmark results evaluating ARIMA, XGBoost, LSTM, Attention-LSTM, FedAvg, and Personalized FedAvg on 3,293 instances.',
      filename: 'benchmark_30min_y30.csv',
      url: api.getReportDownloadUrl('benchmarks', '30'),
      records: '6 models • 3,293 samples',
      badge: 'Primary Benchmark',
    },
    {
      title: '60-Minute Horizon (y60) Benchmark Table',
      description: 'Official 6-model benchmark results evaluating 1-hour lookahead accuracy on the identical 3,293 test instances.',
      filename: 'benchmark_60min_y60.csv',
      url: api.getReportDownloadUrl('benchmarks', '60'),
      records: '6 models • 3,293 samples',
      badge: 'Secondary Horizon',
    },
    {
      title: 'Per-Lot Evaluation & Personalization Audit Trail',
      description: 'Comprehensive audit detailing client-by-client capacity, test sample counts, centralized vs federated error, and personalization gain.',
      filename: 'per_lot_evaluation_audit.csv',
      url: api.getReportDownloadUrl('audit'),
      records: '30 client partitions',
      badge: 'Integrity Audit',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
          <Download className="w-4 h-4" />
          Master Data Repository
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          System Artifacts & Benchmark Exports
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Download verifiable CSV artifacts corresponding to Review 2 academic evaluation standards.
        </p>
      </div>

      {/* Grid of Master Exports */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {exports.map((exp, i) => (
          <div
            key={i}
            className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-3">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
                  {exp.badge}
                </span>
              </div>

              <h2 className="text-base font-bold text-slate-900">{exp.title}</h2>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">{exp.description}</p>
              <div className="mt-3 text-[11px] text-slate-400 font-mono">
                Scope: {exp.records}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs font-mono text-slate-500">{exp.filename}</span>
              <a
                href={exp.url}
                download={exp.filename}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download CSV
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Technical Memo Callout */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1 text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-1">
            <FileText className="w-3.5 h-3.5" /> Project Technical Documentation
          </div>
          <h3 className="text-base font-bold">Research Methodology & Reconciliation Memo</h3>
          <p className="text-xs text-slate-300 mt-1 max-w-xl">
            Detailed technical documentation explaining the 70/15/15 chronological partition, ARIMA convergence safeguard with persistence fallback, and edge personalization dynamics.
          </p>
        </div>

        <div className="shrink-0">
          <span className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white/10 text-white text-xs font-bold border border-white/20">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Verified & Archived
          </span>
        </div>
      </div>
    </div>
  );
};
