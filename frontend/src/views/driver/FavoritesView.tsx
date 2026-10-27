import React, { useState, useEffect, useMemo } from 'react';
import { Facility } from '../../types';
import { api } from '../../api';
import { StatusBadge } from '../../components/StatusBadge';
import {
  Heart,
  Car,
  MapPin,
  Clock,
  ArrowRight,
  Trash2,
  Sparkles,
  TrendingUp,
  TrendingDown,
  Compass
} from 'lucide-react';

interface FavoritesViewProps {
  favorites: string[];
  onSelectFacility: (facilityId: string) => void;
  onToggleFavorite: (facilityId: string) => void;
  onNavigateToFind: () => void;
}

export const FavoritesView: React.FC<FavoritesViewProps> = ({
  favorites,
  onSelectFacility,
  onToggleFavorite,
  onNavigateToFind,
}) => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const res = await api.getFacilities();
        setFacilities(res.facilities);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const favoriteFacilities = useMemo(() => {
    return facilities.filter((f) => favorites.includes(f.id));
  }, [facilities, favorites]);

  const stats = useMemo(() => {
    if (favoriteFacilities.length === 0) return { totalVacant: 0, avgOccupancy: 0, totalCapacity: 0 };
    const totalVacant = favoriteFacilities.reduce((sum, f) => sum + f.vacant_bays, 0);
    const totalCapacity = favoriteFacilities.reduce((sum, f) => sum + f.capacity, 0);
    const avgOccupancy = Math.round(
      favoriteFacilities.reduce((sum, f) => sum + f.occupancy_pct, 0) / favoriteFacilities.length
    );
    return { totalVacant, avgOccupancy, totalCapacity };
  }, [favoriteFacilities]);

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-500 text-sm">
        Loading saved facilities...
      </div>
    );
  }

  if (favoriteFacilities.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-xl mx-auto my-8 shadow-xs">
        <div className="w-16 h-16 rounded-2xl bg-rose-50 text-rose-500 flex items-center justify-center mx-auto mb-4 border border-rose-100">
          <Heart className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">No Saved Parking Lots Yet</h2>
        <p className="text-xs text-slate-500 mt-2 max-w-md mx-auto leading-relaxed">
          Bookmark your regular parking spots, work decks, or shopping garages to get immediate access to live occupancy and AI turnover forecasts.
        </p>
        <button
          onClick={onNavigateToFind}
          className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-md shadow-blue-500/20 transition-all"
        >
          <Compass className="w-4 h-4" />
          Browse Birmingham Parking Map
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-600 mb-1">
            <Heart className="w-4 h-4 fill-current" />
            Personal Bookmarks
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Saved Parking Facilities</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Quick-access dashboard for your monitored destinations and commuter hubs.
          </p>
        </div>

        <button
          onClick={onNavigateToFind}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors self-start md:self-auto"
        >
          <Compass className="w-3.5 h-3.5" />
          Add More Facilities
        </button>
      </div>

      {/* Quick Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Bookmarked Lots</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{favoriteFacilities.length} Facilities</p>
          <span className="text-xs text-slate-500 mt-1 block">Total capacity: {stats.totalCapacity.toLocaleString()} bays</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Currently Available</span>
          <p className="text-2xl font-black text-emerald-600 mt-1">{stats.totalVacant.toLocaleString()} Bays</p>
          <span className="text-xs text-slate-500 mt-1 block">Across all your saved locations</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Average Occupancy</span>
          <p className="text-2xl font-black text-blue-600 mt-1">{stats.avgOccupancy}%</p>
          <span className="text-xs text-slate-500 mt-1 block">Live aggregated load</span>
        </div>
      </div>

      {/* Grid of Saved Lots */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {favoriteFacilities.map((fac) => (
          <div
            key={fac.id}
            className="bg-white rounded-xl border border-slate-200 hover:shadow-md transition-all p-5 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded uppercase">
                      {fac.system_code}
                    </span>
                    <StatusBadge status={fac.status} />
                  </div>
                  <h3 className="font-bold text-slate-900 text-sm">{fac.name}</h3>
                  <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    {fac.address}
                  </p>
                </div>

                <button
                  onClick={() => onToggleFavorite(fac.id)}
                  title="Remove from saved"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Occupancy bar */}
              <div className="my-3 bg-slate-50 rounded-lg p-2.5 border border-slate-100">
                <div className="flex justify-between items-center text-xs mb-1">
                  <span className="text-slate-600 font-medium">Free Spaces:</span>
                  <span className="font-extrabold text-emerald-600 text-sm">
                    {fac.vacant_bays} <span className="text-slate-400 font-normal text-xs">/ {fac.capacity}</span>
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      fac.occupancy_pct >= 90
                        ? 'bg-rose-500'
                        : fac.occupancy_pct >= 70
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${fac.occupancy_pct}%` }}
                  />
                </div>
              </div>

              {/* Forecast preview */}
              <div className="grid grid-cols-2 gap-2 text-center text-xs">
                <div className="bg-blue-50/70 rounded-lg p-2 border border-blue-100">
                  <span className="text-[10px] font-bold text-blue-600 uppercase block">+30m Forecast</span>
                  <span className="font-bold text-blue-900 text-xs mt-0.5 inline-flex items-center gap-1">
                    {fac.forecast_30m_bays} bays
                    {fac.trend_30m === 'increasing' ? (
                      <TrendingUp className="w-3 h-3 text-emerald-600" />
                    ) : (
                      <TrendingDown className="w-3 h-3 text-rose-500" />
                    )}
                  </span>
                </div>
                <div className="bg-indigo-50/70 rounded-lg p-2 border border-indigo-100">
                  <span className="text-[10px] font-bold text-indigo-600 uppercase block">+60m Forecast</span>
                  <span className="font-bold text-indigo-900 text-xs mt-0.5 block">
                    {fac.forecast_60m_bays} bays
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700">{fac.hourly_rate}</span>
              <button
                onClick={() => onSelectFacility(fac.id)}
                className="inline-flex items-center gap-1 text-xs font-bold text-blue-600 hover:text-blue-700"
              >
                Inspect Telemetry
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
