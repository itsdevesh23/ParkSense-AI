import React, { useState, useEffect, useMemo } from 'react';
import { Facility } from '../../types';
import { api } from '../../api';
import { StatusBadge } from '../../components/StatusBadge';
import { MapView } from '../../components/MapView';
import {
  Search,
  SlidersHorizontal,
  Zap,
  TrendingDown,
  TrendingUp,
  Heart,
  ArrowRight,
  MapPin,
  Car,
  Clock,
  Sparkles,
  RefreshCw,
  LayoutGrid,
  Map as MapIcon
} from 'lucide-react';

interface FindParkingViewProps {
  onSelectFacility: (facilityId: string) => void;
  favorites: string[];
  onToggleFavorite: (facilityId: string) => void;
}

export const FindParkingView: React.FC<FindParkingViewProps> = ({
  onSelectFacility,
  favorites,
  onToggleFavorite,
}) => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [onlyEv, setOnlyEv] = useState(false);
  const [sortBy, setSortBy] = useState<string>('vacant_desc');
  const [activeTab, setActiveTab] = useState<'split' | 'map' | 'list'>('split');
  const [selectedMapFacility, setSelectedMapFacility] = useState<Facility | null>(null);

  const fetchFacilities = async () => {
    try {
      setLoading(true);
      const res = await api.getFacilities();
      setFacilities(res.facilities);
    } catch (err) {
      console.error('Failed to load facilities', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFacilities();
  }, []);

  const filteredFacilities = useMemo(() => {
    return facilities
      .filter((f) => {
        const matchesSearch =
          f.name.toLowerCase().includes(search.toLowerCase()) ||
          f.address.toLowerCase().includes(search.toLowerCase());
        const matchesStatus =
          selectedStatus === 'All' || f.status === selectedStatus;
        const matchesEv = !onlyEv || f.has_ev;
        return matchesSearch && matchesStatus && matchesEv;
      })
      .sort((a, b) => {
        if (sortBy === 'vacant_desc') return b.vacant_bays - a.vacant_bays;
        if (sortBy === 'occupancy_asc') return a.occupancy_pct - b.occupancy_pct;
        if (sortBy === 'capacity_desc') return b.capacity - a.capacity;
        if (sortBy === 'rate_asc') {
          const rateA = parseFloat(a.hourly_rate.replace(/[^0-9.]/g, '')) || 0;
          const rateB = parseFloat(b.hourly_rate.replace(/[^0-9.]/g, '')) || 0;
          return rateA - rateB;
        }
        return 0;
      });
  }, [facilities, search, selectedStatus, onlyEv, sortBy]);

  const totalVacantSum = useMemo(() => {
    return facilities.reduce((acc, f) => acc + f.vacant_bays, 0);
  }, [facilities]);

  return (
    <div className="space-y-6">
      {/* Page Title & Stats Banner */}
      <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-sky-700 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-white/5 transform skew-x-12 pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 text-blue-100 text-xs font-semibold backdrop-blur-xs mb-3">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            IoT Stream Live Replay • Attention-LSTM + FedAvg
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Find & Reserve Smart Parking in Birmingham
          </h1>
          <p className="mt-2 text-blue-100 text-sm leading-relaxed">
            Real-time occupancy monitoring with predictive 30-min and 60-min forecasts powered by personalized federated edge models.
          </p>

          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 text-white">
            <div className="bg-white/10 rounded-xl p-3 backdrop-blur-xs">
              <span className="text-[11px] font-medium text-blue-200">Active Facilities</span>
              <p className="text-xl font-bold mt-0.5">{facilities.length} Lots</p>
            </div>
            <div className="bg-white/10 rounded-xl p-3 backdrop-blur-xs">
              <span className="text-[11px] font-medium text-blue-200">Currently Vacant</span>
              <p className="text-xl font-bold mt-0.5 text-emerald-300">{totalVacantSum.toLocaleString()} Bays</p>
            </div>
            <div className="bg-white/10 rounded-xl p-3 backdrop-blur-xs">
              <span className="text-[11px] font-medium text-blue-200">30-min Model Error</span>
              <p className="text-xl font-bold mt-0.5 text-amber-300">±1.45% MAE</p>
            </div>
            <div className="bg-white/10 rounded-xl p-3 backdrop-blur-xs">
              <span className="text-[11px] font-medium text-blue-200">Personalization Gain</span>
              <p className="text-xl font-bold mt-0.5 text-sky-300">+39.7%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Control Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Search bar */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by facility name, landmark or street address..."
              className="w-full pl-10 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-slate-800 placeholder-slate-400"
            />
          </div>

          {/* Quick controls */}
          <div className="flex flex-wrap items-center gap-2">
            {/* View Mode Toggle */}
            <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
              <button
                onClick={() => setActiveTab('split')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  activeTab === 'split' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <SlidersHorizontal className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Split View</span>
              </button>
              <button
                onClick={() => setActiveTab('map')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  activeTab === 'map' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <MapIcon className="w-3.5 h-3.5" />
                <span>Map</span>
              </button>
              <button
                onClick={() => setActiveTab('list')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  activeTab === 'list' ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span>List</span>
              </button>
            </div>

            {/* Sort selector */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="vacant_desc">Most Vacant Bays</option>
              <option value="occupancy_asc">Lowest Occupancy %</option>
              <option value="rate_asc">Lowest Hourly Rate</option>
              <option value="capacity_desc">Largest Capacity</option>
            </select>

            {/* Refresh */}
            <button
              onClick={fetchFacilities}
              title="Refresh live occupancy"
              className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-100">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">Status:</span>
          {['All', 'Available', 'Busy', 'Nearly Full'].map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                selectedStatus === st
                  ? 'bg-blue-600 text-white font-semibold shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st}
            </button>
          ))}

          <div className="h-4 w-px bg-slate-200 mx-1" />

          {/* EV Toggle */}
          <button
            onClick={() => setOnlyEv(!onlyEv)}
            className={`px-2.5 py-1 rounded-full text-xs font-medium inline-flex items-center gap-1.5 transition-colors ${
              onlyEv
                ? 'bg-emerald-600 text-white font-semibold shadow-xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Zap className="w-3 h-3 text-emerald-400" />
            EV Charging Only
          </button>

          <span className="text-xs text-slate-400 ml-auto font-medium">
            Showing <strong className="text-slate-700">{filteredFacilities.length}</strong> of {facilities.length} parking facilities
          </span>
        </div>
      </div>

      {/* Main Content Layout */}
      {activeTab === 'split' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Map on Left (7 cols) */}
          <div className="lg:col-span-7 h-[680px] sticky top-20 rounded-2xl overflow-hidden shadow-sm">
            <MapView
              facilities={filteredFacilities}
              selectedFacility={selectedMapFacility}
              onSelectFacility={(fac) => {
                setSelectedMapFacility(fac);
                onSelectFacility(fac.id);
              }}
            />
          </div>

          {/* Cards on Right (5 cols) */}
          <div className="lg:col-span-5 space-y-4 max-h-[680px] overflow-y-auto pr-1">
            {filteredFacilities.map((fac) => (
              <FacilityCard
                key={fac.id}
                facility={fac}
                isFavorite={favorites.includes(fac.id)}
                onToggleFavorite={() => onToggleFavorite(fac.id)}
                onViewDetails={() => onSelectFacility(fac.id)}
              />
            ))}
            {filteredFacilities.length === 0 && (
              <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500">
                <Car className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="font-semibold text-sm text-slate-700">No parking lots matched your filters</p>
                <p className="text-xs mt-1">Try resetting the status filter or clearing search keywords.</p>
              </div>
            )}
          </div>
        </div>
      ) : activeTab === 'map' ? (
        <div className="h-[750px] rounded-2xl overflow-hidden shadow-sm">
          <MapView
            facilities={filteredFacilities}
            selectedFacility={selectedMapFacility}
            onSelectFacility={(fac) => {
              setSelectedMapFacility(fac);
              onSelectFacility(fac.id);
            }}
          />
        </div>
      ) : (
        /* Full List Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredFacilities.map((fac) => (
            <FacilityCard
              key={fac.id}
              facility={fac}
              isFavorite={favorites.includes(fac.id)}
              onToggleFavorite={() => onToggleFavorite(fac.id)}
              onViewDetails={() => onSelectFacility(fac.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface FacilityCardProps {
  facility: Facility;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  onViewDetails: () => void;
}

const FacilityCard: React.FC<FacilityCardProps> = ({
  facility,
  isFavorite,
  onToggleFavorite,
  onViewDetails,
}) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all p-4.5 flex flex-col justify-between">
      <div>
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded uppercase tracking-wider">
                {facility.system_code}
              </span>
              <StatusBadge status={facility.status} />
              {facility.has_ev && (
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
                  <Zap className="w-3 h-3 text-emerald-600" /> EV
                </span>
              )}
            </div>
            <h3 className="font-bold text-slate-900 text-sm truncate">{facility.name}</h3>
            <p className="text-slate-500 text-xs flex items-center gap-1 mt-0.5 truncate">
              <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
              {facility.address}
            </p>
          </div>

          <button
            onClick={onToggleFavorite}
            aria-label="Toggle favorite"
            className={`p-1.5 rounded-lg border transition-colors ${
              isFavorite
                ? 'bg-rose-50 border-rose-200 text-rose-600'
                : 'border-slate-200 text-slate-400 hover:text-rose-500 hover:bg-slate-50'
            }`}
          >
            <Heart className={`w-4 h-4 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
        </div>

        {/* Live Occupancy Gauge & Counts */}
        <div className="mt-3.5 bg-slate-50 rounded-xl p-3 border border-slate-100">
          <div className="flex justify-between items-baseline mb-1 text-xs">
            <span className="text-slate-600 font-medium">Occupancy</span>
            <span className="font-bold text-slate-900">
              {facility.occupied_bays} <span className="text-slate-400 font-normal">/ {facility.capacity} bays</span>
              <span className="ml-1.5 text-slate-500">({facility.occupancy_pct}%)</span>
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                facility.occupancy_pct >= 90
                  ? 'bg-rose-500'
                  : facility.occupancy_pct >= 70
                  ? 'bg-amber-500'
                  : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, facility.occupancy_pct)} projection` as any || `${facility.occupancy_pct}%` }}
            />
          </div>

          {/* Vacant Highlight */}
          <div className="mt-2.5 flex items-center justify-between text-xs">
            <span className="text-slate-500 font-medium">Available Now:</span>
            <span className="text-sm font-extrabold text-emerald-600">
              {facility.vacant_bays} open bays
            </span>
          </div>
        </div>

        {/* Forecast Strip (30m and 60m) */}
        <div className="mt-3 grid grid-cols-2 gap-2">
          {/* 30m forecast */}
          <div className="bg-blue-50/70 border border-blue-100 rounded-lg p-2 text-center">
            <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wide flex items-center justify-center gap-1">
              <Clock className="w-3 h-3" /> +30 min Forecast
            </span>
            <div className="flex items-center justify-center gap-1 mt-0.5">
              <span className="text-sm font-bold text-blue-900">
                {facility.forecast_30m_bays} bays
              </span>
              {facility.trend_30m === 'increasing' ? (
                <TrendingUp className="w-3.5 h-3.5 text-emerald-600" title="Vacancies expected to rise" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-rose-500" title="Vacancies expected to decrease" />
              )}
            </div>
            <span className="text-[10px] text-blue-500 font-medium">
              Ratio: {(facility.forecast_30m_ratio * 100).toFixed(1)}% free
            </span>
          </div>

          {/* 60m forecast */}
          <div className="bg-indigo-50/70 border border-indigo-100 rounded-lg p-2 text-center">
            <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-wide flex items-center justify-center gap-1">
              <Clock className="w-3 h-3" /> +60 min Forecast
            </span>
            <div className="flex items-center justify-center gap-1 mt-0.5">
              <span className="text-sm font-bold text-indigo-900">
                {facility.forecast_60m_bays} bays
              </span>
            </div>
            <span className="text-[10px] text-indigo-500 font-medium">
              Ratio: {(facility.forecast_60m_ratio * 100).toFixed(1)}% free
            </span>
          </div>
        </div>
      </div>

      {/* Card Footer */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 block font-medium">Tariff Rate</span>
          <span className="text-xs font-bold text-slate-800">{facility.hourly_rate}</span>
        </div>

        <button
          onClick={onViewDetails}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-colors"
        >
          Predictions
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
