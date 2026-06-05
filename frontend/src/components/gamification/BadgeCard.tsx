/**
 * BadgeCard
 * Displays a gamification badge with earned/locked states and rarity indicator.
 */
import type { Badge } from "@/types/gamification.types";
import { cn } from "@/utils/cn";

interface BadgeCardProps {
  badge: Badge;
}

const RARITY_COLORS: Record<string, string> = {
  common: "border-border text-text-muted",
  rare: "border-score-good/40 text-score-good",
  epic: "border-brand-red/40 text-brand-red",
  legendary: "border-brand-gold/40 text-brand-gold",
};

const RARITY_LABELS: Record<string, string> = {
  common: "Común",
  rare: "Raro",
  epic: "Épico",
  legendary: "Legendario",
};

const BadgeCard = ({ badge }: BadgeCardProps) => (
  <div
    className={cn(
      "flex flex-col items-center gap-3 rounded-lg border p-4 text-center transition-opacity",
      RARITY_COLORS[badge.rarity],
      !badge.is_earned && "opacity-40 grayscale"
    )}
  >
    {badge.icon_url ? (
      <img
        src={badge.icon_url}
        alt={badge.display_name}
        className="h-12 w-12 object-contain"
      />
    ) : (
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-bg-tertiary text-2xl">
        🏆
      </div>
    )}

    <div>
      <p className="font-display text-sm font-semibold text-text-primary">
        {badge.display_name}
      </p>
      <p className="mt-0.5 text-xs text-text-muted">{badge.description}</p>
    </div>

    <div className="flex items-center gap-2">
      <span className="text-xs font-medium uppercase tracking-wide">
        {RARITY_LABELS[badge.rarity]}
      </span>
      <span className="text-xs text-brand-gold">+{badge.xp_reward} XP</span>
    </div>

    {badge.earned_at && (
      <span className="text-xs text-text-muted">
        {new Date(badge.earned_at).toLocaleDateString("es-ES")}
      </span>
    )}

    {!badge.is_earned && (
      <span className="text-xs text-text-muted italic">Sin desbloquear</span>
    )}
  </div>
);

export default BadgeCard;
