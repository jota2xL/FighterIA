/**
 * AnalysisResultCard
 * Compact summary card for displaying an analysis in lists.
 */
import { Link } from "react-router-dom";
import type { AnalysisListItem } from "@/types/analysis.types";
import { formatRelativeTime, getScoreColor, formatScore } from "@/utils/format";
import { cn } from "@/utils/cn";
import Badge from "@/components/ui/Badge";

interface AnalysisResultCardProps {
  analysis: AnalysisListItem;
}

const STATUS_BADGE: Record<string, { label: string; variant: "success" | "warning" | "danger" | "muted" }> = {
  completed: { label: "Completado", variant: "success" },
  processing: { label: "Procesando", variant: "warning" },
  pending: { label: "Pendiente", variant: "muted" },
  failed: { label: "Error", variant: "danger" },
};

const AnalysisResultCard = ({ analysis }: AnalysisResultCardProps) => {
  const badgeInfo = STATUS_BADGE[analysis.status] ?? STATUS_BADGE.pending;

  return (
    <Link
      to={`/analysis/${analysis.id}`}
      className="flex items-center gap-4 rounded-lg border border-border bg-bg-secondary p-4 transition-colors hover:border-border-strong hover:bg-bg-hover"
    >
      {/* Thumbnail */}
      <div className="h-16 w-24 shrink-0 overflow-hidden rounded-md bg-black">
        {analysis.video_overlay_url ? (
          <video
            src={analysis.video_overlay_url}
            className="h-full w-full object-cover"
            muted
            preload="metadata"
            aria-hidden="true"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <svg className="h-6 w-6 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.069A1 1 0 0121 8.82v6.36a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <p className="truncate font-medium text-text-primary">
          {analysis.technique_display_name}
        </p>
        <p className="text-xs text-text-muted">{analysis.discipline_name}</p>
        <div className="flex items-center gap-2">
          <Badge label={badgeInfo.label} variant={badgeInfo.variant} />
          <span className="text-xs text-text-muted">
            {formatRelativeTime(analysis.created_at)}
          </span>
        </div>
      </div>

      {/* Score */}
      <div className="shrink-0 text-right">
        <span
          className={cn(
            "font-display text-3xl font-bold",
            getScoreColor(analysis.global_score)
          )}
        >
          {formatScore(analysis.global_score)}
        </span>
        {analysis.global_score !== null && (
          <span className="ml-0.5 text-sm text-text-muted">/100</span>
        )}
      </div>
    </Link>
  );
};

export default AnalysisResultCard;
