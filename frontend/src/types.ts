export type UserRole = 'customer' | 'operator' | 'admin';

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  title: string;
  assigned_facilities: string[];
  avatar: string;
}

export interface Facility {
  id: string;
  client_index: number;
  name: string;
  system_code: string;
  operator: string;
  owner_group: string;
  capacity: number;
  occupied_bays: number;
  vacant_bays: number;
  occupancy_pct: number;
  status: 'Available' | 'Busy' | 'Nearly Full' | string;
  status_color: 'green' | 'amber' | 'red' | string;
  forecast_30m_bays: number;
  forecast_30m_ratio: number;
  forecast_60m_bays: number;
  forecast_60m_ratio: number;
  trend_30m: 'increasing' | 'decreasing';
  trend_delta: number;
  model_mae_ratio: number;
  model_mae_spaces: number;
  global_fedavg_mae: number;
  personalization_gain_pct: number;
  lat: number;
  lng: number;
  address: string;
  hourly_rate: string;
  has_ev: boolean;
  has_disabled: boolean;
  opening_hours: string;
  data_freshness: string;
  data_status: string;
  total_test_samples: number;
}

export interface OccupancyStep {
  step_index: number;
  time_label: string;
  capacity: number;
  actual_avail_ratio: number;
  actual_occupied_bays: number;
  actual_vacant_bays: number;
  actual_occupancy_pct: number;
  target_30m_actual_bays: number;
  pred_30m_bays: number;
  pred_30m_ratio: number;
  target_60m_actual_bays: number;
  pred_60m_bays: number;
  pred_60m_ratio: number;
  error_30m_bays: number;
  error_60m_bays: number;
}

export interface BenchmarkModel {
  Model: string;
  'Pooled MAE (Micro, Ratio)': number;
  'Pooled RMSE (Ratio)': number;
  'Macro Mean MAE (Ratio)': number;
  'Between-Lot Std (sigma)': number;
  'Mean Space Error (bays)': number;
}

export interface RoundScalingStep {
  Rounds: number;
  'Mean Train MSE': number;
  'Pooled Test MAE': number;
  'Macro Mean MAE': number;
  'Between-Lot Std': number;
}

export interface AuditRecord {
  'Client ID': string;
  'Parking Name': string;
  Capacity: number;
  'Test Samples': number;
  'Cent Attention MAE': number;
  'Cent Attention Spaces': number;
  'FedAvg MAE': number;
  'FedAvg Spaces': number;
  'Personalized MAE': number;
  'Personalized Spaces': number;
  'Personalization Gain (%)': number;
}
