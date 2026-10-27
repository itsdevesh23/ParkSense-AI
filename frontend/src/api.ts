import { UserProfile, Facility, OccupancyStep, BenchmarkModel, RoundScalingStep, AuditRecord } from './types';

const API_BASE = 'http://localhost:8000/api';

class ApiClient {
  private userEmail: string = localStorage.getItem('parksense_user_email') || 'driver@parksense.ai';

  getUserEmail(): string {
    return this.userEmail;
  }

  setUserEmail(email: string) {
    this.userEmail = email;
    localStorage.setItem('parksense_user_email', email);
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      'Content-Type': 'application/json',
      'X-Demo-User': this.userEmail,
      ...(options.headers || {})
    };

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `HTTP Error ${res.status}`);
      }
      return await res.json();
    } catch (err: any) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  }

  // Auth & Roles
  async getProfile(): Promise<UserProfile> {
    return this.request<UserProfile>('/auth/me');
  }

  async listDemoUsers(): Promise<UserProfile[]> {
    return this.request<UserProfile[]>('/auth/demo-users');
  }

  async switchRole(email: string): Promise<any> {
    this.setUserEmail(email);
    return this.request('/auth/switch-role?email=' + encodeURIComponent(email), { method: 'POST' });
  }

  // Facilities
  async getFacilities(params: {
    search?: string;
    status?: string;
    sort_by?: string;
    min_capacity?: number;
    has_ev?: boolean;
  } = {}): Promise<{ total_count: number; data_notice: string; facilities: Facility[] }> {
    const query = new URLSearchParams();
    if (params.search) query.set('search', params.search);
    if (params.status && params.status !== 'All') query.set('status', params.status);
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.min_capacity) query.set('min_capacity', String(params.min_capacity));
    if (params.has_ev) query.set('has_ev', 'true');

    return this.request(`/facilities?${query.toString()}`);
  }

  async getFacility(id: string): Promise<Facility> {
    return this.request<Facility>(`/facilities/${id}`);
  }

  async getFacilityOccupancy(id: string, limit: number = 24): Promise<{
    facility_id: string;
    facility_name: string;
    capacity: number;
    history_points: number;
    timeline: OccupancyStep[];
  }> {
    return this.request(`/facilities/${id}/occupancy?limit=${limit}`);
  }

  async getFacilityForecast(id: string, horizon: number = 30): Promise<any> {
    return this.request(`/facilities/${id}/forecast?horizon=${horizon}`);
  }

  // Owner
  async getOwnerOverview(): Promise<any> {
    return this.request('/owner/overview');
  }

  async getOwnerFacilities(): Promise<Facility[]> {
    return this.request<Facility[]>('/owner/facilities');
  }

  async updateFacilityMetadata(id: string, payload: any): Promise<any> {
    return this.request(`/owner/facilities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  }

  async getOwnerAnalytics(): Promise<any> {
    return this.request('/owner/analytics');
  }

  async getOwnerHealth(): Promise<any> {
    return this.request('/owner/health');
  }

  // Admin
  async getAdminOverview(): Promise<any> {
    return this.request('/admin/overview');
  }

  async getAdminRegistry(): Promise<{ count: number; registry: Facility[] }> {
    return this.request('/admin/registry');
  }

  async getAdminFederated(): Promise<any> {
    return this.request('/admin/federated');
  }

  async getAdminBenchmarks(horizon: string = 'both'): Promise<any> {
    return this.request(`/admin/benchmarks?horizon=${horizon}`);
  }

  async getAdminAudit(): Promise<any> {
    return this.request('/admin/audit');
  }

  // Reports
  getReportDownloadUrl(reportType: 'occupancy' | 'benchmarks' | 'audit', horizon?: string): string {
    const hParam = horizon ? `?horizon=${horizon}` : '';
    return `${API_BASE}/reports/${reportType}.csv${hParam}`;
  }
}

export const api = new ApiClient();
