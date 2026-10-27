import React, { useState, useEffect } from 'react';
import { UserRole, UserProfile } from './types';
import { api } from './api';
import { DemoBanner } from './components/DemoBanner';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

// Driver Views
import { FindParkingView } from './views/driver/FindParkingView';
import { FacilityDetailsView } from './views/driver/FacilityDetailsView';
import { FavoritesView } from './views/driver/FavoritesView';
import { ForecastExplorerView } from './views/driver/ForecastExplorerView';

// Owner Views
import { OwnerOverviewView } from './views/owner/OwnerOverviewView';
import { OwnerFacilitiesView } from './views/owner/OwnerFacilitiesView';
import { OwnerAnalyticsView } from './views/owner/OwnerAnalyticsView';
import { OwnerHealthView } from './views/owner/OwnerHealthView';
import { OwnerReportsView } from './views/owner/OwnerReportsView';

// Admin Views
import { AdminOverviewView } from './views/admin/AdminOverviewView';
import { AdminRegistryView } from './views/admin/AdminRegistryView';
import { AdminFederatedView } from './views/admin/AdminFederatedView';
import { AdminBenchmarksView } from './views/admin/AdminBenchmarksView';
import { AdminAuditView } from './views/admin/AdminAuditView';
import { AdminReportsView } from './views/admin/AdminReportsView';

import { RefreshCw, ShieldAlert } from 'lucide-react';

