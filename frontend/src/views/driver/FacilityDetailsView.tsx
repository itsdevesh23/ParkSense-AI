import React, { useState, useEffect } from 'react';
import { Facility, OccupancyStep } from '../../types';
import { api } from '../../api';
import { StatusBadge } from '../../components/StatusBadge';
import {
  ArrowLeft,
  MapPin,
  Clock,
  Zap,
  Accessibility,
  Building,
  TrendingUp,
  TrendingDown,
  Cpu,
  Heart,
  Calendar,
  AlertCircle,
  HelpCircle,
  BarChart2,
  RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

interface FacilityDetailsViewProps {
  facilityId: string;
  onBack: () => void;
  favorites: string[];
  onToggleFavorite: (facilityId: string) => void;
  onSelectFacility: (facilityId: string) => void;
}

export const FacilityDetailsView: React.FC<FacilityDetailsViewProps> = ({
  facilityId,
  onBack,
  favorites,
  onToggleFavorite,
  onSelectFacility,
}) => {
  const [allFacilities, setAllFacilities] = useState<Facility[]>([]);
  const [facility, setFacility] = useState<Facility | null>(null);
  const [timeline, setTimeline] = useState<OccupancyStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [metricUnit, setMetricUnit] = useState<'bays' | 'ratio'>('bays');

  useEffect(() => {
    const loadAll = async () => {
      try {
        const res = await api.getFacilities();
        setAllFacilities(res.facilities);
      } catch (e) {
        console.error(e);
      }
    };
    loadAll();
  }, []);

  useEffect(() => {
    if (!facilityId) return;
    const loadData = async () => {
      try {
        setLoading(true);
        const [facRes, occRes] = await Promise.all([
          api.getFacility(facilityId),
          api.getFacilityOccupancy(facilityId, 24),
        ]);
        setFacility(facRes);
        setTimeline(occRes.timeline || []);
      } catch (err) {
        console.error('Failed to load facility details', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [facilityId]);

  if (loading && !facility) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
          <p className="text-sm font-semibold text-slate-600">Loading facility telemetry & forecasts...</p>
        </div>
      </div>
    );
  }

  if (!facility) {
    return (
      <div className="bg-white rounded-xl p-8 border border-slate-200 text-center">
        <AlertCircle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-800">Facility Not Found</h3>
        <p className="text-xs text-slate-500 mt-1">Unable to locate parking facility identifier.</p>
        <button
          onClick={onBack}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold"
        >
          Return to Parking Map
        </button>
      </div>
    );
  }

  const isFavorite = favorites.includes(facility.id);

  // Formatted chart data based on selected unit
  const chartData = timeline.map((pt) => ({
    time: pt.time_label,
    'Actual Occupied': metricUnit === 'bays' ? pt.actual_occupied_bays : (1 - pt.actual_avail_ratio),
    'Actual Vacant': metricUnit === 'bays' ? pt.actual_vacant_bays : pt.actual_avail_ratio,
    '30m Forecast': metricUnit === 'bays' ? pt.pred_30m_bays : pt.pred_30m_ratio,
    '60m Forecast': metricUnit === 'bays' ? pt.pred_60m_bays : pt.pred_60m_ratio,
  }));

  return (
    <div className="space-y-6">
      {/* Navigation & Facility Quick Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-blue-600 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Parking Explorer
        </button>

        {/* Quick facility dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Switch Lot:</span>
          <select
            value={facility.id}
            onChange={(e) => onSelectFacility(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-3 py-1.5 font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {allFacilities.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.system_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Facility Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded uppercase tracking-wider">
                Client #{facility.client_index} • {facility.system_code}
              </span>
              <StatusBadge status={facility.status} />
              {facility.has_ev && (
                <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/50">
                  <Zap className="w-3.5 h-3.5 text-emerald-600" /> EV Fast Chargers
                </span>
              )}
              {facility.has_disabled && (
                <span className="inline-flex items-center gap-1 text-xs font-semibold text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-200/50">
                  <Accessibility className="w-3.5 h-3.5 text-sky-600" /> Accessible Bays
                </span>
              )}
            </div>

            <h1 className="text-2xl font-black text-slate-900 tracking-tight">{facility.name}</h1>
            <p className="text-slate-500 text-xs sm:text-sm flex items-center gap-1.5 mt-1">
              <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
              {facility.address}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onToggleFavorite(facility.id)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
                isFavorite
                  ? 'bg-rose-50 border-rose-300 text-rose-600 shadow-xs'
                  : 'bg-white border-slate-200 text-slate-600 hover:border-rose-300 hover:text-rose-600'
              }`}
            >
              <Heart className={`w-4 h-4 ${isFavorite ? 'fill-current text-rose-600' : ''}`} />
              {isFavorite ? 'Saved to Favorites' : 'Add to Favorites'}
            </button>
          </div>
        </div>

        {/* Quick specs strip */}
        <div className="mt-6 pt-5 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Hourly Tariff</span>
            <p className="text-sm font-bold text-slate-800 mt-0.5">{facility.hourly_rate}</p>
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Operating Hours</span>
            <p className="text-sm font-bold text-slate-800 mt-0.5 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {facility.opening_hours}
            </p>
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Operator Group</span>
            <p className="text-sm font-bold text-slate-800 mt-0.5 flex items-center gap-1">
              <Building className="w-3.5 h-3.5 text-slate-400" />
              {facility.operator}
            </p>
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">IoT Telemetry</span>
            <p className="text-sm font-bold text-emerald-600 mt-0.5 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              {facility.data_freshness}
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards: Live State, 30m Forecast, 60m Forecast */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Current Live State */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Live Sensor Telemetry
            </span>
            <div className="flex items-baseline justify-between">
              <h2 className="text-2xl font-black text-slate-900">{facility.vacant_bays} Bays Open</h2>
              <span className="text-xs font-bold text-slate-500">
                {facility.occupied_bays} / {facility.capacity} occupied
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mt-3 w-full bg-slate-100 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  facility.occupancy_pct >= 90
                    ? 'bg-rose-500'
                    : facility.occupancy_pct >= 70
                    ? 'bg-amber-500'
                    : 'bg-emerald-500'
                }`}
                style={{ width: `${facility.occupancy_pct}%` }}
              />
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Occupancy Ratio: <strong className="text-slate-700">{facility.occupancy_pct}%</strong></span>
            <span>Capacity: <strong className="text-slate-700">{facility.capacity} total bays</strong></span>
          </div>
        </div>

        {/* Card 2: 30-Minute AI Forecast */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50/60 rounded-2xl border border-blue-200/80 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-blue-700 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" /> +30 Min Horizon Forecast
              </span>
              <span className="text-[10px] bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded-full">
                Attention-LSTM
              </span>
            </div>

            <div className="flex items-baseline justify-between mt-1">
              <h2 className="text-2xl font-black text-blue-950">
                {facility.forecast_30m_bays} Vacant Bays
              </h2>
              <div className="flex items-center gap-1">
                {facility.trend_30m === 'increasing' ? (
                  <span className="inline-flex items-center text-xs font-bold text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded">
                    <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> +{Math.abs(facility.forecast_30m_bays - facility.vacant_bays)} bays
                  </span>
                ) : (
                  <span className="inline-flex items-center text-xs font-bold text-rose-700 bg-rose-100/80 px-2 py-0.5 rounded">
                    <TrendingDown className="w-3.5 h-3.5 mr-0.5" /> -{Math.abs(facility.forecast_30m_bays - facility.vacant_bays)} bays
                  </span>
                )}
              </div>
            </div>

            <p className="text-xs text-blue-800 mt-2 font-medium">
              Expected availability ratio: <strong>{(facility.forecast_30m_ratio * 100).toFixed(1)}%</strong>
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-blue-200/50 flex items-center justify-between text-[11px] text-blue-700">
            <span>Local Error: <strong>±{(facility.model_mae_ratio * 100).toFixed(2)}% MAE</strong></span>
            <span className="font-semibold text-emerald-700">Personalization: +{facility.personalization_gain_pct}%</span>
          </div>
        </div>

        {/* Card 3: 60-Minute AI Forecast */}
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50/60 rounded-2xl border border-indigo-200/80 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" /> +60 Min Horizon Forecast
              </span>
              <span className="text-[10px] bg-indigo-100 text-indigo-800 font-bold px-2 py-0.5 rounded-full">
                Attention-LSTM
              </span>
            </div>

            <div className="flex items-baseline justify-between mt-1">
              <h2 className="text-2xl font-black text-indigo-950">
                {facility.forecast_60m_bays} Vacant Bays
              </h2>
              <span className="text-xs font-bold text-indigo-700">
                {(facility.forecast_60m_ratio * 100).toFixed(1)}% free
              </span>
            </div>

            <p className="text-xs text-indigo-800 mt-2 font-medium">
              Estimated turnover shift: <strong>{facility.forecast_60m_bays - facility.vacant_bays > 0 ? '+' : ''}{facility.forecast_60m_bays - facility.vacant_bays} bays</strong> relative to current
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-indigo-200/50 flex items-center justify-between text-[11px] text-indigo-700">
            <span>Forecast Target: <strong>t+2 (60 min ahead)</strong></span>
            <span className="font-semibold text-indigo-900">Pooled MAE: 0.0717</span>
          </div>
        </div>
      </div>

      {/* Chronological Actual vs Forecast Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="inline-flex items-center gap-1 text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
              <BarChart2 className="w-3.5 h-3.5 text-blue-600" />
              Chronological Time Series (Replay Window)
            </div>
            <h3 className="text-base font-bold text-slate-900">
              Actual Occupancy vs. Federated Attention-LSTM Predictions
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Evaluating true sensor observations against multi-step model predictions across continuous test timestamps.
            </p>
          </div>

          {/* Unit Toggle: Bays vs Ratio */}
          <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50 self-start sm:self-auto">
            <button
              onClick={() => setMetricUnit('bays')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                metricUnit === 'bays'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Physical Spaces (Bays)
            </button>
            <button
              onClick={() => setMetricUnit('ratio')}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                metricUnit === 'ratio'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Availability Ratio [0, 1]
            </button>
          </div>
        </div>

        {/* Recharts Container */}
        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
                domain={metricUnit === 'ratio' ? [0, 1] : ['auto', 'auto']}
                unit={metricUnit === 'ratio' ? '' : ' bays'}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="Actual Vacant"
                stroke="#10b981"
                strokeWidth={2.5}
                dot={{ r: 3 }}
                name="Actual Vacant"
              />
              <Line
                type="monotone"
                dataKey="30m Forecast"
                stroke="#2563eb"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 2.5 }}
                name="30-min Predicted"
              />
              <Line
                type="monotone"
                dataKey="60m Forecast"
                stroke="#8b5cf6"
                strokeWidth={2}
                strokeDasharray="2 2"
                dot={{ r: 2.5 }}
                name="60-min Predicted"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model & Privacy Notice */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-xs text-slate-600 flex items-start gap-3">
        <Cpu className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-800">Federated Edge Personalization Model</h4>
          <p className="mt-1 leading-relaxed">
            This facility runs an Attention-Based LSTM client model fine-tuned from the global Round-8 FedAvg checkpoint.
            By incorporating temporal self-attention across 4-step lookback streams, the personalized model reduces forecasting MAE by{' '}
            <strong className="text-emerald-700">{facility.personalization_gain_pct}%</strong> compared to non-personalized FedAvg,
            while maintaining local client partition isolation.
          </p>
        </div>
      </div>
    </div>
  );
};
