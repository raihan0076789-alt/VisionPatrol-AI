import { apiClient } from "./client";
import { AnalyticsSummary } from "../types";

export const analyticsApi = {
  summary: async (): Promise<AnalyticsSummary> => {
    const { data } = await apiClient.get("/analytics/summary");
    return data;
  },
  byType: async (days = 30) => {
    const { data } = await apiClient.get("/analytics/violations-by-type", { params: { days } });
    return data;
  },
  byDay: async (days = 30) => {
    const { data } = await apiClient.get("/analytics/violations-by-day", { params: { days } });
    return data;
  },
  topOffenders: async () => {
    const { data } = await apiClient.get("/analytics/top-offenders");
    return data;
  },
};