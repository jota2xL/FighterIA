/**
 * FeedbackList
 * Prioritized list of corrections, each expandable with biomechanical explanation.
 */
import React from "react";
import type { FeedbackItem } from "@/types/analysis.types";
import { cn } from "@/utils/cn";

interface FeedbackListProps {
  feedback: FeedbackItem[];
}

const FeedbackList = ({ feedback }: FeedbackListProps) => {
  const [openIdx, setOpenIdx] = React.useState<number | null>(0);

  if (feedback.length === 0) return null;

  const sorted = [...feedback].sort((a, b) => a.priority_order - b.priority_order);

  return (
    <div className="flex flex-col gap-2">
      {sorted.map((item, idx) => {
        const isOpen = openIdx === idx;
        return (
          <div
            key={item.priority_order}
            className={cn(
              "rounded-lg border transition-colors",
              isOpen ? "border-brand-red/30 bg-brand-red/5" : "border-border bg-bg-secondary"
            )}
          >
            <button
              onClick={() => setOpenIdx(isOpen ? null : idx)}
              className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left"
              aria-expanded={isOpen}
            >
              <div className="flex items-center gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-red text-xs font-bold text-white">
                  {item.priority_order}
                </span>
                <span className="font-medium text-text-primary">
                  {item.correction_title}
                </span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="hidden text-xs text-text-muted sm:inline">
                  Impacto: {item.impact_score.toFixed(0)}%
                </span>
                <svg
                  className={cn(
                    "h-4 w-4 text-text-muted transition-transform",
                    isOpen && "rotate-180"
                  )}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {isOpen && (
              <div className="border-t border-border/50 px-4 pb-4 pt-3">
                <p className="mb-3 text-sm text-text-secondary">
                  {item.correction_text}
                </p>
                <div className="mb-3 rounded-md bg-bg-tertiary p-3">
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-text-muted">
                    Explicación biomecánica
                  </p>
                  <p className="text-sm text-text-secondary">
                    {item.biomechanical_explanation}
                  </p>
                </div>
                <div className="rounded-md bg-bg-tertiary p-3">
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-text-muted">
                    Ejercicio sugerido
                  </p>
                  <p className="text-sm text-text-secondary">
                    {item.exercise_suggestion}
                  </p>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default FeedbackList;
