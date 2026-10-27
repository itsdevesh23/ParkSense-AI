import React, { useState, useEffect } from 'react';
import { Facility } from '../../types';
import { api } from '../../api';
import { StatusBadge } from '../../components/StatusBadge';
import {
  Building2,
  Edit2,
  Save,
  X,
  Zap,
  Accessibility,
  Clock,
  Search,
  CheckCircle2,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

export const OwnerFacilitiesView: React.FC = () => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editingFacility, setEditingFacility] = useState<Facility | null>(null);
  const [formData, setFormData] = useState({
    hourly_rate: '',
    opening_hours: '',
    has_ev: false,
    has_disabled: false,
  });
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  const loadFacilities = async () => {
    try {
      setLoading(true);
      const res = await api.getOwnerFacilities();
      setFacilities(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFacilities();
  }, []);

  const startEdit = (fac: Facility) => {
    setEditingFacility(fac);
    setFormData({
      hourly_rate: fac.hourly_rate,
      opening_hours: fac.opening_hours,
      has_ev: fac.has_ev,
      has_disabled: fac.has_disabled,
    });
    setSaveStatus(null);
  };

  const cancelEdit = () => {
    setEditingFacility(null);
    setSaveStatus(null);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingFacility) return;

    try {
      setSaveStatus('saving');
      await api.updateFacilityMetadata(editingFacility.id, formData);
      setSaveStatus('success');
      setTimeout(() => {
        setEditingFacility(null);
        setSaveStatus(null);
        loadFacilities();
      }, 900);
    } catch (err) {
      console.error(err);
      setSaveStatus('error');
    }
  };

  const filtered = facilities.filter(
    (f) =>
      f.name.toLowerCase().includes(search.toLowerCase()) ||
      f.system_code.toLowerCase().includes(search.toLowerCase()) ||
      f.address.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 mb-1">
            <Building2 className="w-4 h-4" />
            Asset & Tariff Management
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Manage Assigned Facilities
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure rates, operational hours, EV infrastructure, and accessibility provisions.
          </p>
        </div>

        <button
          onClick={loadFacilities}
          className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors self-start sm:self-auto"
          title="Reload facilities"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-3 shadow-xs max-w-md">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search facility name or code..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-slate-800"
          />
        </div>
      </div>

      {/* Facilities Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((fac) => (
          <div
            key={fac.id}
            className="bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-all p-5 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded uppercase font-mono">
                      {fac.system_code}
                    </span>
                    <StatusBadge status={fac.status} />
                  </div>
                  <h3 className="font-bold text-slate-900 text-sm">{fac.name}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">{fac.address}</p>
                </div>

                <button
                  onClick={() => startEdit(fac)}
                  className="p-2 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors"
                  title="Edit facility parameters"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Specs & Configuration */}
              <div className="mt-4 bg-slate-50 rounded-xl p-3.5 space-y-2 text-xs border border-slate-100">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 font-medium">Capacity</span>
                  <span className="font-bold text-slate-800">{fac.capacity} bays</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 font-medium">Hourly Tariff</span>
                  <span className="font-extrabold text-blue-700">{fac.hourly_rate}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 font-medium">Hours</span>
                  <span className="font-medium text-slate-800 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    {fac.opening_hours}
                  </span>
                </div>
                <div className="flex justify-between items-center pt-1 border-t border-slate-200/60">
                  <span className="text-slate-500 font-medium">EV Charging</span>
                  <span
                    className={`font-semibold inline-flex items-center gap-1 ${
                      fac.has_ev ? 'text-emerald-700' : 'text-slate-400'
                    }`}
                  >
                    <Zap className="w-3 h-3" />
                    {fac.has_ev ? 'Installed' : 'None'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 font-medium">Accessible Bays</span>
                  <span
                    className={`font-semibold inline-flex items-center gap-1 ${
                      fac.has_disabled ? 'text-sky-700' : 'text-slate-400'
                    }`}
                  >
                    <Accessibility className="w-3 h-3" />
                    {fac.has_disabled ? 'Available' : 'None'}
                  </span>
                </div>
              </div>
            </div>

            {/* Telemetry info */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Client #{fac.client_index}</span>
              <span className="text-emerald-600 font-medium">Sensor Online</span>
            </div>
          </div>
        ))}
      </div>

      {/* Edit Modal */}
      {editingFacility && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Edit Facility Parameters</h3>
                <p className="text-xs text-slate-500">{editingFacility.name} ({editingFacility.system_code})</p>
              </div>
              <button
                onClick={cancelEdit}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSave} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Hourly Parking Rate
                </label>
                <input
                  type="text"
                  value={formData.hourly_rate}
                  onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                  placeholder="e.g. £2.50/hr"
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 font-medium focus:ring-2 focus:ring-blue-500 focus:bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Operational Opening Hours
                </label>
                <input
                  type="text"
                  value={formData.opening_hours}
                  onChange={(e) => setFormData({ ...formData, opening_hours: e.target.value })}
                  placeholder="e.g. 24/7 or 06:00 - 23:00"
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-800 font-medium focus:ring-2 focus:ring-blue-500 focus:bg-white"
                  required
                />
              </div>

              <div className="space-y-2 pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.has_ev}
                    onChange={(e) => setFormData({ ...formData, has_ev: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-emerald-600" />
                    EV Rapid Charging Points Available
                  </span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.has_disabled}
                    onChange={(e) => setFormData({ ...formData, has_disabled: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                    <Accessibility className="w-3.5 h-3.5 text-sky-600" />
                    Dedicated Accessible / Blue Badge Bays
                  </span>
                </label>
              </div>

              {saveStatus === 'success' && (
                <div className="p-3 bg-emerald-50 text-emerald-800 rounded-lg text-xs font-semibold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Facility parameters saved successfully!
                </div>
              )}

              {saveStatus === 'error' && (
                <div className="p-3 bg-rose-50 text-rose-800 rounded-lg text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-600" />
                  Failed to update parameters. Please try again.
                </div>
              )}

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={cancelEdit}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saveStatus === 'saving'}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors"
                >
                  <Save className="w-3.5 h-3.5" />
                  {saveStatus === 'saving' ? 'Saving...' : 'Save Parameters'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
