import React from 'react';
import { UserRole } from '../types';
import {
  Compass,
  MapPin,
  Heart,
  TrendingUp,
  LayoutDashboard,
  Building2,
  LineChart,
  Activity,
  FileText,
  Globe,
  Database,
  Cpu,
  BarChart3,
  ClipboardCheck,
  Download,
  Info
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: any;
  badge?: string;
}

interface SidebarProps {
  currentRole: UserRole;
  currentView: string;
  onSelectView: (viewId: string) => void;
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentRole,
  currentView,
  onSelectView,
  mobileMenuOpen,
  setMobileMenuOpen,
}) => {
  const driverNav: NavItem[] = [
    { id: 'driver_find', label: 'Find Parking', icon: Compass },
    { id: 'driver_facility', label: 'Facility Details', icon: MapPin },
    { id: 'driver_favorites', label: 'Saved Favorites', icon: Heart },
    { id: 'driver_explorer', label: 'Forecast Explorer', icon: TrendingUp, badge: 'AI' }
  ];

  const ownerNav: NavItem[] = [
    { id: 'owner_overview', label: 'Operator Overview', icon: LayoutDashboard },
    { id: 'owner_facilities', label: 'My Facilities', icon: Building2 },
    { id: 'owner_analytics', label: 'Forecast Analytics', icon: LineChart },
    { id: 'owner_health', label: 'Data & Sensors', icon: Activity, badge: 'Live' },
    { id: 'owner_reports', label: 'Operational Reports', icon: FileText }
  ];

  const adminNav: NavItem[] = [
    { id: 'admin_overview', label: 'Global Overview', icon: Globe },
    { id: 'admin_registry', label: 'Facility Registry', icon: Database, badge: '30 Lots' },
    { id: 'admin_federated', label: 'Federated Learning', icon: Cpu, badge: 'Round 8' },
    { id: 'admin_benchmarks', label: 'Benchmark Lab', icon: BarChart3, badge: '6 Models' },
    { id: 'admin_audit', label: 'Data Quality & Audit', icon: ClipboardCheck },
    { id: 'admin_reports', label: 'Master Reports', icon: Download }
  ];

  let items: NavItem[] = [];
  let roleTitle = '';

  if (currentRole === 'customer') {
    items = driverNav;
    roleTitle = 'Driver & Commuter View';
  } else if (currentRole === 'operator') {
    items = ownerNav;
    roleTitle = 'Facility Operator Portal';
  } else {
    items = adminNav;
    roleTitle = 'Administrator Command';
  }

  const content = (
    <div className="flex flex-col h-full bg-white border-r border-slate-200 w-64">
      {/* Section Header */}
      <div className="p-4 border-b border-slate-100">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Role Workspace
        </span>
        <h2 className="text-sm font-bold text-slate-800 tracking-tight mt-0.5">
          {roleTitle}
        </h2>
      </div>

      {/* Nav list */}
      <nav className="p-3 space-y-1 flex-1 overflow-y-auto">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => {
                onSelectView(item.id);
                setMobileMenuOpen(false);
              }}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/25'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info Box */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/70">
        <div className="flex items-start gap-2 text-slate-500 text-[11px]">
          <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-slate-700">Team 4 Project</p>
            <p className="text-slate-500 mt-0.5 leading-snug">
              Federated Multi-Lot Smart Parking Forecasting (Attention-LSTM)
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop fixed sidebar */}
      <aside className="hidden md:block shrink-0 sticky top-16 h-[calc(100vh-4rem)]">
        {content}
      </aside>

      {/* Mobile drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 md:hidden flex">
          <div
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white z-50">
            {content}
          </div>
        </div>
      )}
    </>
  );
};
