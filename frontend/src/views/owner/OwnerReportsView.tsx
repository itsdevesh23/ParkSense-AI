import React from 'react';
import { api } from '../../api';
import {
  FileText,
  Download,
  Table,
  CheckCircle2,
  Calendar,
  FileSpreadsheet,
  ArrowUpRight
} from 'lucide-react';

export const OwnerReportsView: React.FC = () => {
  const reports = [
    {
      id: 'occupancy',
      title: 'Operational Occupancy & Forecast Snapshot',
      description: 'Current bay availability, percentage utilization, and 30m / 60m projected vacancy for all assigned facilities.',
      filename: 'parksense_occupancy_report.csv',
      endpoint: api.getReportDownloadUrl('occupancy'),
      format: 'CSV (Comma Separated Values)',
      fields: ['ID', 'Facility Name', 'System Code', 'Capacity', 'Occupied Bays', 'Vacant Bays', 'Occupancy %', '30m Forecast Bays', '60m Forecast Bays', 'Tariff'],
    },
    {
      id: 'benchmarks',
      title: 'Model Evaluation & Benchmark Ledger',
      description: 'Accuracy metrics for Centralized Attention-LSTM, FedAvg, and Personalized FedAvg across 3,293 test samples.',
      filename: 'parksense_benchmarks_report.csv',
      endpoint: api.getReportDownloadUrl('benchmarks'),
      format: 'CSV (Comma Separated Values)',
      fields: ['Model', 'Pooled MAE', 'Pooled RMSE', 'Macro Mean MAE', 'Between-Lot Std (sigma)', 'Mean Space Error (bays)'],
    },
    {
      id: 'audit',
      title: 'Fleet Dataset Audit & Personalization Trail',
      description: 'Lot-by-lot evaluation audit documenting baseline FedAvg vs fine-tuned personalization error reduction.',
      filename: 'parksense_audit_trail.csv',
      endpoint: api.getReportDownloadUrl('audit'),
      format: 'CSV (Comma Separated Values)',
      fields: ['Client ID', 'Parking Name', 'Capacity', 'Test Samples', 'Cent Attention MAE', 'FedAvg MAE', 'Personalized MAE', 'Personalization Gain %'],
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
          <FileText className="w-4 h-4" />
          Export & Reporting Hub
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          Operational Reports & Data Exports
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Generate audit-ready CSV exports of live fleet states, model performance scores, and data integrity ledgers.
        </p>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reports.map((rpt) => (
          <div
            key={rpt.id}
            className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
                <FileSpreadsheet className="w-5 h-5" />
              </div>

              <h2 className="text-base font-bold text-slate-900">{rpt.title}</h2>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">{rpt.description}</p>

              <div className="mt-4 pt-4 border-t border-slate-100">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Key Schema Columns:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {rpt.fields.slice(0, 5).map((f, i) => (
                    <span key={i} className="text-[10px] bg-slate-100 text-slate-600 font-mono px-2 py-0.5 rounded">
                      {f}
                    </span>
                  ))}
                  {rpt.fields.length > 5 && (
                    <span className="text-[10px] text-slate-400 font-mono px-1.5 py-0.5">
                      +{rpt.fields.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-medium">{rpt.format}</span>
              <a
                href={rpt.endpoint}
                download={rpt.filename}
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
    </div>
  );
};
