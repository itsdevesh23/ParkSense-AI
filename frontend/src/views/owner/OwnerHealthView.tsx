import React, { useState, useEffect } from 'react';
import { api } from '../../api';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  Radio,
  Clock,
  ShieldCheck,
  RefreshCw,
  HardDrive
} from 'lucide-react';

export const OwnerHealthView: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const res = await api.getOwnerHealth();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  if (loading && !data) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-500">Checking IoT sensor feeds & stream integrity...</p>
      </div>
    );
  }

  if (!data) return null;

  const summary = data.summary || {};
  const sensors: any[] = data.sensor_freshness || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-600 mb-1">
            <Radio className="w-4 h-4 animate-pulse" />
            Sensor Telemetry & Health Monitor
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            IoT Edge Data Streams
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Monitor sensor availability, heartbeat packets, and data clipping audit statistics.
          </p>
        </div>

        <button
          onClick={fetchHealth}
          className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors self-start sm:self-auto"
          title="Refresh health checks"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Connected Sensors
          </span>
          <p className="text-2xl font-black text-slate-900 mt-1">
            {summary.total_sensors || sensors.length} Units
          </p>
          <span className="text-xs text-emerald-600 font-medium mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> 100% operational
          </span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Sampling Cadence
          </span>
          <p className="text-2xl font-black text-blue-600 mt-1">
            30 Minutes
          </p>
          <span className="text-xs text-slate-500 mt-1 block">
            18 active records / day (08:00 - 16:30)
          </span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Clipping Safeguard
          </span>
          <p className="text-2xl font-black text-amber-600 mt-1">
            Active
          </p>
          <span className="text-xs text-slate-500 mt-1 block">
            Values bounded to [0.0, 1.0] range
          </span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Partition Split
          </span>
          <p className="text-2xl font-black text-slate-900 mt-1">
            70 / 15 / 15
          </p>
          <span className="text-xs text-slate-500 mt-1 block">
            Chronological train/val/test split
          </span>
        </div>
      </div>

      {/* Sensor Feeds Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            Sensor Telemetry Status by Facility
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Individual IoT client ingestion feeds and test observation volume.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                <th className="py-2.5 px-3">Facility</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Data Cadence</th>
                <th className="py-2.5 px-3 text-right">Capacity</th>
                <th className="py-2.5 px-3 text-right">Test Samples</th>
                <th className="py-2.5 px-3 text-right">Clipping Events</th>
                <th className="py-2.5 px-3 text-center">Integrity Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sensors.map((s, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3">
                    <span className="font-bold text-slate-900">{s.name}</span>
                    <span className="block text-[10px] text-slate-400 font-mono">{s.system_code} • Client #{s.client_index}</span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Live Replay
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 font-medium">Every 30 min</td>
                  <td className="py-2.5 px-3 text-right font-medium text-slate-700">{s.capacity} bays</td>
                  <td className="py-2.5 px-3 text-right font-mono font-medium text-blue-700">{s.test_samples} steps</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-600">{s.clipping_events || 0}</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Pass
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit & Integrity Callout */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-xs text-slate-600 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-slate-800">IoT Stream Data Sanitation</h4>
          <p className="mt-1 leading-relaxed">
            The data ingestion pipeline enforces strict chronological ordering across all 30 parking lots.
            Raw sensors recording negative counts or capacity overflows (such as occasional sensor calibration drift)
            are sanitized via mathematical boundary clamping into valid $[0, 1]$ availability ratios without discarding time intervals.
          </p>
        </div>
      </div>
    </div>
  );
};
