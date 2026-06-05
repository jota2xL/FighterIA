import axios from "axios";
import { useAuthStore } from "@/store/auth.store";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 300000,
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = useAuthStore.getState().refreshToken;
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
            { refresh_token: refresh }
          );
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return apiClient(original);
        } catch {
          useAuthStore.getState().logout();
          window.location.href = "/login";
        }
      } else {
        useAuthStore.getState().logout();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
