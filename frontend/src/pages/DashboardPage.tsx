/**
 * DashboardPage
 * Main authenticated dashboard with stats, belt progress, charts and recent analyses.
 */
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { dashboardService } from "@/services/dashboard.service";
import { useAuthStore } from "@/store/auth.store";
import StatsCard from "@/components/dashboard/StatsCard";
import BeltProgress from "@/components/dashboard/BeltProgress";
import ProgressChart from "@/components/dashboard/ProgressChart";
import ActivityHeatmap from "@/components/dashboard/ActivityHeatmap";
import StreakCounter from "@/components/gamification/StreakCounter";
import AnalysisResultCard from "@/components/analysis/AnalysisResultCard";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { formatScore, formatXP } from "@/utils/format";

const DashboardPage = () => {
  const user = useAuthStore((s) => s.user);

  const {
    data: stats,
    isLoading: loadingStats,
    isError: errorStats,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardService.getStats,
  });

  const { data: recent, isLoading: loadingRecent } = useQuery({
    queryKey: ["recent-analyses"],
    queryFn: () => dashboardService.getRecentAnalyses(3),
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-primary">
            Hola, {user?.username} 👊
          </h1>
          <p className="text-sm text-text-secondary">
            {new Date().toLocaleDateString("es-ES", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </p>
        </div>
        <Link to="/analysis/new">
          <Button>Nuevo análisis</Button>
        </Link>
      </div>

      {/* Stats grid */}
      {loadingStats ? (
        <Spinner />
      ) : errorStats ? (
        <ErrorMessage
          message="Error cargando estadísticas"
          onRetry={() => refetchStats()}
        />
      ) : stats ? (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatsCard
            label="Análisis realizados"
            value={stats.total_analyses}
            icon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          />
          <StatsCard
            label="Mejor puntuación"
            value={formatScore(stats.best_score)}
            icon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            }
          />
          <StatsCard
            label="XP total"
            value={formatXP(stats.xp)}
            icon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            }
          />
          <StatsCard
            label="Media de score"
            value={formatScore(stats.average_score)}
            icon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            }
          />
        </div>
      ) : null}

      {/* Belt + Streak */}
      <div className="grid gap-4 md:grid-cols-2">
        {stats && (
          <BeltProgress
            currentBelt={stats.belt_level}
            currentXp={stats.xp}
            xpForNextBelt={stats.xp_for_next_belt}
            nextBeltName={stats.xp_next_belt_name}
          />
        )}
        {user && (
          <StreakCounter
            currentStreak={user.current_streak}
            maxStreak={user.max_streak}
            shields={user.streak_shields}
          />
        )}
      </div>

      {/* Progress Chart */}
      <ProgressChart />

      {/* Activity Heatmap */}
      <ActivityHeatmap />

      {/* Recent analyses */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-bold text-text-primary">
            Análisis recientes
          </h2>
          <Link
            to="/history"
            className="text-sm text-brand-red hover:text-brand-red-light transition-colors"
          >
            Ver todos →
          </Link>
        </div>

        {loadingRecent ? (
          <Spinner size="sm" />
        ) : recent && recent.length > 0 ? (
          <div className="flex flex-col gap-3">
            {recent.map((a) => (
              <AnalysisResultCard key={a.id} analysis={{
                id: a.id,
                technique_display_name: a.technique_display_name,
                discipline_name: a.discipline_name ?? "",
                global_score: a.global_score,
                status: "completed",
                video_overlay_url: a.video_overlay_url,
                created_at: a.created_at,
              }} />
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-dashed border-border p-8 text-center">
            <p className="text-text-muted">
              Aún no has realizado ningún análisis.
            </p>
            <Link to="/analysis/new" className="mt-3 inline-block">
              <Button size="sm">Empieza ahora</Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
