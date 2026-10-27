import React, { useState, useEffect } from 'react';
import { BenchmarkModel } from '../../types';
import { api } from '../../api';
import {
  BarChart3,
  Award,
  CheckCircle2,
  TrendingDown,
  Clock,
  Layers,
  ArrowRight,
  ShieldAlert,
  Info,
  RefreshCw,
  FileSpreadsheet
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

export const AdminBenchmarksView: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [horizonTab, setHorizonTab] = useState<'both' | '30' | '60'>('both');

  const fetchBenchmarks = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminBenchmarks('both');
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  if (loading && !data) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-500">Loading verified multi-model benchmark records...</p>
      </div>
    );
  }

  if (!data) return null;

  const bench30: BenchmarkModel[] = data.benchmark_30min || [];
  const bench60: BenchmarkModel[] = data.benchmark_60min || [];

  // Comparison chart data combining both horizons
  const comparisonData = bench30.map((m30) => {
    const m60 = bench60.find((m) => m.Model === m30.Model);
    return {
      model: m30.Model.replace('Attention-', 'Attn-').replace('Personalized ', 'Pers. '),
      '30m MAE': m30['Pooled MAE (Micro, Ratio)'],
      '60m MAE': m60 ? m60['Pooled MAE (Micro, Ratio)'] : 0,
      '30m Bays': m30['Mean Space Error (bays)'],
      '60m Bays': m60 ? m60['Mean Space Error (bays)'] : 0,
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
            <BarChart3 className="w-4 h-4" />
            Official Research Benchmark Suite
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Six-Model Benchmark Evaluation Lab
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Strict empirical evaluation across 30 parking lots on identical N = 3,293 test observations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Tab selector */}
          <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
            <button
              onClick={() => setHorizonTab('both')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                horizonTab === 'both' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Both Horizons
            </button>
            <button
              onClick={() => setHorizonTab('30')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                horizonTab === '30' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              30-min (t+1)
            </button>
            <button
              onClick={() => setHorizonTab('60')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                horizonTab === '60' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              60-min (t+2)
            </button>
          </div>

          <button
            onClick={fetchBenchmarks}
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors"
            title="Reload benchmarks"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Comparative Bar Chart: MAE Ratio Across Both Horizons */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Pooled MAE Ratio Comparison (30-min vs 60-min Horizons)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Lower MAE represents tighter forecasting bounds. Centralized models maintain absolute lead; personalization closes 40% of the federated performance gap.
          </p>
        </div>

        <div className="h-80 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData} margin={{ top: 15, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="model" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="30m MAE" fill="#3b82f6" radius={[4, 4, 0, 0]} name="30-min MAE (t+1)" />
              <Bar dataKey="60m MAE" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="60-min MAE (t+2)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 30-Minute Benchmark Table */}
      {(horizonTab === 'both' || horizonTab === '30') && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
                <Clock className="w-3.5 h-3.5" /> Horizon 1: 30-min ahead (y30 / t+1)
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Primary 30-Minute Forecasting Benchmark Table
              </h3>
            </div>
            <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg font-mono">
              N = 3,293 instances
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3 text-right">Pooled MAE (Ratio)</th>
                  <th className="py-2.5 px-3 text-right">Pooled RMSE (Ratio)</th>
                  <th className="py-2.5 px-3 text-right">Macro Mean MAE</th>
                  <th className="py-2.5 px-3 text-right">Between-Lot Std (σ)</th>
                  <th className="py-2.5 px-3 text-right">Mean Space Error (bays)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {bench30.map((m) => (
                  <tr
                    key={m.Model}
                    className={`hover:bg-slate-50 ${
                      m.Model.includes('Personalized')
                        ? 'bg-blue-50/40 font-semibold'
                        : m.Model === 'XGBoost'
                        ? 'bg-emerald-50/30'
                        : ''
                    }`}
                  >
                    <td className="py-2.5 px-3 font-sans font-bold text-slate-900 flex items-center gap-2">
                      {m.Model}
                      {m.Model === 'XGBoost' && (
                        <span className="font-sans text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                          Best Centralized
                        </span>
                      )}
                      {m.Model.includes('Personalized') && (
                        <span className="font-sans text-[10px] font-bold text-blue-700 bg-blue-100 px-1.5 py-0.5 rounded">
                          Best Federated
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-slate-900">
                      {m['Pooled MAE (Micro, Ratio)']}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {m['Pooled RMSE (Ratio)']}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {m['Macro Mean MAE (Ratio)']}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {m['Between-Lot Std (sigma)']}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-indigo-700">
                      ±{m['Mean Space Error (bays)']} bays
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 60-Minute Benchmark Table */}
      {(horizonTab === 'both' || horizonTab === '60') && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 mb-1">
                <Clock className="w-3.5 h-3.5" /> Horizon 2: 60-min ahead (y60 / t+2)
              </div>
              <h3 className="text-base font-bold text-slate-900">
                Secondary 60-Minute Forecasting Benchmark Table
              </h3>
            </div>
            <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg font-mono">
              N = 3,293 instances
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3 text-right">Pooled MAE (Ratio)</th>
                  <th className="py-2.5 px-3 text-right">Pooled RMSE (Ratio)</th>
                  <th className="py-2.5 px-3 text-right">Macro Mean MAE</th>
                  <th className="py-2.5 px-3 text-right">Between-Lot Std (σ)</th>
                  <th className="py-2.5 px-3 text-right">Mean Space Error (bays)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {bench60.map((m) => (
                  <tr
                    key={m.Model}
                    className={`hover:bg-slate-50 ${
                      m.Model.includes('Personalized')
                        ? 'bg-indigo-50/40 font-semibold'
                        : m.Model === 'XGBoost'
                        ? 'bg-emerald-50/30'
                        : ''
                    }`}
                  >
                    <td className="py-2.5 px-3 font-sans font-bold text-slate-900 flex items-center gap-2">
                      {m.Model}
                      {m.Model === 'XGBoost' && (
                        <span className="font-sans text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                          Best Centralized
                        </span>
                      )}
                      {m.Model.includes('Personalized') && (
                        <span className="font-sans text-[10px] font-bold text-indigo-700 bg-indigo-100 px-1.5 py-0.5 rounded">
                          Best Federated
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-slate-900">
                      {m['Pooled MAE (Micro, Ratio)']}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {m['Pooled RMSE (Ratio)']}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {m['Macro Mean MAE (Ratio)']}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-600">
                      {m['Between-Lot Std (sigma)']}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-indigo-700">
                      ±{m['Mean Space Error (bays)']} bays
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Rigorous Academic Discussion Box */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-xs text-slate-700 space-y-3">
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600" />
          Empirical Research Synthesis & Discussion
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <p>
              <strong className="text-slate-900">Centralized vs Federated Trade-Off:</strong> Centralized tree boosting (XGBoost) achieves the lowest error across both horizons (MAE 0.0145 at 30m, 0.0245 at 60m). However, centralized pipelines require continuous raw stream aggregation from all 30 municipal and commercial operators to a central datacenter.
            </p>
            <p>
              <strong className="text-slate-900">Convergence of Deep Sequence Models:</strong> Standard LSTM and Attention-LSTM centralized models achieve virtually identical MAE (0.0218 vs 0.0217 at 30m; 0.0291 vs 0.0290 at 60m), confirming the temporal self-attention layer successfully captures diurnal cyclicality.
            </p>
          </div>
          <div className="space-y-2">
            <p>
              <strong className="text-slate-900">Personalization Impact:</strong> Standard FedAvg yields 0.1007 MAE at 30m due to sharp client heterogeneity across 30 parking lots. Personalization reduces this to 0.0607 (39.7% reduction) while compressing cross-lot dispersion ($\sigma$) by 48.0% (0.0531 to 0.0276).
            </p>
            <p>
              <strong className="text-slate-900">ARIMA Safeguard Verification:</strong> Incorporating convergence safeguards into ARIMA ensures non-converged series fall back to persistence, achieving MAE 0.0168 at 30m and 0.0361 at 60m, definitively outperforming pure naive persistence (0.0257 and 0.0494).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
