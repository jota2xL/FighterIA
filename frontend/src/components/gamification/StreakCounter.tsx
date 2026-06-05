/**
 * StreakCounter
 * Displays current streak, max streak and shield count.
 */
interface StreakCounterProps {
  currentStreak: number;
  maxStreak: number;
  shields: number;
}

const StreakCounter = ({ currentStreak, maxStreak, shields }: StreakCounterProps) => (
  <div className="rounded-lg border border-border bg-bg-secondary p-4">
    <h3 className="mb-4 font-display text-lg font-semibold text-text-primary">
      Racha
    </h3>
    <div className="flex items-end gap-4">
      <div className="text-center">
        <p className="font-display text-5xl font-bold text-brand-red">
          {currentStreak}
        </p>
        <p className="mt-1 text-xs text-text-muted">Racha actual</p>
      </div>
      <div className="mb-1 flex flex-col gap-1 text-center">
        <div>
          <span className="font-display text-xl font-bold text-text-secondary">
            {maxStreak}
          </span>
          <p className="text-xs text-text-muted">Máxima racha</p>
        </div>
        <div>
          <span className="font-display text-xl font-bold text-brand-gold">
            {shields}
          </span>
          <p className="text-xs text-text-muted">Escudos</p>
        </div>
      </div>
    </div>
    {currentStreak >= 7 && (
      <p className="mt-3 text-xs text-brand-gold">
        🔥 ¡{currentStreak} días seguidos! Sigue así.
      </p>
    )}
  </div>
);

export default StreakCounter;
