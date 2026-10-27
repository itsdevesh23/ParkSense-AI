import React, { useState, useEffect } from 'react';
import { api } from '../../api';
import {
  LineChart,
  BarChart3,
  Cpu,
  Layers,
  ArrowUpRight,
  TrendingDown,
  CheckCircle2,
  RefreshCw,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

export const OwnerAnalyticsView: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [metricUnit, setMetricUnit] = useState<'spaces' | 'ratio'>('spaces');

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.getOwnerAnalytics();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading && !data) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-500">Loading forecast accuracy records...</p>
      </div>
    );
  }

  if (!data) return null;

  const lotRecords: any[] = data.lot_forecast_accuracy || [];

  const chartData = lotRecords.map((r) => ({
    name: r.name.replace(' Birmingham', '').replace(' Car Park', ''),
    'Centralized Attention': metricUnit === 'spaces' ? r.centralized_spaces : (r.centralized_mae * 100),
    'FedAvg (Global)': metricUnit === 'spaces' ? r.fedavg_spaces : (r.fedavg_mae * 100),
    'Personalized FedAvg': metricUnit === 'spaces' ? r.personalized_spaces : (r.personalized_mae * 100),
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
            <LineChart className="w-4 h-4" />
            Accuracy Evaluation
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Fleet Forecast Accuracy Analytics
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Compare centralized models against decentralized FedAvg and local personalization gains.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Unit Toggle */}
          <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
            <button
              onClick={() => setMetricUnit('spaces')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                metricUnit === 'spaces'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Mean Spaces Error (bays)
            </button>
            <button
              onClick={() => setMetricUnit('ratio')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                metricUnit === 'ratio'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              MAE Ratio (%)
            </button>
          </div>

          <button
            onClick={fetchAnalytics}
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors"
            title="Refresh analytics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Model Benchmark Comparison Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Pooled Baseline Error (FedAvg)
          </span>
          <p className="text-2xl font-black text-slate-900 mt-1">
            0.1007 <span className="text-xs text-slate-500 font-normal">MAE ratio</span>
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Global non-personalized weights evaluated after 8 rounds.
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-blue-200 p-5 shadow-xs bg-blue-50/30">
          <span className="text-[11px] font-bold text-blue-600 uppercase tracking-wider">
            Personalized FedAvg Error
          </span>
          <p className="text-2xl font-black text-blue-900 mt-1">
            0.0607 <span className="text-xs text-blue-600 font-normal">MAE ratio</span>
          </p>
          <p className="text-xs text-blue-700 mt-1">
            Local edge fine-tuning achieves <strong className="text-emerald-700 font-bold">39.7% lower error</strong>.
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Between-Lot Dispersion (Std Dev)
          </span>
          <p className="text-2xl font-black text-slate-900 mt-1">
            0.0276 <span className="text-xs text-slate-500 font-normal">σ</span>
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Variance across facilities cut by 48.0% (down from 0.0531).
          </p>
        </div>
      </div>

      {/* Comparative Bar Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-600" />
            Model Accuracy Comparison Across Managed Facilities
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Comparing Centralized Attention-LSTM vs. Global FedAvg vs. Personalized FedAvg ({metricUnit === 'spaces' ? 'Spaces in Bays' : 'MAE Ratio %'}). Lower is better.
          </p>
        </div>

        <div className="h-80 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" />
              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
                unit={metricUnit === 'spaces' ? ' bays' : '%'}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="Centralized Attention" fill="#94a3b8" radius={[4, 4, 0, 0]} name="Centralized Attention-LSTM" />
              <Bar dataKey="FedAvg (Global)" fill="#f97316" radius={[4, 4, 0, 0]} name="FedAvg Global (Round 8)" />
              <Bar dataKey="Personalized FedAvg" fill="#2563eb" radius={[4, 4, 0, 0]} name="Personalized FedAvg (Proposed)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Lot-by-Lot Audit Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Facility Breakdown Table</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Detailed performance breakdown for all facilities in your portfolio.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                <th className="py-2.5 px-3">Facility</th>
                <th className="py-2.5 px-3 text-right">Capacity</th>
                <th className="py-2.5 px-3 text-right">Centralized MAE</th>
                <th className="py-2.5 px-3 text-right">FedAvg MAE</th>
                <th className="py-2.5 px-3 text-right">Personalized MAE</th>
                <th className="py-2.5 px-3 text-right">Mean Error (Bays)</th>
                <th className="py-2.5 px-3 text-right">Gain (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {lotRecords.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3">
                    <span className="font-bold text-slate-900">{r.name}</span>
                    <span className="block text-[10px] text-slate-400 font-mono">Client #{r.client_index}</span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-medium text-slate-700">{r.capacity}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-600">{(r.centralized_mae * 100).toFixed(2)}%</td>
                  <td className="py-2.5 px-3 text-right font-mono text-orange-600">{(r.fedavg_mae * 100).toFixed(2)}%</td>
                  <td className="py-2.5 px-3 text-right font-mono font-bold text-blue-700">{(r.personalized_mae * 100).toFixed(2)}%</td>
                  <td className="py-2.5 px-3 text-right font-bold text-slate-900">±{r.personalized_spaces.toFixed(1)} bays</td>
                  <td className="py-2.5 px-3 text-right font-extrabold text-emerald-600">+{r.gain_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
