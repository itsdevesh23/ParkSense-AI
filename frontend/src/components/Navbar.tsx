import React, { useState } from 'react';
import { UserProfile, UserRole } from '../types';
import {
  Car,
  Building2,
  Shield,
  UserCheck,
  ChevronDown,
  Layers,
  Radio,
  Menu,
  X
} from 'lucide-react';

interface NavbarProps {
  currentUser: UserProfile | null;
  allDemoUsers?: UserProfile[];
  demoUsers?: UserProfile[];
  onSwitchUser?: (email: string) => void;
  onSwitchRole?: (email: string) => void;
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentUser,
  allDemoUsers,
  demoUsers,
  onSwitchUser,
  onSwitchRole,
  mobileMenuOpen,
  setMobileMenuOpen,
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const effectiveUsers = allDemoUsers || demoUsers || [];
  const handleSwitch = onSwitchRole || onSwitchUser || (() => {});

  const roleMeta: Record<UserRole, { label: string; icon: any; color: string }> = {
    customer: { label: 'Driver / Customer', icon: Car, color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    operator: { label: 'Parking Operator', icon: Building2, color: 'bg-blue-50 text-blue-700 border-blue-200' },
    admin: { label: 'System Admin', icon: Shield, color: 'bg-indigo-50 text-indigo-700 border-indigo-200' }
  };

  const userRole = currentUser?.role || 'customer';
  const currentRoleMeta = roleMeta[userRole] || roleMeta.customer;
  const RoleIcon = currentRoleMeta.icon;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-700 to-indigo-900 flex items-center justify-center text-white shadow-sm shadow-blue-500/20 font-bold text-lg tracking-wider">
              P
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg tracking-tight text-slate-900">
                  ParkSense<span className="text-blue-600">.AI</span>
                </span>
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              </div>
              <p className="text-[10px] text-slate-400 -mt-1 font-medium hidden sm:block">
                Federated Smart Parking Platform
              </p>
            </div>
          </div>
        </div>

        {/* Center: System Status Pill (Desktop) */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-slate-50 border border-slate-200 rounded-full text-xs text-slate-600">
          <Radio className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
          <span className="font-medium text-slate-700">Birmingham Testbed:</span>
          <span>30 Active Nodes (FedAvg Round 8)</span>
        </div>

        {/* Right: Demo Role Switcher & Profile */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 transition-all text-xs text-slate-700 font-medium shadow-xs"
            >
              <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md border text-[11px] font-semibold ${currentRoleMeta.color}`}>
                <RoleIcon className="w-3.5 h-3.5" />
                {currentRoleMeta.label}
              </span>
              <span className="hidden sm:inline font-semibold text-slate-800">{currentUser?.name || 'Demo User'}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-2">
                <div className="px-3 py-2 border-b border-slate-100">
                  <p className="text-xs font-bold text-slate-900">Switch Demo Role & Perspective</p>
                  <p className="text-[11px] text-slate-500">
                    Instant role authorization without credentials:
                  </p>
                </div>

                <div className="p-1 space-y-1">
                  {effectiveUsers.map((u) => {
                    const meta = roleMeta[u.role] || roleMeta.customer;
                    const Icon = meta.icon;
                    const isActive = u.email === currentUser?.email;

                    return (
                      <button
                        key={u.email}
                        onClick={() => {
                          handleSwitch(u.email);
                          setDropdownOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-lg flex items-start gap-3 transition-colors ${
                          isActive
                            ? 'bg-blue-50/70 border border-blue-200 text-blue-950'
                            : 'hover:bg-slate-50 text-slate-700'
                        }`}
                      >
                        <div className={`p-1.5 rounded-md border ${meta.color} mt-0.5`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-xs text-slate-900 truncate">
                              {u.name}
                            </span>
                            {isActive && (
                              <span className="text-[10px] font-bold text-blue-600 bg-blue-100/70 px-1.5 py-0.2 rounded">
                                Active
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-500 font-medium truncate">{u.title}</p>
                          <p className="text-[10px] text-slate-400 truncate">{u.email}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
