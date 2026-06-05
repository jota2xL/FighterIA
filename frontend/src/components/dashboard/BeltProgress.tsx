/**
 * BeltProgress
 * Displays current belt, XP progress bar and next belt target.
 * Receives data as props from DashboardPage (already fetched via /dashboard/me).
 */
import { getBeltLabel } from "@/utils/format";
import type { BeltLevel } from "@/types/auth.types";

const BELT_COLORS: Record<BeltLevel, string> = {
  blanco: "bg-belt-blanco",
  amarillo: "bg-belt-amarillo",
  naranja: "bg-belt-naranja",
  verde: "bg-belt-verde",
  azul: "bg-belt-azul",
  marron: "bg-belt-marron",
  negro: "bg-belt-negro border border-border-strong",
};

const BELT_TEXT: Record<BeltLevel, string> = {
  blanco: "text-gray-900",
  amarillo: "text-gray-900",
  naranja: "text-white",
  verde: "text-white",
  azul: "text-white",
  marron: "text-white",
  negro: "text-text-primary",
};

// XP thresholds per belt — mirrors backend gamification_service.BELT_THRESHOLDS
const BELT_THRESHOLDS: Record<BeltLevel, number> = {
  blanco: 0,
  amarillo: 501,
  naranja: 1501,
  verde: 3001,
  azul: 5001,
  marron: 8001,
  negro: 12001,
};

interface BeltProgressProps {
  currentBelt: BeltLevel;
  currentXp: number;
  xpForNextBelt: number | null;
  nextBeltName: string | null;
}

const BeltProgress = ({
  currentBelt,
  currentXp,
  xpForNextBelt,
  nextBeltName,
}: BeltProgressProps) => {
  const currentThreshold = BELT_THRESHOLDS[currentBelt] ?? 0;
  const progressPercent =
    xpForNextBelt && xpForNextBelt > currentThreshold
      ? Math.min(
          ((currentXp - currentThreshold) / (xpForNextBelt - currentThreshold)) * 100,
          100
        )
      : 100;
  const xpNeeded = xpForNextBelt ? Math.max(xpForNextBelt - currentXp, 0) : 0;

  return (
    <div className="rounded-lg border border-border bg-bg-secondary p-4">
      <h3 className="mb-4 font-display text-lg font-semibold text-text-primary">
        Cinturón
      </h3>
      <div className="flex items-center gap-4">
        {/* Belt badge */}
        <div
          className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-full font-display text-xs font-bold ${BELT_COLORS[currentBelt]} ${BELT_TEXT[currentBelt]}`}
        >
          {getBeltLabel(currentBelt).slice(0, 3).toUpperCase()}
        </div>

        <div className="flex-1">
          <div className="mb-1 flex items-baseline justify-between">
            <span className="font-display text-base font-semibold text-text-primary">
              {getBeltLabel(currentBelt)}
            </span>
            <span className="text-xs text-text-muted">
              {currentXp.toLocaleString()}
              {xpForNextBelt ? ` / ${xpForNextBelt.toLocaleString()} XP` : " XP"}
            </span>
          </div>

          {/* Progress bar */}
          <div className="h-2 overflow-hidden rounded-full bg-bg-tertiary">
            <div
              className="h-full rounded-full bg-brand-red transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
              role="progressbar"
              aria-valuenow={progressPercent}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>

          {nextBeltName ? (
            <p className="mt-1 text-xs text-text-muted">
              Próximo: Cinturón {getBeltLabel(nextBeltName as BeltLevel)} —{" "}
              {xpNeeded.toLocaleString()} XP restantes
            </p>
          ) : (
            <p className="mt-1 text-xs text-brand-gold">
              ¡Cinturón Negro alcanzado!
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default BeltProgress;
