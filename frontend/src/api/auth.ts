import { apiClient } from "./client";
import { AuthTokens, User } from "../types";

export const authApi = {
  login: async (email: string, password: string): Promise<AuthTokens> => {
    const { data } = await apiClient.post("/auth/login", { email, password });
    return data;
  },
  register: async (payload: { full_name: string; email: string; password: string; role: string }): Promise<User> => {
    const { data } = await apiClient.post("/auth/register", payload);
    return data;
  },
  me: async (): Promise<User> => {
    const { data } = await apiClient.get("/auth/me");
    return data;
  },
};