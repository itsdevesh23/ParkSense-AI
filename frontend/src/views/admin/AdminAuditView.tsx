import React, { useState, useEffect, useMemo } from 'react';
import { AuditRecord } from '../../types';
import { api } from '../../api';
import {
  ClipboardCheck,
  ShieldCheck,
  AlertTriangle,
  Database,
  Search,
  Download,
  CheckCircle2,
  TrendingDown,
  RefreshCw,
  FileSpreadsheet
} from 'lucide-react';

export const AdminAuditView: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<string>('Client ID');

  const fetchAudit = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminAudit();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  const auditRows: AuditRecord[] = data?.per_lot_audit || [];

  const filteredRows = useMemo(() => {
    return auditRows
      .filter((r) =>
        r['Parking Name'].toLowerCase().includes(search.toLowerCase()) ||
        r['Client ID'].toLowerCase().includes(search.toLowerCase())
      )
      .sort((a, b) => {
        if (sortField === 'Gain') {
          return b['Personalization Gain (%)'] - a['Personalization Gain (%)'];
        }
        if (sortField === 'Capacity') {
          return b.Capacity - a.Capacity;
        }
        if (sortField === 'Personalized MAE') {
          return a['Personalized MAE'] - b['Personalized MAE'];
        }
        return a['Client ID'].localeCompare(b['Client ID'], undefined, { numeric: true });
      });
  }, [auditRows, search, sortField]);

  if (loading && !data) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-500">Loading dataset integrity audit ledger...</p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
            <ClipboardCheck className="w-4 h-4" />
            Dataset Provenance & Quality Audit
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Data Quality & Personalization Audit Trail
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Transparent record of all data boundary corrections and client-by-client accuracy gains.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={api.getReportDownloadUrl('audit')}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export Audit CSV
          </a>
          <button
            onClick={fetchAudit}
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors"
            title="Reload audit"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Audit Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Total Raw Ingested
          </span>
          <p className="text-2xl font-black text-slate-900 mt-1">35,717 Records</p>
          <span className="text-xs text-slate-500">Across 30 parking lots</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Sensor Clipping Events
          </span>
          <p className="text-2xl font-black text-amber-600 mt-1">385 Clamped</p>
          <span className="text-xs text-slate-500">12 negative (NIA North) + 373 over-cap</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Sampling Cadence
          </span>
          <p className="text-2xl font-black text-blue-600 mt-1">18 / Day</p>
          <span className="text-xs text-slate-500">08:00 to 16:30 (30-min steps)</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Partition Leakage Check
          </span>
          <p className="text-2xl font-black text-emerald-600 mt-1">0.0% Leakage</p>
          <span className="text-xs text-emerald-700 font-medium">Strict chronological split</span>
        </div>
      </div>

      {/* Audit Details Box */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 text-xs text-slate-700 space-y-3">
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          Data Integrity Methodology & Verification
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80">
            <span className="font-bold text-slate-900 block mb-1">Negative Value Handling</span>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              12 anomalous negative occupancy readings were detected at NIA North. Rather than deleting time steps and breaking sequential continuity, values were clamped to zero.
            </p>
          </div>
          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80">
            <span className="font-bold text-slate-900 block mb-1">Capacity Overfill Clamping</span>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              373 records where occupied bays momentarily exceeded rated capacity were clamped to 1.0 (100% capacity), preventing mathematical gradient explosions during LSTM backpropagation.
            </p>
          </div>
          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80">
            <span className="font-bold text-slate-900 block mb-1">Lookback Temporal Integrity</span>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              Sequence lookback is fixed at 4 timesteps (2 hours). The 70/15/15 chronological partition ensures that no test timestamp precedes any training sample.
            </p>
          </div>
        </div>
      </div>

      {/* Lot-by-Lot Evaluation Audit Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-slate-900">Per-Lot Evaluation Audit Ledger</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Verified records from results/per_lot_evaluation_audit.csv across all 30 client partitions.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter lot..."
                className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
              />
            </div>

            <select
              value={sortField}
              onChange={(e) => setSortField(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700"
            >
              <option value="Client ID">Sort by Client ID</option>
              <option value="Gain">Sort by Personalization Gain</option>
              <option value="Capacity">Sort by Capacity</option>
              <option value="Personalized MAE">Sort by Lowest Error</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                <th className="py-2.5 px-3">Client</th>
                <th className="py-2.5 px-3">Parking Name</th>
                <th className="py-2.5 px-3 text-right">Capacity</th>
                <th className="py-2.5 px-3 text-right">Samples</th>
                <th className="py-2.5 px-3 text-right">Cent. Attn MAE</th>
                <th className="py-2.5 px-3 text-right">FedAvg MAE</th>
                <th className="py-2.5 px-3 text-right">Personalized MAE</th>
                <th className="py-2.5 px-3 text-right">Mean Error (Bays)</th>
                <th className="py-2.5 px-3 text-right">Gain (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {filteredRows.map((r) => (
                <tr key={r['Client ID']} className="hover:bg-slate-50">
                  <td className="py-2 px-3 font-bold text-slate-500">{r['Client ID']}</td>
                  <td className="py-2 px-3 font-sans font-semibold text-slate-900">{r['Parking Name']}</td>
                  <td className="py-2 px-3 text-right text-slate-700 font-medium">{r.Capacity}</td>
                  <td className="py-2 px-3 text-right text-blue-700">{r['Test Samples']}</td>
                  <td className="py-2 px-3 text-right text-slate-600">{r['Cent Attention MAE'].toFixed(4)}</td>
                  <td className="py-2 px-3 text-right text-orange-600">{r['FedAvg MAE'].toFixed(4)}</td>
                  <td className="py-2 px-3 text-right font-bold text-blue-700">{r['Personalized MAE'].toFixed(4)}</td>
                  <td className="py-2 px-3 text-right font-bold text-slate-900 font-sans">±{r['Personalized Spaces'].toFixed(1)}</td>
                  <td className="py-2 px-3 text-right font-bold text-emerald-600 font-sans">
                    +{r['Personalization Gain (%)']}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
