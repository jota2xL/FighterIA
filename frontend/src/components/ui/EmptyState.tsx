/**
 * EmptyState
 * Displayed when a list or resource returns no results.
 */
interface EmptyStateProps {
  message: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

import React from "react";

const EmptyState = ({
  message,
  description,
  actionLabel,
  onAction,
  icon,
}: EmptyStateProps) => (
  <div className="flex flex-col items-center gap-4 py-16 text-center">
    {icon && <div className="text-text-muted">{icon}</div>}
    {!icon && (
      <svg
        className="h-12 w-12 text-text-muted"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
    )}
    <div>
      <p className="font-display text-lg font-semibold text-text-secondary">{message}</p>
      {description && (
        <p className="mt-1 text-sm text-text-muted">{description}</p>
      )}
    </div>
    {actionLabel && onAction && (
      <button
        onClick={onAction}
        className="rounded-md bg-brand-red px-4 py-2 text-sm font-semibold text-white hover:bg-brand-red-dark transition-colors"
      >
        {actionLabel}
      </button>
    )}
  </div>
);

export default EmptyState;
