import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Facility } from '../types';
import { ArrowUpRight, Clock, Navigation } from 'lucide-react';

// Custom colored SVG pin markers for Leaflet
const createPinIcon = (colorHex: string, label: string) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="32" height="42">
      <defs>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/>
        </filter>
      </defs>
      <path d="M16 0C7.16 0 0 7.16 0 16c0 10.5 14.5 24.5 15.2 25.2.4.4 1.2.4 1.6 0C17.5 40.5 32 26.5 32 16 32 7.16 24.84 0 16 0z" fill="${colorHex}" filter="url(#shadow)"/>
      <circle cx="16" cy="15" r="8" fill="#ffffff"/>
      <text x="16" y="19" font-size="10" font-weight="bold" fill="${colorHex}" text-anchor="middle" font-family="sans-serif">P</text>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'custom-leaflet-marker',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -38]
  });
};

const greenIcon = createPinIcon('#10b981', 'P');
const amberIcon = createPinIcon('#f59e0b', 'P');
const redIcon = createPinIcon('#ef4444', 'P');

interface MapViewProps {
  facilities: Facility[];
  selectedFacility: Facility | null;
  onSelectFacility: (facility: Facility) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  facilities,
  selectedFacility,
  onSelectFacility,
}) => {
  // Center of Birmingham City Centre
  const birminghamCenter: [number, number] = [52.4800, -1.9000];

  return (
    <div className="w-full h-full min-h-[380px] rounded-xl overflow-hidden border border-slate-200 relative shadow-sm">
      <MapContainer
        center={birminghamCenter}
        zoom={14}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {facilities.map((fac) => {
          let markerIcon = greenIcon;
          if (fac.occupancy_pct >= 90) markerIcon = redIcon;
          else if (fac.occupancy_pct >= 70) markerIcon = amberIcon;

          return (
            <Marker
              key={fac.id}
              position={[fac.lat, fac.lng]}
              icon={markerIcon}
              eventHandlers={{
                click: () => onSelectFacility(fac),
              }}
            >
              <Popup>
                <div className="p-1 min-w-[200px]">
                  <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-1.5 mb-2">
                    <span className="font-bold text-xs text-slate-900 truncate">
                      {fac.name}
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-500 mb-2 truncate">
                    {fac.address}
                  </p>

                  <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2 rounded-lg mb-2.5 text-center">
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold uppercase">Current Free</p>
                      <p className="text-sm font-extrabold text-emerald-600">
                        {fac.vacant_bays} <span className="text-[10px] text-slate-400 font-normal">/ {fac.capacity}</span>
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 font-semibold uppercase">In 30m</p>
                      <p className="text-sm font-extrabold text-blue-600">
                        {fac.forecast_30m_bays} <span className="text-[10px] text-slate-400 font-normal">bays</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-600 mb-2">
                    <span>Rate: <strong className="text-slate-800">{fac.hourly_rate}</strong></span>
                    <span>In 60m: <strong className="text-indigo-600">{fac.forecast_60m_bays} bays</strong></span>
                  </div>

                  <button
                    onClick={() => onSelectFacility(fac)}
                    className="w-full flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-1.5 px-3 rounded-lg transition-colors shadow-xs"
                  >
                    View Predictions & Analytics
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-white/95 backdrop-blur-xs px-3 py-2 rounded-lg border border-slate-200 shadow-md text-xs">
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Live Vacancy Status</p>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1 text-slate-700 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> &gt; 30% Free
          </span>
          <span className="flex items-center gap-1 text-slate-700 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> 10–30% Free
          </span>
          <span className="flex items-center gap-1 text-slate-700 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> &lt; 10% Free
          </span>
        </div>
      </div>
    </div>
  );
};
