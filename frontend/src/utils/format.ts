import type { BeltLevel } from "@/types/auth.types";

export function formatDate(dateString: string): string {
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(dateString));
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Hoy";
  if (diffDays === 1) return "Ayer";
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
  return formatDate(dateString);
}

export function formatScore(score: number | null): string {
  if (score === null) return "—";
  return score.toFixed(1);
}

export function getScoreColor(score: number | null): string {
  if (score === null) return "text-text-muted";
  if (score >= 80) return "text-score-excellent";
  if (score >= 60) return "text-score-good";
  return "text-score-poor";
}

export function getScoreBgColor(score: number | null): string {
  if (score === null) return "bg-bg-tertiary";
  if (score >= 80) return "bg-score-excellent/10";
  if (score >= 60) return "bg-score-good/10";
  return "bg-score-poor/10";
}

const BELT_LABELS: Record<BeltLevel, string> = {
  blanco: "Blanco",
  amarillo: "Amarillo",
  naranja: "Naranja",
  verde: "Verde",
  azul: "Azul",
  marron: "Marrón",
  negro: "Negro",
};

export function getBeltLabel(belt: BeltLevel): string {
  return BELT_LABELS[belt];
}

const BELT_ORDER: BeltLevel[] = [
  "blanco",
  "amarillo",
  "naranja",
  "verde",
  "azul",
  "marron",
  "negro",
];

export function getNextBelt(current: BeltLevel): BeltLevel | null {
  const idx = BELT_ORDER.indexOf(current);
  if (idx === -1 || idx === BELT_ORDER.length - 1) return null;
  return BELT_ORDER[idx + 1];
}

export function formatXP(xp: number): string {
  if (xp >= 1000) return `${(xp / 1000).toFixed(1)}k`;
  return String(xp);
}
