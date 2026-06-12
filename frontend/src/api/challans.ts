import { apiClient } from "./client";
import { Challan } from "../types";

export const challansApi = {
  generate: async (violationId: string): Promise<Challan> => {
    const { data } = await apiClient.post(`/challans/generate/${violationId}`);
    return data;
  },
  list: async (): Promise<Challan[]> => {
    const { data } = await apiClient.get("/challans/");
    return data;
  },
  get: async (id: string): Promise<Challan> => {
    const { data } = await apiClient.get(`/challans/${id}`);
    return data;
  },
  update: async (id: string, status: string): Promise<Challan> => {
    const { data } = await apiClient.patch(`/challans/${id}`, { status });
    return data;
  },
  downloadUrl: (id: string): string =>
    `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/v1/challans/${id}/download`,
};

