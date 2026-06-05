export interface Gym {
  id: number;
  name: string;
  city: string;
  country: string;
  plan: string;
  created_at: string;
}

export interface GymCreate {
  name: string;
  city: string;
  country?: string;
  plan?: string;
}

export interface Trainer {
  id: number;
  gym_id: number;
  user_id?: number;
  role: string;
  status: string;
}

export interface Lead {
  id: number;
  gym_id: number;
  name: string;
  email: string;
  phone?: string;
  status: string;
  source: string;
  notes: string;
  created_at: string;
}

export interface LeadCreate {
  name: string;
  email: string;
  phone?: string;
  status?: string;
  source?: string;
  notes?: string;
}

export interface GymMetrics {
  gym_id: number;
  gym_name: string;
  total_trainers: number;
  total_leads: number;
  conversion_rate: number;
  plan: string;
}
