/**
 * BusinessDashboardPage
 * Metrics dashboard for a specific gym: trainers, leads, conversion rate and plan.
 */
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { crmService } from "@/services/crm.service";
import StatsCard from "@/components/dashboard/StatsCard";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";

const BusinessDashboardPage = () => {
  const { gymId } = useParams<{ gymId: string }>();
  const parsedGymId = Number(gymId);

  const {
    data: metrics,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["gym-metrics", parsedGymId],
    queryFn: () => crmService.getGymMetrics(parsedGymId),
    enabled: !isNaN(parsedGymId),
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link
            to="/gyms"
            className="text-sm text-text-muted hover:text-text-secondary transition-colors"
          >
            ← Gimnasios
          </Link>
          <h1 className="font-display text-3xl font-bold text-text-primary mt-1">
            {metrics?.gym_name ?? "Dashboard del Gimnasio"}
          </h1>
          <p className="text-sm text-text-secondary">
            Métricas y rendimiento del gimnasio
          </p>
        </div>
        <Link to={`/gyms/${gymId}/leads`}>
          <Button variant="secondary">Ver Leads</Button>
        </Link>
      </div>

      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage
          message="Error cargando las métricas del gimnasio"
          onRetry={() => refetch()}
        />
      ) : metrics ? (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatsCard
              label="Entrenadores"
              value={metrics.total_trainers}
              icon={
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              }
            />
            <StatsCard
              label="Total Leads"
              value={metrics.total_leads}
              icon={
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              }
            />
            <StatsCard
              label="Tasa de Conversión"
              value={`${(metrics.conversion_rate * 100).toFixed(1)}%`}
              icon={
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              }
              trendUp={metrics.conversion_rate > 0.2}
            />
            <StatsCard
              label="Plan activo"
              value={metrics.plan.charAt(0).toUpperCase() + metrics.plan.slice(1)}
              icon={
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                  />
                </svg>
              }
            />
          </div>

          {/* Conversion bar */}
          <div className="rounded-lg border border-border bg-bg-secondary p-6">
            <h2 className="mb-4 font-display text-lg font-semibold text-text-primary">
              Tasa de conversión de leads
            </h2>
            <div className="flex items-center gap-4">
              <div className="flex-1 overflow-hidden rounded-full bg-bg-tertiary h-3">
                <div
                  className="h-3 rounded-full bg-brand-red transition-all"
                  style={{
                    width: `${Math.min(metrics.conversion_rate * 100, 100).toFixed(1)}%`,
                  }}
                />
              </div>
              <span className="shrink-0 text-sm font-semibold text-text-primary">
                {(metrics.conversion_rate * 100).toFixed(1)}%
              </span>
            </div>
            <p className="mt-2 text-xs text-text-muted">
              {metrics.total_leads === 0
                ? "Sin leads registrados aún"
                : `${Math.round(metrics.total_leads * metrics.conversion_rate)} de ${metrics.total_leads} leads convertidos`}
            </p>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default BusinessDashboardPage;
