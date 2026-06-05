/**
 * NewAnalysisPage
 * Multi-step form: discipline/technique selection → video upload → processing loader.
 */
import React from "react";
import { useCreateAnalysis } from "@/hooks/useAnalysis";
import TechniqueSelector from "@/components/analysis/TechniqueSelector";
import VideoUploader from "@/components/analysis/VideoUploader";
import Spinner from "@/components/ui/Spinner";
import Button from "@/components/ui/Button";
import { cn } from "@/utils/cn";

type Step = 1 | 2 | 3;

const STEPS = [
  { number: 1, label: "Técnica" },
  { number: 2, label: "Vídeo" },
  { number: 3, label: "Análisis" },
];

const NewAnalysisPage = () => {
  const [step, setStep] = React.useState<Step>(1);
  const [disciplineId, setDisciplineId] = React.useState<number | null>(null);
  const [techniqueId, setTechniqueId] = React.useState<number | null>(null);
  const [videoFile, setVideoFile] = React.useState<File | null>(null);

  const createAnalysis = useCreateAnalysis();

  const handleSubmit = () => {
    if (!techniqueId || !videoFile) return;
    setStep(3);
    createAnalysis.mutate({ techniqueId, video: videoFile });
  };

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 font-display text-3xl font-bold text-text-primary">
        Nuevo análisis
      </h1>

      {/* Step indicator */}
      <div className="mb-8 flex items-center gap-2">
        {STEPS.map((s, idx) => (
          <React.Fragment key={s.number}>
            <div
              className={cn(
                "flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium transition-colors",
                step === s.number
                  ? "bg-brand-red text-white"
                  : step > s.number
                  ? "bg-bg-tertiary text-score-correct"
                  : "bg-bg-tertiary text-text-muted"
              )}
            >
              <span>{s.number}</span>
              <span className="hidden sm:inline">{s.label}</span>
            </div>
            {idx < STEPS.length - 1 && (
              <div
                className={cn(
                  "h-px flex-1 transition-colors",
                  step > s.number ? "bg-brand-red/40" : "bg-border"
                )}
              />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step 1: Technique selection */}
      {step === 1 && (
        <div className="rounded-xl border border-border bg-bg-secondary p-6">
          <h2 className="mb-1 font-display text-xl font-semibold text-text-primary">
            Selecciona la técnica
          </h2>
          <p className="mb-6 text-sm text-text-secondary">
            Elige la disciplina y la técnica que vas a ejecutar en el vídeo.
          </p>
          <TechniqueSelector
            selectedDisciplineId={disciplineId}
            selectedTechniqueId={techniqueId}
            onDisciplineChange={setDisciplineId}
            onTechniqueChange={setTechniqueId}
          />
          <div className="mt-6 flex justify-end">
            <Button
              onClick={() => setStep(2)}
              disabled={!techniqueId}
            >
              Siguiente →
            </Button>
          </div>
        </div>
      )}

      {/* Step 2: Video upload */}
      {step === 2 && (
        <div className="rounded-xl border border-border bg-bg-secondary p-6">
          <h2 className="mb-1 font-display text-xl font-semibold text-text-primary">
            Sube tu vídeo
          </h2>
          <p className="mb-6 text-sm text-text-secondary">
            MP4, MOV o AVI — máximo 60 segundos de duración.
          </p>
          <VideoUploader
            onFileSelect={setVideoFile}
            selectedFile={videoFile}
            error={createAnalysis.isError ? "Error al procesar. Inténtalo de nuevo." : null}
          />
          <div className="mt-6 flex justify-between">
            <Button variant="ghost" onClick={() => setStep(1)}>
              ← Atrás
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!videoFile}
              isLoading={createAnalysis.isPending}
            >
              Analizar técnica
            </Button>
          </div>
        </div>
      )}

      {/* Step 3: Processing */}
      {step === 3 && (
        <div className="rounded-xl border border-border bg-bg-secondary p-12 text-center">
          <h2 className="mb-2 font-display text-2xl font-bold text-text-primary">
            Procesando tu vídeo
          </h2>
          <p className="mb-8 text-sm text-text-secondary">
            Esto puede tardar entre 30 segundos y 2 minutos según la duración del vídeo.
          </p>
          <Spinner size="lg" motivational />
        </div>
      )}
    </div>
  );
};

export default NewAnalysisPage;
