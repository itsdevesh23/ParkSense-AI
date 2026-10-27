import React, { useState, useEffect } from 'react';
import { Facility } from '../../types';
import { api } from '../../api';
import { MetricCard } from '../../components/MetricCard';
import { StatusBadge } from '../../components/StatusBadge';
import {
  Building2,
  Users,
  Car,
  TrendingUp,
  AlertTriangle,
  Clock,
  ArrowRight,
  ShieldCheck,
  Download,
  BarChart3,
  RefreshCw
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

interface OwnerOverviewViewProps {
  onNavigateToFacilities: () => void;
  onNavigateToAnalytics: () => void;
  onNavigateToReports: () => void;
}

export const OwnerOverviewView: React.FC<OwnerOverviewViewProps> = ({
  onNavigateToFacilities,
  onNavigateToAnalytics,
  onNavigateToReports,
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const res = await api.getOwnerOverview();
      setData(res);
    } catch (err) {
      console.error('Failed to load owner overview', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  if (loading && !data) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-500">Loading operator dashboard & facility metrics...</p>
      </div>
    );
  }

  if (!data) return null;

  const facilities: Facility[] = data.facilities || [];
  const alerts: any[] = data.alerts || [];

  const chartData = facilities.map((f) => ({
    name: f.name.replace(' Birmingham', '').replace(' Car Park', ''),
    Capacity: f.capacity,
    Occupied: f.occupied_bays,
    '30m Pred Free': f.forecast_30m_bays,
  }));

  return (
    <div className="space-y-6">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
            <Building2 className="w-4 h-4" />
            Facility Operations Command
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Operator Fleet Overview</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time management portal for assigned Birmingham municipal & commercial parking decks.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onNavigateToReports}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export Data
          </button>
          <button
            onClick={fetchOverview}
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors"
            title="Refresh fleet telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Assigned Facilities"
          value={`${data.assigned_facilities_count} Lots`}
          subtitle={`Total capacity: ${data.total_capacity.toLocaleString()} bays`}
          trend={{ direction: 'neutral', label: 'Managed fleet' }}
          icon={Building2}
          accentColor="blue"
        />
        <MetricCard
          title="Currently Occupied"
          value={`${data.total_occupied.toLocaleString()} Bays`}
          subtitle={`${data.avg_occupancy_pct}% aggregate fleet load`}
          trend={{ direction: 'up', label: 'Live telemetry' }}
          icon={Car}
          accentColor="amber"
        />
        <MetricCard
          title="Vacant Right Now"
          value={`${data.total_vacant.toLocaleString()} Bays`}
          subtitle="Available for arriving commuters"
          trend={{ direction: 'down', label: 'Real-time open' }}
          icon={Users}
          accentColor="emerald"
        />
        <MetricCard
          title="30-min AI Projected Free"
          value={`${data.forecast_30m_total_vacant.toLocaleString()} Bays`}
          subtitle="Attention-LSTM federated forecast"
          trend={{ direction: 'neutral', label: 'Lookahead t+1' }}
          icon={TrendingUp}
          accentColor="indigo"
        />
      </div>

      {/* Real-Time Operational Alerts */}
      {alerts.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <h3 className="text-xs font-bold text-amber-900 uppercase tracking-wide">
              Active Operational Alerts ({alerts.length})
            </h3>
          </div>
          <div className="space-y-1.5">
            {alerts.map((alt: any, idx: number) => (
              <div key={idx} className="flex items-start justify-between text-xs text-amber-800 bg-white/70 p-2 rounded-lg border border-amber-100">
                <span className="font-semibold">{alt.facility_name}: {alt.message}</span>
                <span className="text-[10px] text-amber-600 font-mono shrink-0 ml-2">{alt.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fleet Capacity vs Occupancy Bar Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              Fleet Capacity, Current Occupancy & 30-min Forecast
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Comparative profile across all managed parking decks in your operator portfolio.
            </p>
          </div>
          <button
            onClick={onNavigateToAnalytics}
            className="text-xs font-bold text-blue-600 hover:text-blue-700 inline-flex items-center gap-1 self-start sm:self-auto"
          >
            Deep-Dive Accuracy
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="h-80 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" />
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
              <Bar dataKey="Capacity" fill="#cbd5e1" radius={[4, 4, 0, 0]} name="Total Capacity" />
              <Bar dataKey="Occupied" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Occupied Bays" />
              <Bar dataKey="30m Pred Free" fill="#10b981" radius={[4, 4, 0, 0]} name="30m Pred Vacant" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Managed Facilities Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Assigned Facility Roster</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Live statuses and forecast outputs for lots linked to your operator role.
            </p>
          </div>
          <button
            onClick={onNavigateToFacilities}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-bold transition-colors"
          >
            Manage Configurations
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                <th className="py-2.5 px-3">Facility</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Capacity</th>
                <th className="py-2.5 px-3 text-right">Current Occupied</th>
                <th className="py-2.5 px-3 text-right">Available Now</th>
                <th className="py-2.5 px-3 text-right">30m Forecast</th>
                <th className="py-2.5 px-3 text-right">Tariff</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {facilities.map((fac) => (
                <tr key={fac.id} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3">
                    <div className="font-bold text-slate-900">{fac.name}</div>
                    <div className="text-[10px] text-slate-400 font-mono">{fac.system_code} • Client #{fac.client_index}</div>
                  </td>
                  <td className="py-2.5 px-3">
                    <StatusBadge status={fac.status} />
                  </td>
                  <td className="py-2.5 px-3 text-right font-medium text-slate-700">{fac.capacity} bays</td>
                  <td className="py-2.5 px-3 text-right font-bold text-slate-900">
                    {fac.occupied_bays} <span className="text-slate-400 font-normal">({fac.occupancy_pct}%)</span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-extrabold text-emerald-600">{fac.vacant_bays} bays</td>
                  <td className="py-2.5 px-3 text-right font-bold text-blue-600">{fac.forecast_30m_bays} bays</td>
                  <td className="py-2.5 px-3 text-right font-semibold text-slate-700">{fac.hourly_rate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
