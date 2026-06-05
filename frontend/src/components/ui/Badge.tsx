/**
 * Badge
 * Generic inline status badge with color variants.
 */
import { cn } from "@/utils/cn";

interface BadgeProps {
  label: string;
  variant?: "default" | "success" | "warning" | "danger" | "gold" | "muted";
  size?: "sm" | "md";
  className?: string;
}

const Badge = ({
  label,
  variant = "default",
  size = "sm",
  className,
}: BadgeProps) => {
  const variants = {
    default: "bg-bg-tertiary text-text-secondary border-border",
    success: "bg-score-correct/10 text-score-correct border-score-correct/20",
    warning: "bg-score-good/10 text-score-good border-score-good/20",
    danger: "bg-score-poor/10 text-score-poor border-score-poor/20",
    gold: "bg-brand-gold/10 text-brand-gold border-brand-gold/20",
    muted: "bg-bg-hover text-text-muted border-border",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-medium",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {label}
    </span>
  );
};

export default Badge;
