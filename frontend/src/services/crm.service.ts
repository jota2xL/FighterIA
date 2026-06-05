import apiClient from "./api.client";
import type { Gym, GymCreate, GymMetrics, Lead, LeadCreate } from "@/types/crm.types";

export const crmService = {
  getGyms: () =>
    apiClient.get<Gym[]>("/crm/gyms").then((r) => r.data),

  createGym: (data: GymCreate) =>
    apiClient.post<Gym>("/crm/gyms", data).then((r) => r.data),

  getGymMetrics: (gymId: number) =>
    apiClient.get<GymMetrics>(`/crm/gyms/${gymId}/metrics`).then((r) => r.data),

  getLeads: (gymId: number) =>
    apiClient.get<Lead[]>(`/crm/gyms/${gymId}/leads`).then((r) => r.data),

  createLead: (gymId: number, data: LeadCreate) =>
    apiClient.post<Lead>(`/crm/gyms/${gymId}/leads`, data).then((r) => r.data),

  updateLead: (gymId: number, leadId: number, data: Partial<LeadCreate>) =>
    apiClient
      .put<Lead>(`/crm/gyms/${gymId}/leads/${leadId}`, data)
      .then((r) => r.data),
};
