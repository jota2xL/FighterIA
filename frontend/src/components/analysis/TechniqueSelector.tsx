/**
 * TechniqueSelector
 * Cascading discipline → technique selectors for the analysis form.
 */
import { useQuery } from "@tanstack/react-query";
import { disciplineService } from "@/services/analysis.service";
import type { Discipline, Technique } from "@/types/analysis.types";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";

interface TechniqueSelectorProps {
  selectedDisciplineId: number | null;
  selectedTechniqueId: number | null;
  onDisciplineChange: (id: number | null) => void;
  onTechniqueChange: (id: number | null) => void;
}

const TechniqueSelector = ({
  selectedDisciplineId,
  selectedTechniqueId,
  onDisciplineChange,
  onTechniqueChange,
}: TechniqueSelectorProps) => {
  const {
    data: disciplines,
    isLoading: loadingDisciplines,
    isError: errorDisciplines,
    refetch: refetchDisciplines,
  } = useQuery<Discipline[]>({
    queryKey: ["disciplines"],
    queryFn: disciplineService.getAll,
  });

  const {
    data: techniques,
    isLoading: loadingTechniques,
    isError: errorTechniques,
    refetch: refetchTechniques,
  } = useQuery<Technique[]>({
    queryKey: ["techniques", selectedDisciplineId],
    queryFn: () => disciplineService.getTechniques(selectedDisciplineId!),
    enabled: !!selectedDisciplineId,
  });

  if (loadingDisciplines) return <Spinner size="sm" />;
  if (errorDisciplines)
    return (
      <ErrorMessage
        message="Error cargando disciplinas"
        onRetry={() => refetchDisciplines()}
      />
    );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-text-secondary">
          Disciplina
        </label>
        <select
          value={selectedDisciplineId ?? ""}
          onChange={(e) => {
            const val = e.target.value ? Number(e.target.value) : null;
            onDisciplineChange(val);
            onTechniqueChange(null);
          }}
          className="rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-red"
        >
          <option value="">Seleccionar disciplina...</option>
          {disciplines?.map((d) => (
            <option key={d.id} value={d.id}>
              {d.display_name}
            </option>
          ))}
        </select>
      </div>

      {selectedDisciplineId && (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-text-secondary">
            Técnica
          </label>
          {loadingTechniques ? (
            <Spinner size="sm" />
          ) : errorTechniques ? (
            <ErrorMessage
              message="Error cargando técnicas"
              onRetry={() => refetchTechniques()}
            />
          ) : (
            <select
              value={selectedTechniqueId ?? ""}
              onChange={(e) =>
                onTechniqueChange(e.target.value ? Number(e.target.value) : null)
              }
              className="rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-red"
            >
              <option value="">Seleccionar técnica...</option>
              {techniques?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.display_name}
                  {t.difficulty ? ` — ${t.difficulty}` : ""}
                </option>
              ))}
            </select>
          )}
        </div>
      )}
    </div>
  );
};

export default TechniqueSelector;
