import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { analysisService } from "@/services/analysis.service";
import toast from "react-hot-toast";

export function useCreateAnalysis() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ techniqueId, video }: { techniqueId: number; video: File }) =>
      analysisService.create(techniqueId, video),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["history"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      if (data.xp_awarded > 0) {
        toast.success(`¡+${data.xp_awarded} XP ganados!`);
      }
      navigate(`/analysis/${data.id}`);
    },
    onError: () => {
      toast.error("Error al procesar el vídeo. Inténtalo de nuevo.");
    },
  });
}

export function useAnalysis(id: number) {
  return useQuery({
    queryKey: ["analysis", id],
    queryFn: () => analysisService.getById(id),
    enabled: !!id,
  });
}

export function useAnalysisHistory(page = 1, limit = 20, disciplineId?: number) {
  return useQuery({
    queryKey: ["history", page, limit, disciplineId],
    queryFn: () => analysisService.getMyHistory(page, limit, disciplineId),
  });
}
