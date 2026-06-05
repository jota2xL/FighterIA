/**
 * HistoryPage
 * Paginated analysis history with discipline filter.
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { disciplineService } from "@/services/analysis.service";
import { useAnalysisHistory } from "@/hooks/useAnalysis";
import type { Discipline } from "@/types/analysis.types";
import AnalysisResultCard from "@/components/analysis/AnalysisResultCard";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import EmptyState from "@/components/ui/EmptyState";
import Button from "@/components/ui/Button";
import { Link } from "react-router-dom";

const PAGE_SIZE = 20;

const HistoryPage = () => {
  const [page, setPage] = React.useState(1);
  const [disciplineId, setDisciplineId] = React.useState<number | undefined>(undefined);

  const { data: disciplines } = useQuery<Discipline[]>({
    queryKey: ["disciplines"],
    queryFn: disciplineService.getAll,
  });

  const { data, isLoading, isError, refetch } = useAnalysisHistory(
    page,
    PAGE_SIZE,
    disciplineId
  );

  React.useEffect(() => {
    setPage(1);
  }, [disciplineId]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display text-3xl font-bold text-text-primary">
          Historial de análisis
        </h1>
        <Link to="/analysis/new">
          <Button size="sm">Nuevo análisis</Button>
        </Link>
      </div>

      {/* Filter */}
      {disciplines && disciplines.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setDisciplineId(undefined)}
            className={`rounded-full border px-3 py-1 text-sm font-medium transition-colors ${
              !disciplineId
                ? "border-brand-red bg-brand-red/10 text-text-primary"
                : "border-border text-text-secondary hover:bg-bg-hover"
            }`}
          >
            Todas
          </button>
          {disciplines.map((d) => (
            <button
              key={d.id}
              onClick={() => setDisciplineId(d.id)}
              className={`rounded-full border px-3 py-1 text-sm font-medium transition-colors ${
                disciplineId === d.id
                  ? "border-brand-red bg-brand-red/10 text-text-primary"
                  : "border-border text-text-secondary hover:bg-bg-hover"
              }`}
            >
              {d.display_name}
            </button>
          ))}
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage message="Error cargando el historial" onRetry={() => refetch()} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          message="Sin análisis todavía"
          description="Sube tu primer vídeo para empezar."
          actionLabel="Nuevo análisis"
          onAction={() => window.location.assign("/analysis/new")}
        />
      ) : (
        <>
          <div className="flex flex-col gap-3">
            {data.items.map((a) => (
              <AnalysisResultCard key={a.id} analysis={a} />
            ))}
          </div>

          {/* Pagination */}
          {data.pages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                ← Anterior
              </Button>
              <span className="text-sm text-text-muted">
                {page} / {data.pages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page === data.pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Siguiente →
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default HistoryPage;
