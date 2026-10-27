import React, { useState, useEffect } from 'react';
import { api } from '../../api';
import { MetricCard } from '../../components/MetricCard';
import {
  Globe,
  Cpu,
  Database,
  BarChart3,
  ShieldCheck,
  CheckCircle2,
  TrendingUp,
  ArrowRight,
  Layers,
  Server,
  Zap,
  RefreshCw,
  GitBranch
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

interface AdminOverviewViewProps {
  onNavigateToFederated: () => void;
  onNavigateToBenchmarks: () => void;
  onNavigateToRegistry: () => void;
  onNavigateToAudit: () => void;
}

export const AdminOverviewView: React.FC<AdminOverviewViewProps> = ({
  onNavigateToFederated,
  onNavigateToBenchmarks,
  onNavigateToRegistry,
  onNavigateToAudit,
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminOverview();
      setData(res);
    } catch (err) {
      console.error(err);
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
        <p className="text-xs font-semibold text-slate-500">Loading system administration metrics...</p>
      </div>
    );
  }

  if (!data) return null;

  // 30-min primary benchmark leaderboard data
  const leaderboardData = [
    { name: 'XGBoost (Cent)', mae: 0.0145, spaces: 13.9, type: 'Centralized' },
    { name: 'ARIMA (Cent)', mae: 0.0168, spaces: 15.6, type: 'Centralized' },
    { name: 'Attn-LSTM (Cent)', mae: 0.0217, spaces: 18.2, type: 'Centralized' },
    { name: 'Std LSTM (Cent)', mae: 0.0218, spaces: 18.4, type: 'Centralized' },
    { name: 'Pers. FedAvg', mae: 0.0607, spaces: 47.7, type: 'Federated' },
    { name: 'FedAvg (Global)', mae: 0.1007, spaces: 79.1, type: 'Federated' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-blue-200 text-xs font-semibold backdrop-blur-xs mb-3">
            <Globe className="w-3.5 h-3.5 text-blue-400" />
            Global System Command & Research Evaluation Lab
          </div>
          <h1 className="text-2xl md:text-3xl font-black tracking-tight">
            ParkSense AI Architecture Telemetry
          </h1>
          <p className="mt-2 text-slate-300 text-sm leading-relaxed">
            Federated Multi-Lot Smart Parking Forecasting using Attention-Based LSTM on IoT Streams.
            Coordinating 30 edge client partitions, FedAvg central aggregation, and decentralized edge personalization.
          </p>
        </div>
      </div>

      {/* Global KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Edge Client Fleet"
          value="30 Facilities"
          subtitle="Independent client partitions"
          trend={{ direction: 'neutral', label: '100% Online' }}
          icon={Cpu}
          accentColor="blue"
        />
        <MetricCard
          title="Dataset Ingestion"
          value="35,717 Records"
          subtitle="Birmingham IoT stream archive"
          trend={{ direction: 'neutral', label: 'Sanitized' }}
          icon={Database}
          accentColor="emerald"
        />
        <MetricCard
          title="Unified Test Partition"
          value="3,293 Samples"
          subtitle="Identical test set across all 6 models"
          trend={{ direction: 'neutral', label: 'Zero Leakage' }}
          icon={ShieldCheck}
          accentColor="indigo"
        />
        <MetricCard
          title="FL Convergence"
          value="8 Rounds"
          subtitle="39.7% error drop via personalization"
          trend={{ direction: 'up', label: 'Converged' }}
          icon={GitBranch}
          accentColor="amber"
        />
      </div>

      {/* Architecture Overview Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card 1: Decentralized FL Overview */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Federated Learning Subsystem
              </span>
              <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                FedAvg Active
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900">Decentralized Multi-Lot Training</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              30 autonomous parking facility clients perform 2 local epochs of Attention-LSTM gradient updates per round,
              transmitting only neural weights to the central coordinator.
            </p>

            <div className="mt-4 space-y-2 bg-slate-50 rounded-xl p-3 text-xs border border-slate-100">
              <div className="flex justify-between">
                <span className="text-slate-500">Global Communication Rounds:</span>
                <span className="font-bold text-slate-800">8 Rounds</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Local Epochs (E):</span>
                <span className="font-bold text-slate-800">2 Epochs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Batch Size (B):</span>
                <span className="font-bold text-slate-800">32</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Personalization Gain:</span>
                <span className="font-extrabold text-emerald-600">+39.7% Error Reduction</span>
              </div>
            </div>
          </div>

          <button
            onClick={onNavigateToFederated}
            className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-xs"
          >
            Open Federated Monitor
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 2: 6-Model Benchmark Summary */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Rigorous Evaluation Lab
              </span>
              <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                N = 3,293
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900">Six-Model Benchmark Suite</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Standardized comparison across ARIMA, XGBoost, Standard LSTM, Centralized Attention-LSTM, FedAvg, and Personalized FedAvg at both 30m and 60m horizons.
            </p>

            <div className="mt-4 space-y-2 bg-slate-50 rounded-xl p-3 text-xs border border-slate-100">
              <div className="flex justify-between">
                <span className="text-slate-500">Best Centralized (30m):</span>
                <span className="font-bold text-slate-800">XGBoost (0.0145 MAE)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Best Decentralized (30m):</span>
                <span className="font-bold text-blue-700">Pers. FedAvg (0.0607 MAE)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Standard LSTM (30m):</span>
                <span className="font-bold text-slate-800">0.0218 MAE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Centralized Attention-LSTM:</span>
                <span className="font-bold text-slate-800">0.0217 MAE</span>
              </div>
            </div>
          </div>

          <button
            onClick={onNavigateToBenchmarks}
            className="mt-4 w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5"
          >
            Examine Benchmark Tables
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 3: Data Quality & Audit */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Integrity & Governance
              </span>
              <span className="text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                385 Clipped
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900">Dataset Ingestion Audit</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Full provenance audit across 35,717 raw readings, resolving 12 negative counts and 373 capacity overfills without data truncation or time warping.
            </p>

            <div className="mt-4 space-y-2 bg-slate-50 rounded-xl p-3 text-xs border border-slate-100">
              <div className="flex justify-between">
                <span className="text-slate-500">Negative Values Cleaned:</span>
                <span className="font-bold text-slate-800">12 (NIA North)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Over-Capacity Clipped:</span>
                <span className="font-bold text-slate-800">373 observations</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Daily Sampling Frequency:</span>
                <span className="font-bold text-slate-800">18 points/day</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Test Split Integrity:</span>
                <span className="font-extrabold text-emerald-600">Chronological (15%)</span>
              </div>
            </div>
          </div>

          <button
            onClick={onNavigateToAudit}
            className="mt-4 w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5"
          >
            Review Audit Trail
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Primary 6-Model Benchmark Leaderboard Bar Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-600" />
            30-Minute Horizon Model Leaderboard (Pooled MAE Ratio)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluated on all 3,293 unified test observations across all 30 parking lots (lower is better).
          </p>
        </div>

        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={leaderboardData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
                formatter={(val: any) => [`${val} MAE Ratio`, 'Error']}
              />
              <Bar dataKey="mae" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Pooled MAE Ratio" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
