/**
 * BadgesPage
 * Displays all earned and available badges grouped by category.
 */
import { useBadges } from "@/hooks/useGamification";
import BadgeCard from "@/components/gamification/BadgeCard";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";

const CATEGORY_LABELS: Record<string, string> = {
  streak: "Rachas",
  score: "Puntuación",
  volume: "Volumen",
  technique: "Técnicas",
  special: "Especiales",
};

const BadgesPage = () => {
  const { data, isLoading, isError, refetch } = useBadges();

  if (isLoading) return <Spinner />;
  if (isError)
    return <ErrorMessage message="Error cargando badges" onRetry={() => refetch()} />;
  if (!data) return null;

  const allBadges = [...data.earned, ...data.available];
  const categories = [...new Set(allBadges.map((b) => b.category))];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-3xl font-bold text-text-primary">
          Logros
        </h1>
        <p className="mt-1 text-text-secondary">
          {data.total_earned} / {data.total_available} desbloqueados
        </p>
      </div>

      {/* Earned */}
      {data.earned.length > 0 && (
        <section>
          <h2 className="mb-4 font-display text-xl font-semibold text-text-primary">
            Conseguidos
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {data.earned.map((b) => (
              <BadgeCard key={b.id} badge={b} />
            ))}
          </div>
        </section>
      )}

      {/* By category */}
      {categories.map((cat) => {
        const badges = data.available.filter((b) => b.category === cat);
        if (badges.length === 0) return null;
        return (
          <section key={cat}>
            <h2 className="mb-4 font-display text-xl font-semibold text-text-primary">
              {CATEGORY_LABELS[cat] ?? cat}
            </h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {badges.map((b) => (
                <BadgeCard key={b.id} badge={b} />
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
};

export default BadgesPage;
