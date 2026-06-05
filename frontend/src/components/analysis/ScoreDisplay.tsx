/**
 * ScoreDisplay
 * Global score with Rajdhani typography and 4 sub-score breakdown cards.
 */
import { cn } from "@/utils/cn";
import type { Analysis } from "@/types/analysis.types";

interface ScoreDisplayProps {
  analysis: Analysis;
}

const getScoreColor = (score: number | null) => {
  if (score === null) return "text-text-muted";
  if (score >= 80) return "text-score-excellent";
  if (score >= 60) return "text-score-good";
  return "text-score-poor";
};

const getScoreBg = (score: number | null) => {
  if (score === null) return "border-border";
  if (score >= 80) return "border-score-excellent/30";
  if (score >= 60) return "border-score-good/30";
  return "border-score-poor/30";
};

interface SubScoreCardProps {
  label: string;
  score: number | null;
}

const SubScoreCard = ({ label, score }: SubScoreCardProps) => (
  <div
    className={cn(
      "flex flex-col items-center gap-1 rounded-lg border p-3",
      "bg-bg-tertiary",
      getScoreBg(score)
    )}
  >
    <span className="text-xs font-medium text-text-secondary uppercase tracking-wide">
      {label}
    </span>
    <span
      className={cn("font-display text-2xl font-bold", getScoreColor(score))}
    >
      {score !== null ? score.toFixed(0) : "—"}
    </span>
  </div>
);

const ScoreDisplay = ({ analysis }: ScoreDisplayProps) => {
  const score = analysis.global_score;

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Global score */}
      <div className="text-center">
        <p className="mb-1 text-sm font-medium text-text-secondary uppercase tracking-widest">
          Puntuación Global
        </p>
        <span
          className={cn(
            "font-display text-8xl font-bold leading-none",
            getScoreColor(score)
          )}
        >
          {score !== null ? score.toFixed(0) : "—"}
        </span>
        <span className="ml-2 font-display text-3xl text-text-muted">/100</span>
      </div>

      {/* Sub-scores */}
      <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-4">
        <SubScoreCard label="Potencia" score={analysis.power_score} />
        <SubScoreCard label="Equilibrio" score={analysis.balance_score} />
        <SubScoreCard label="Alineación" score={analysis.alignment_score} />
        <SubScoreCard label="Velocidad" score={analysis.speed_score} />
      </div>
    </div>
  );
};

export default ScoreDisplay;
