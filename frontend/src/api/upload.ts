import { apiClient } from "./client";

export const uploadApi = {
  uploadVideo: async (
    file: File,
    onProgress?: (pct: number) => void
  ): Promise<{ session_id: string; status: string; message: string }> => {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await apiClient.post("/upload/video", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      },
    });
    return data;
  },

  getSessions: async () => {
    const { data } = await apiClient.get("/upload/sessions");
    return data;
  },

  getSessionStatus: async (sessionId: string) => {
    const { data } = await apiClient.get(`/upload/sessions/${sessionId}/status`);
    return data;
  },
};