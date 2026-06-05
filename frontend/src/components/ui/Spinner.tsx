/**
 * Spinner
 * Animated loading indicator with optional motivational cycling messages.
 */
import React from "react";

const MOTIVATIONAL_MESSAGES = [
  "Analizando tu técnica...",
  "Calculando ángulos articulares...",
  "Comparando con referencias biomecánicas...",
  "Generando overlay visual...",
  "Evaluando tu potencia...",
  "¡Casi listo! Preparando tu feedback...",
];

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  motivational?: boolean;
}

const Spinner = ({ size = "md", motivational = false }: SpinnerProps) => {
  const [msgIdx, setMsgIdx] = React.useState(0);

  React.useEffect(() => {
    if (!motivational) return;
    const interval = setInterval(
      () => setMsgIdx((i) => (i + 1) % MOTIVATIONAL_MESSAGES.length),
      2500
    );
    return () => clearInterval(interval);
  }, [motivational]);

  const sizeClass = {
    sm: "h-5 w-5",
    md: "h-10 w-10",
    lg: "h-16 w-16",
  }[size];

  return (
    <div className="flex flex-col items-center gap-4 py-8">
      <div
        className={`animate-spin rounded-full border-2 border-bg-hover border-t-brand-red ${sizeClass}`}
      />
      {motivational && (
        <p className="max-w-xs animate-pulse text-center text-sm text-text-secondary">
          {MOTIVATIONAL_MESSAGES[msgIdx]}
        </p>
      )}
    </div>
  );
};

export default Spinner;
