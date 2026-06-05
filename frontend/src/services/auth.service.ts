import apiClient from "./api.client";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types/auth.types";

export const authService = {
  register: (data: RegisterRequest) =>
    apiClient.post<TokenResponse>("/auth/register", data).then((r) => r.data),

  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>("/auth/login", data).then((r) => r.data),

  refresh: (refreshToken: string) =>
    apiClient
      .post<TokenResponse>("/auth/refresh", { refresh_token: refreshToken })
      .then((r) => r.data),

  forgotPassword: (email: string) =>
    apiClient.post("/auth/forgot-password", { email }).then((r) => r.data),

  me: () => apiClient.get<User>("/auth/me").then((r) => r.data),

  updateProfile: (data: FormData) =>
    apiClient
      .put<User>("/users/me", data, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data),
};
