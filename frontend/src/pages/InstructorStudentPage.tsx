/**
 * InstructorStudentPage
 * Detailed student view for instructor: stats, recent analyses and comment history.
 */
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { instructorService } from "@/services/instructor.service";
import CommentBox from "@/components/instructor/CommentBox";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { formatRelativeTime, getScoreColor, formatScore, getBeltLabel } from "@/utils/format";
import { cn } from "@/utils/cn";

const InstructorStudentPage = () => {
  const { studentId } = useParams<{ studentId: string }>();
  const id = Number(studentId);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["student", id],
    queryFn: () => instructorService.getStudentDetail(id),
    enabled: !!id,
  });

  if (isLoading) return <Spinner />;
  if (isError)
    return <ErrorMessage message="Error cargando datos del alumno" onRetry={() => refetch()} />;
  if (!data) return null;

  const { user, recent_analyses, comments, progress_summary } = data;

  return (
    <div className="mx-auto max-w-4xl flex flex-col gap-6">
      {/* Header */}
      <div>
        <Link
          to="/instructor"
          className="text-sm text-text-muted hover:text-text-secondary transition-colors"
        >
          ← Panel Instructor
        </Link>
        <div className="mt-2 flex items-center gap-4">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.username}
              className="h-14 w-14 rounded-full object-cover border-2 border-border"
            />
          ) : (
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-red text-xl font-bold text-white">
              {user.username[0].toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="font-display text-2xl font-bold text-text-primary">
              {user.full_name}
            </h1>
            <p className="text-sm text-text-muted">
              @{user.username} · Cinturón {getBeltLabel(user.belt_level as Parameters<typeof getBeltLabel>[0])} · {user.xp.toLocaleString()} XP
            </p>
          </div>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Mejor score", value: formatScore(progress_summary.best_score) },
          { label: "Media", value: formatScore(progress_summary.average_score) },
          { label: "Total análisis", value: progress_summary.total_analyses },
          { label: "Últimos 30d", value: progress_summary.analyses_last_30_days },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-lg border border-border bg-bg-secondary p-3 text-center"
          >
            <p className={cn("font-display text-2xl font-bold", getScoreColor(typeof s.value === "string" ? parseFloat(s.value) : null))}>
              {s.value}
            </p>
            <p className="text-xs text-text-muted">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Recent analyses */}
      {recent_analyses.length > 0 && (
        <section>
          <h2 className="mb-3 font-display text-xl font-bold text-text-primary">
            Análisis recientes
          </h2>
          <div className="flex flex-col gap-2">
            {recent_analyses.map((a) => (
              <Link
                key={a.id}
                to={`/analysis/${a.id}`}
                className="flex items-center justify-between rounded-lg border border-border bg-bg-secondary px-4 py-3 hover:bg-bg-hover transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-text-primary">
                    {a.technique_display_name}
                  </p>
                  <p className="text-xs text-text-muted">
                    {formatRelativeTime(a.created_at)}
                  </p>
                </div>
                <span className={cn("font-display text-xl font-bold", getScoreColor(a.global_score))}>
                  {formatScore(a.global_score)}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Comments */}
      <section>
        <h2 className="mb-3 font-display text-xl font-bold text-text-primary">
          Comentarios del instructor
        </h2>
        {comments.length > 0 && (
          <div className="mb-4 flex flex-col gap-2">
            {comments.map((c) => (
              <div
                key={c.id}
                className="rounded-lg border border-border bg-bg-secondary p-3"
              >
                <p className="text-sm text-text-secondary">{c.content}</p>
                <p className="mt-1 text-xs text-text-muted">
                  {formatRelativeTime(c.created_at)}
                </p>
              </div>
            ))}
          </div>
        )}
        <CommentBox studentId={id} />
      </section>
    </div>
  );
};

export default InstructorStudentPage;
