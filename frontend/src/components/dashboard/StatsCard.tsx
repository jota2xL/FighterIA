/**
 * StatsCard
 * Single metric display card for the dashboard stats grid.
 */
import React from "react";
import { cn } from "@/utils/cn";

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
  trendUp?: boolean;
  className?: string;
}

const StatsCard = ({ label, value, icon, trend, trendUp, className }: StatsCardProps) => (
  <div className={cn("rounded-lg border border-border bg-bg-secondary p-4", className)}>
    <div className="flex items-start justify-between">
      <div className="rounded-md bg-bg-tertiary p-2 text-brand-red">{icon}</div>
      {trend && (
        <span
          className={cn(
            "text-xs font-medium",
            trendUp ? "text-score-correct" : "text-score-poor"
          )}
        >
          {trendUp ? "↑" : "↓"} {trend}
        </span>
      )}
    </div>
    <p className="mt-3 font-display text-3xl font-bold text-text-primary">{value}</p>
    <p className="mt-1 text-sm text-text-secondary">{label}</p>
  </div>
);

export default StatsCard;
