/**
 * XPBar
 * Compact XP display with animated bar for the navbar or profile section.
 */
import { formatXP } from "@/utils/format";

interface XPBarProps {
  xp: number;
  xpForNext: number;
  showLabel?: boolean;
}

const XPBar = ({ xp, xpForNext, showLabel = true }: XPBarProps) => {
  const percent = xpForNext > 0 ? Math.min((xp / xpForNext) * 100, 100) : 100;

  return (
    <div className="flex flex-col gap-1">
      {showLabel && (
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-brand-gold">
            {formatXP(xp)} XP
          </span>
          <span className="text-xs text-text-muted">
            /{formatXP(xpForNext)} XP
          </span>
        </div>
      )}
      <div className="h-1.5 overflow-hidden rounded-full bg-bg-tertiary">
        <div
          className="h-full rounded-full bg-brand-gold transition-all duration-700"
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${formatXP(xp)} de ${formatXP(xpForNext)} XP`}
        />
      </div>
    </div>
  );
};

export default XPBar;
