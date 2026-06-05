/**
 * LandingPage
 * Public marketing page with hero section and feature highlights.
 */
import { Link } from "react-router-dom";
import Button from "@/components/ui/Button";

const FEATURES = [
  {
    icon: "🎯",
    title: "Análisis biomecánico IA",
    description:
      "MediaPipe detecta 33 articulaciones en tiempo real y calcula ángulos con precisión milimétrica.",
  },
  {
    icon: "🎥",
    title: "Overlay visual",
    description:
      "Tu vídeo devuelto con el esqueleto superpuesto: articulaciones en verde (correcto) y rojo (a mejorar).",
  },
  {
    icon: "📊",
    title: "Puntuación 0–100",
    description:
      "Puntuación global y sub-scores de potencia, equilibrio, alineación y velocidad.",
  },
  {
    icon: "🥋",
    title: "Sistema de cinturones",
    description:
      "Gana XP en cada análisis y progresa de cinturón blanco a negro como en el dojo real.",
  },
  {
    icon: "🏆",
    title: "Gamificación",
    description:
      "Rachas, badges, tabla de clasificación. Entrena cada día y desbloquea logros únicos.",
  },
  {
    icon: "👨‍🏫",
    title: "Modo instructor",
    description:
      "Crea grupos, invita alumnos y monitoriza su progreso desde un panel centralizado.",
  },
];

const LandingPage = () => (
  <div className="min-h-screen bg-bg-primary">
    {/* Navbar */}
    <nav className="flex items-center justify-between border-b border-border px-6 py-4">
      <span className="font-display text-2xl font-bold">
        <span className="text-brand-red">FIGHTER</span>
        <span className="text-text-primary">IA</span>
      </span>
      <div className="flex items-center gap-3">
        <Link to="/login">
          <Button variant="ghost" size="sm">
            Iniciar sesión
          </Button>
        </Link>
        <Link to="/register">
          <Button size="sm">Empezar gratis</Button>
        </Link>
      </div>
    </nav>

    {/* Hero */}
    <section className="mx-auto max-w-5xl px-6 py-20 text-center">
      <span className="mb-4 inline-block rounded-full border border-brand-red/30 bg-brand-red/10 px-4 py-1 text-sm font-medium text-brand-red">
        Análisis de vídeo con MediaPipe IA
      </span>
      <h1 className="mb-6 font-display text-5xl font-bold leading-tight text-text-primary sm:text-6xl lg:text-7xl">
        Mejora tu técnica con{" "}
        <span className="text-brand-red">inteligencia artificial</span>
      </h1>
      <p className="mx-auto mb-10 max-w-2xl text-lg text-text-secondary">
        Sube un vídeo de tu técnica, recibe análisis biomecánico en segundos:
        overlay visual, puntuación y correcciones priorizadas por impacto.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-4">
        <Link to="/register">
          <Button size="lg">Analizar mi técnica</Button>
        </Link>
        <Link to="/login">
          <Button variant="secondary" size="lg">
            Ya tengo cuenta
          </Button>
        </Link>
      </div>
    </section>

    {/* Features */}
    <section className="mx-auto max-w-6xl px-6 py-16">
      <h2 className="mb-12 text-center font-display text-3xl font-bold text-text-primary">
        Todo lo que necesitas para entrenar mejor
      </h2>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="rounded-xl border border-border bg-bg-secondary p-6 transition-colors hover:border-border-strong"
          >
            <span className="mb-3 block text-3xl">{f.icon}</span>
            <h3 className="mb-2 font-display text-lg font-semibold text-text-primary">
              {f.title}
            </h3>
            <p className="text-sm text-text-secondary">{f.description}</p>
          </div>
        ))}
      </div>
    </section>

    {/* CTA */}
    <section className="border-t border-border py-20 text-center">
      <h2 className="mb-4 font-display text-3xl font-bold text-text-primary">
        ¿Listo para entrenar con IA?
      </h2>
      <p className="mb-8 text-text-secondary">
        Regístrate gratis y analiza tu primera técnica hoy mismo.
      </p>
      <Link to="/register">
        <Button size="lg">Crear cuenta gratis</Button>
      </Link>
    </section>

    <footer className="border-t border-border px-6 py-6 text-center text-xs text-text-muted">
      © 2026 FighterIA — Entrena con inteligencia
    </footer>
  </div>
);

export default LandingPage;
