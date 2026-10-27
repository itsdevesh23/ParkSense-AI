import React, { useState, useEffect } from 'react';
import { Facility, OccupancyStep } from '../../types';
import { api } from '../../api';
import {
  TrendingUp,
  TrendingDown,
  Cpu,
  Layers,
  Sparkles,
  ArrowRight,
  Clock,
  Compass,
  AlertTriangle,
  CheckCircle2,
  Table as TableIcon
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area
} from 'recharts';

interface ForecastExplorerViewProps {
  onSelectFacility: (id: string) => void;
}

export const ForecastExplorerView: React.FC<ForecastExplorerViewProps> = ({
  onSelectFacility,
}) => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [selectedFacilityId, setSelectedFacilityId] = useState<string>('');
  const [horizon, setHorizon] = useState<30 | 60>(30);
  const [timeline, setTimeline] = useState<OccupancyStep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        setLoading(true);
        const res = await api.getFacilities();
        setFacilities(res.facilities);
        if (res.facilities.length > 0) {
          setSelectedFacilityId(res.facilities[0].id);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  useEffect(() => {
    if (!selectedFacilityId) return;
    const fetchTimeline = async () => {
      try {
        const res = await api.getFacilityOccupancy(selectedFacilityId, 24);
        setTimeline(res.timeline || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchTimeline();
  }, [selectedFacilityId]);

  const currentFacility = facilities.find((f) => f.id === selectedFacilityId) || facilities[0];

  const chartData = timeline.map((pt) => ({
    time: pt.time_label,
    Actual: horizon === 30 ? pt.actual_vacant_bays : pt.actual_vacant_bays,
    Predicted: horizon === 30 ? pt.pred_30m_bays : pt.pred_60m_bays,
    'Absolute Error': horizon === 30 ? pt.error_30m_bays : pt.error_60m_bays,
  }));

  const targetVacant = horizon === 30
    ? currentFacility?.forecast_30m_bays ?? 0
    : currentFacility?.forecast_60m_bays ?? 0;

  const currentVacant = currentFacility?.vacant_bays ?? 0;
  const netDelta = targetVacant - currentVacant;

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
          <Sparkles className="w-3.5 h-3.5 text-blue-500" />
          Predictive Deep Learning Laboratory
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          Smart Parking Forecast Explorer
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Simulate multi-step forward lookahead dynamics with Attention-LSTM temporal self-attention weights.
        </p>
      </div>

      {/* Control Strip: Lot Selector + Horizon Toggle */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Lot selector */}
        <div className="flex-1 max-w-md">
          <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
            Target Parking Facility
          </label>
          <select
            value={selectedFacilityId}
            onChange={(e) => setSelectedFacilityId(e.target.value)}
            className="w-full text-xs font-bold bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {facilities.map((fac) => (
              <option key={fac.id} value={fac.id}>
                Client #{fac.client_index} — {fac.name} (Cap: {fac.capacity} bays)
              </option>
            ))}
          </select>
        </div>

        {/* Horizon selector */}
        <div>
          <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
            Forecast Horizon (Lookahead)
          </label>
          <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
            <button
              onClick={() => setHorizon(30)}
              className={`px-4 py-2 rounded-md text-xs font-bold transition-all flex items-center gap-1.5 ${
                horizon === 30
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              +30 Minutes (t+1)
            </button>
            <button
              onClick={() => setHorizon(60)}
              className={`px-4 py-2 rounded-md text-xs font-bold transition-all flex items-center gap-1.5 ${
                horizon === 60
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              +60 Minutes (t+2)
            </button>
          </div>
        </div>
      </div>

      {/* Model Architecture Info & Turnover Summary */}
      {currentFacility && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Turnover Summary Card */}
          <div className="md:col-span-2 bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-6 shadow-md relative overflow-hidden flex flex-col justify-between">
            <div className="relative z-10">
              <span className="text-[11px] font-bold text-blue-300 uppercase tracking-wider">
                Automated Turnover Synthesis
              </span>
              <h2 className="text-xl font-bold mt-1">
                {netDelta >= 0 ? (
                  <span className="text-emerald-400 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" /> Vacancies Expanding (+{netDelta} bays)
                  </span>
                ) : (
                  <span className="text-rose-400 flex items-center gap-2">
                    <TrendingDown className="w-5 h-5" /> High Demand Surge ({netDelta} bays)
                  </span>
                )}
              </h2>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                At <strong className="text-white">{currentFacility.name}</strong>, current availability is{' '}
                <strong className="text-white">{currentVacant} bays</strong>. The Attention-LSTM model predicts{' '}
                <strong className="text-white">{targetVacant} open bays</strong> in {horizon} minutes.
                {netDelta < 0
                  ? ' Commuters should plan to arrive within the next 15–20 minutes to secure parking before capacity tightens.'
                  : ' Ample spots are expected to open up as earlier vehicles depart their sessions.'}
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-white/10 grid grid-cols-3 gap-3 text-xs relative z-10">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Current Vacant</span>
                <span className="text-base font-extrabold text-white">{currentVacant} bays</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Predicted in {horizon}m</span>
                <span className="text-base font-extrabold text-blue-300">{targetVacant} bays</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Net Shift</span>
                <span className={`text-base font-extrabold ${netDelta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {netDelta > 0 ? `+${netDelta}` : netDelta} bays
                </span>
              </div>
            </div>
          </div>

          {/* Model Metrics Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
                Model Evaluation Context
              </span>
              <h3 className="text-sm font-bold text-slate-800">
                Client #{currentFacility.client_index} Weights
              </h3>

              <div className="mt-3 space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Architecture</span>
                  <span className="font-semibold text-slate-800">Attention-LSTM</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Lookback Window</span>
                  <span className="font-semibold text-slate-800">4 steps (2 hrs)</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Local Test MAE</span>
                  <span className="font-semibold text-blue-600">
                    ±{(currentFacility.model_mae_ratio * 100).toFixed(2)}% ratio
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Mean Space Error</span>
                  <span className="font-semibold text-slate-800">
                    ±{currentFacility.model_mae_spaces.toFixed(1)} bays
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Personalization Gain</span>
                  <span className="font-bold text-emerald-600">
                    +{currentFacility.personalization_gain_pct}%
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => onSelectFacility(currentFacility.id)}
              className="mt-4 w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5"
            >
              Full Facility View
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Actual vs Forecast Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            {horizon}-Minute Ahead Lookahead Curve
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Synchronized plot of ground-truth observations vs. multi-step Attention-LSTM outputs over time.
          </p>
        </div>

        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} unit=" bays" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="Actual"
                stroke="#10b981"
                strokeWidth={2.5}
                dot={{ r: 3 }}
                name="Actual Vacant (Ground Truth)"
              />
              <Line
                type="monotone"
                dataKey="Predicted"
                stroke="#2563eb"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 2.5 }}
                name={`Predicted (${horizon}m Horizon)`}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Residual Error Area Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Pointwise Residuals (|Actual - Predicted| in bays)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Tracking individual observation deviations to verify tight bounds and absence of systematic bias.
          </p>
        </div>

        <div className="h-48 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} unit=" bays" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Area
                type="monotone"
                dataKey="Absolute Error"
                stroke="#f59e0b"
                fill="#fef3c7"
                strokeWidth={2}
                name="Residual Error (bays)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Evaluation Sample Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <TableIcon className="w-4 h-4 text-blue-600" />
              Test Observation Ledger ({timeline.length} Steps)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Raw verification numbers from chronological evaluation partition.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                <th className="py-2.5 px-3">Step</th>
                <th className="py-2.5 px-3">Time</th>
                <th className="py-2.5 px-3 text-right">Actual Vacant</th>
                <th className="py-2.5 px-3 text-right">Forecast ({horizon}m)</th>
                <th className="py-2.5 px-3 text-right">Absolute Residual</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {timeline.slice(0, 10).map((row) => {
                const actual = horizon === 30 ? row.actual_vacant_bays : row.actual_vacant_bays;
                const pred = horizon === 30 ? row.pred_30m_bays : row.pred_60m_bays;
                const err = horizon === 30 ? row.error_30m_bays : row.error_60m_bays;
                return (
                  <tr key={row.step_index} className="hover:bg-slate-50">
                    <td className="py-2 px-3 font-mono text-slate-500">#{row.step_index}</td>
                    <td className="py-2 px-3 font-semibold text-slate-800">{row.time_label}</td>
                    <td className="py-2 px-3 text-right font-bold text-slate-900">{actual} bays</td>
                    <td className="py-2 px-3 text-right font-bold text-blue-600">{pred} bays</td>
                    <td className="py-2 px-3 text-right font-mono font-medium text-amber-700">{err} bays</td>
                    <td className="py-2 px-3 text-center">
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500" /> Replayed
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
