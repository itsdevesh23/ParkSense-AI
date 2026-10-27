import React, { useState, useEffect, useMemo } from 'react';
import { Facility } from '../../types';
import { api } from '../../api';
import { StatusBadge } from '../../components/StatusBadge';
import {
  Database,
  Search,
  Filter,
  Download,
  Building2,
  MapPin,
  Zap,
  Accessibility,
  RefreshCw,
  Hash
} from 'lucide-react';

export const AdminRegistryView: React.FC = () => {
  const [registry, setRegistry] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [operatorFilter, setOperatorFilter] = useState('All');
  const [onlyEv, setOnlyEv] = useState(false);

  const fetchRegistry = async () => {
    try {
      setLoading(true);
      const res = await api.getAdminRegistry();
      setRegistry(res.registry);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRegistry();
  }, []);

  const operators = useMemo(() => {
    const set = new Set(registry.map((r) => r.operator));
    return ['All', ...Array.from(set)];
  }, [registry]);

  const filtered = useMemo(() => {
    return registry.filter((r) => {
      const matchesSearch =
        r.name.toLowerCase().includes(search.toLowerCase()) ||
        r.system_code.toLowerCase().includes(search.toLowerCase()) ||
        r.address.toLowerCase().includes(search.toLowerCase());
      const matchesOp = operatorFilter === 'All' || r.operator === operatorFilter;
      const matchesEv = !onlyEv || r.has_ev;
      return matchesSearch && matchesOp && matchesEv;
    });
  }, [registry, search, operatorFilter, onlyEv]);

  const totalCap = registry.reduce((sum, r) => sum + r.capacity, 0);
  const totalSamples = registry.reduce((sum, r) => sum + (r.total_test_samples || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
            <Database className="w-4 h-4" />
            Edge Client Fleet Master Registry
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            30-Facility Decentralized Registry
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Complete topology of autonomous parking IoT clients, capacities, and coordinate metadata.
          </p>
        </div>

        <button
          onClick={fetchRegistry}
          className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors self-start sm:self-auto"
          title="Reload registry"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </div>

      {/* Summary Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Registered Clients</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{registry.length} Nodes</p>
          <span className="text-xs text-emerald-600 font-medium">Clients #0 through #29</span>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Bay Capacity</span>
          <p className="text-2xl font-black text-blue-600 mt-1">{totalCap.toLocaleString()} Bays</p>
          <span className="text-xs text-slate-500">Avg {Math.round(totalCap / (registry.length || 1))} bays/facility</span>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Test Samples Evaluated</span>
          <p className="text-2xl font-black text-indigo-600 mt-1">3,293 Samples</p>
          <span className="text-xs text-slate-500">Strict chronological test partition</span>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Municipal & Private</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{operators.length - 1} Operators</p>
          <span className="text-xs text-slate-500">Birmingham City Council & private</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by client index, facility name, or address..."
              className="w-full pl-10 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-slate-800"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={operatorFilter}
              onChange={(e) => setOperatorFilter(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {operators.map((op) => (
                <option key={op} value={op}>
                  {op === 'All' ? 'All Operators' : op}
                </option>
              ))}
            </select>

            <button
              onClick={() => setOnlyEv(!onlyEv)}
              className={`px-3 py-2 rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 transition-colors ${
                onlyEv
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              EV Chargers Only
            </button>
          </div>
        </div>
      </div>

      {/* Master 30-Facility Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Registered Facility Nodes</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Displaying {filtered.length} of {registry.length} parking client entities.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                <th className="py-2.5 px-3">Node</th>
                <th className="py-2.5 px-3">Facility Name</th>
                <th className="py-2.5 px-3">Operator</th>
                <th className="py-2.5 px-3 text-right">Capacity</th>
                <th className="py-2.5 px-3 text-right">Test Samples</th>
                <th className="py-2.5 px-3">Coordinates</th>
                <th className="py-2.5 px-3 text-right">Tariff</th>
                <th className="py-2.5 px-3 text-center">Amenities</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-mono text-slate-500 font-bold">
                    #{r.client_index}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="font-bold text-slate-900">{r.name}</span>
                    <span className="block text-[10px] text-slate-400 font-mono">{r.system_code}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 font-medium">
                    {r.operator}
                  </td>
                  <td className="py-2.5 px-3 text-right font-extrabold text-slate-900">
                    {r.capacity} bays
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-blue-700 font-bold">
                    {r.total_test_samples || 0}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[10px] text-slate-500">
                    {r.lat.toFixed(4)}, {r.lng.toFixed(4)}
                  </td>
                  <td className="py-2.5 px-3 text-right font-semibold text-slate-700">
                    {r.hourly_rate}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      {r.has_ev ? (
                        <span title="EV Charging" className="p-1 rounded bg-emerald-50 text-emerald-600">
                          <Zap className="w-3 h-3" />
                        </span>
                      ) : (
                        <span className="text-slate-300 text-[10px]">-</span>
                      )}
                      {r.has_disabled && (
                        <span title="Accessible Bays" className="p-1 rounded bg-sky-50 text-sky-600">
                          <Accessibility className="w-3 h-3" />
                        </span>
                      )}
                    </div>
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
