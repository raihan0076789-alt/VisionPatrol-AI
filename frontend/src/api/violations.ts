import { apiClient } from "./client";
import { Violation } from "../types";

export const violationsApi = {
  list: async (params?: Record<string, string>): Promise<Violation[]> => {
    const { data } = await apiClient.get("/violations/", { params });
    return data;
  },
  get: async (id: string): Promise<Violation> => {
    const { data } = await apiClient.get(`/violations/${id}`);
    return data;
  },
  update: async (id: string, payload: { status?: string; notes?: string }): Promise<Violation> => {
    const { data } = await apiClient.patch(`/violations/${id}`, payload);
    return data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/violations/${id}`);
  },
};