export function App() {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [allDemoUsers, setAllDemoUsers] = useState<UserProfile[]>([]);
  const [currentView, setCurrentView] = useState<string>('driver_find');
  const [selectedFacilityId, setSelectedFacilityId] = useState<string>('BHMBCCMKT01');
  const [favorites, setFavorites] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('parksense_favorites');
      return saved ? JSON.parse(saved) : ['BHMBCCMKT01', 'BHMBCCPST01', 'BHMBCCTH01'];
    } catch {
      return ['BHMBCCMKT01', 'BHMBCCPST01'];
    }
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize profile & demo users
  useEffect(() => {
    const init = async () => {
      try {
        setLoading(true);
        const [profile, demoUsers] = await Promise.all([
          api.getProfile(),
          api.listDemoUsers()
        ]);
        setCurrentUser(profile);
        setAllDemoUsers(demoUsers);

        // Set initial view according to role
        if (profile.role === 'customer') {
          setCurrentView('driver_find');
        } else if (profile.role === 'operator') {
          setCurrentView('owner_overview');
        } else {
          setCurrentView('admin_overview');
        }
      } catch (err) {
        console.error('Failed to initialize app', err);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const handleRoleSwitch = async (email: string) => {
    try {
      setLoading(true);
      await api.switchRole(email);
      const updatedProfile = await api.getProfile();
      setCurrentUser(updatedProfile);

      // Auto-navigate to appropriate home view for this role
      if (updatedProfile.role === 'customer') {
        setCurrentView('driver_find');
      } else if (updatedProfile.role === 'operator') {
        setCurrentView('owner_overview');
      } else {
        setCurrentView('admin_overview');
      }
    } catch (err) {
      console.error('Failed to switch role', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = (facilityId: string) => {
    setFavorites((prev) => {
      const next = prev.includes(facilityId)
        ? prev.filter((id) => id !== facilityId)
        : [...prev, facilityId];
      localStorage.setItem('parksense_favorites', JSON.stringify(next));
      return next;
    });
  };

  const handleSelectFacility = (id: string) => {
    setSelectedFacilityId(id);
    setCurrentView('driver_facility');
  };

  if (loading && !currentUser) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-3 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm max-w-sm w-full text-center">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          </div>
          <h2 className="text-base font-bold text-slate-800">Initializing ParkSense AI</h2>
          <p className="text-xs text-slate-500">
            Connecting to FastAPI backend & loading Birmingham IoT stream replay...
          </p>
        </div>
      </div>
    );
  }

  const role = currentUser?.role || 'customer';

  // Render view component based on active currentView
  const renderView = () => {
    // Driver views
    if (currentView === 'driver_find') {
      return (
        <FindParkingView
          onSelectFacility={handleSelectFacility}
          favorites={favorites}
          onToggleFavorite={handleToggleFavorite}
        />
      );
    }
    if (currentView === 'driver_facility') {
      return (
        <FacilityDetailsView
          facilityId={selectedFacilityId}
          onBack={() => setCurrentView('driver_find')}
          favorites={favorites}
          onToggleFavorite={handleToggleFavorite}
          onSelectFacility={setSelectedFacilityId}
        />
      );
    }
    if (currentView === 'driver_favorites') {
      return (
        <FavoritesView
          favorites={favorites}
          onSelectFacility={handleSelectFacility}
          onToggleFavorite={handleToggleFavorite}
          onNavigateToFind={() => setCurrentView('driver_find')}
        />
      );
    }
    if (currentView === 'driver_explorer') {
      return (
        <ForecastExplorerView
          onSelectFacility={handleSelectFacility}
        />
      );
    }

    // Owner views
    if (currentView === 'owner_overview') {
      return (
        <OwnerOverviewView
          onNavigateToFacilities={() => setCurrentView('owner_facilities')}
          onNavigateToAnalytics={() => setCurrentView('owner_analytics')}
          onNavigateToReports={() => setCurrentView('owner_reports')}
        />
      );
    }
    if (currentView === 'owner_facilities') {
      return <OwnerFacilitiesView />;
    }
    if (currentView === 'owner_analytics') {
      return <OwnerAnalyticsView />;
    }
    if (currentView === 'owner_health') {
      return <OwnerHealthView />;
    }
    if (currentView === 'owner_reports') {
      return <OwnerReportsView />;
    }

    // Admin views
    if (currentView === 'admin_overview') {
      return (
        <AdminOverviewView
          onNavigateToFederated={() => setCurrentView('admin_federated')}
          onNavigateToBenchmarks={() => setCurrentView('admin_benchmarks')}
          onNavigateToRegistry={() => setCurrentView('admin_registry')}
          onNavigateToAudit={() => setCurrentView('admin_audit')}
        />
      );
    }
    if (currentView === 'admin_registry') {
      return <AdminRegistryView />;
    }
    if (currentView === 'admin_federated') {
      return <AdminFederatedView />;
    }
    if (currentView === 'admin_benchmarks') {
      return <AdminBenchmarksView />;
    }
    if (currentView === 'admin_audit') {
      return <AdminAuditView />;
    }
    if (currentView === 'admin_reports') {
      return <AdminReportsView />;
    }

    // Default fallback
    return (
      <FindParkingView
        onSelectFacility={handleSelectFacility}
        favorites={favorites}
        onToggleFavorite={handleToggleFavorite}
      />
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-800 font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Academic Disclaimer & Locality Notice */}
      <DemoBanner />

      {/* Global Navbar */}
      <Navbar
        currentUser={currentUser}
        allDemoUsers={allDemoUsers}
        onSwitchRole={handleRoleSwitch}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      {/* Main Layout Container */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        {/* Navigation Sidebar */}
        <Sidebar
          currentRole={role}
          currentView={currentView}
          onSelectView={(v) => setCurrentView(v)}
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
        />

        {/* View Workspace */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0 overflow-y-auto">
          {renderView()}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          <div>
            <p className="font-bold text-slate-700">
              ParkSense AI • Final Year Project Review 2
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Federated Multi-Lot Smart Parking Forecasting Using Attention-Based LSTM on IoT Streams
            </p>
          </div>

          <div className="text-right">
            <p className="font-semibold text-slate-700">Team 4</p>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5">
              Devesh Munagala (23BCT0149) • Abhinav (23BCT0142)
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
