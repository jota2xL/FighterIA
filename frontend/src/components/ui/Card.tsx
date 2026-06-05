/**
 * Card
 * Dark-themed container card with optional hover and header.
 */
import React from "react";
import { cn } from "@/utils/cn";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}

const Card = ({ children, className, hoverable = false, onClick }: CardProps) => (
  <div
    onClick={onClick}
    className={cn(
      "rounded-lg border border-border bg-bg-secondary p-4",
      hoverable && "cursor-pointer transition-colors hover:border-border-strong hover:bg-bg-hover",
      onClick && "cursor-pointer",
      className
    )}
  >
    {children}
  </div>
);

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

export const CardHeader = ({ title, subtitle, action, className }: CardHeaderProps) => (
  <div className={cn("mb-4 flex items-start justify-between", className)}>
    <div>
      <h3 className="font-display text-lg font-semibold text-text-primary">{title}</h3>
      {subtitle && <p className="mt-0.5 text-sm text-text-secondary">{subtitle}</p>}
    </div>
    {action && <div className="ml-4 shrink-0">{action}</div>}
  </div>
);

export default Card;
