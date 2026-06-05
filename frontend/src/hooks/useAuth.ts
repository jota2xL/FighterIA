import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";
import type { LoginRequest, RegisterRequest } from "@/types/auth.types";
import toast from "react-hot-toast";

export function useAuth() {
  const { setTokens, setUser, logout: storeLogout, user, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      navigate("/dashboard");
      toast.success(`¡Bienvenido, ${data.user.username}!`);
    },
    onError: () => {
      toast.error("Credenciales incorrectas");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      navigate("/dashboard");
      toast.success(`¡Cuenta creada, ${data.user.username}!`);
    },
    onError: () => {
      toast.error("Error al crear la cuenta. Comprueba los datos.");
    },
  });

  const logout = () => {
    storeLogout();
    queryClient.clear();
    navigate("/login");
  };

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: authService.me,
    enabled: isAuthenticated(),
  });

  useEffect(() => {
    if (me) setUser(me);
  }, [me, setUser]);

  return {
    user: me ?? user,
    loginMutation,
    registerMutation,
    logout,
    isAuthenticated: isAuthenticated(),
  };
}
