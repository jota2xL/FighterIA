/**
 * AnalysisResultPage
 * Full analysis result: overlay video, scores, joint table and prioritized feedback.
 */
import React from "react";
import { useParams, Link } from "react-router-dom";
import { useAnalysis } from "@/hooks/useAnalysis";
import { analysisService } from "@/services/analysis.service";
import { nlpService } from "@/services/nlp.service";
import VideoPlayer from "@/components/analysis/VideoPlayer";
import ScoreDisplay from "@/components/analysis/ScoreDisplay";
import JointResultsTable from "@/components/analysis/JointResultsTable";
import FeedbackList from "@/components/analysis/FeedbackList";
import Card, { CardHeader } from "@/components/ui/Card";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import { formatDate } from "@/utils/format";
import toast from "react-hot-toast";

const XP_TOAST_KEY = "xp-toast";

const AnalysisResultPage = () => {
  const { id } = useParams<{ id: string }>();
  const analysisId = Number(id);
  const { data, isLoading, isError, refetch } = useAnalysis(analysisId);
  const xpToastShown = React.useRef(false);

  // NLP Feedback state
  const [nlpFeedback, setNlpFeedback] = React.useState<string | null>(null);
  const [nlpLoading, setNlpLoading] = React.useState(false);
  const [nlpError, setNlpError] = React.useState<string | null>(null);

  const handleGenerateNlpFeedback = async () => {
    if (!data || data.status !== "completed") return;
    setNlpLoading(true);
    setNlpError(null);
    try {
      const result = await nlpService.getNlpFeedback({
        potencia: data.power_score ?? 0,
        equilibrio: data.balance_score ?? 0,
        alineacion: data.alignment_score ?? 0,
        velocidad: data.speed_score ?? 0,
      });
      setNlpFeedback(result.feedback);
    } catch {
      setNlpError("Error al generar el feedback con IA. Inténtalo de nuevo.");
    } finally {
      setNlpLoading(false);
    }
  };

  React.useEffect(() => {
    if (data?.xp_awarded && data.xp_awarded > 0 && !xpToastShown.current) {
      xpToastShown.current = true;
      toast.success(`¡+${data.xp_awarded} XP ganados!`, { id: XP_TOAST_KEY });
    }
  }, [data?.xp_awarded]);

  if (isLoading) return <Spinner motivational />;
  if (isError)
    return (
      <ErrorMessage
        message="Error cargando el análisis"
        onRetry={() => refetch()}
      />
    );
  if (!data) return null;

  const overlayUrl = analysisService.getOverlayUrl(analysisId);
  const originalUrl = analysisService.getOriginalUrl(analysisId);

  return (
    <div className="mx-auto max-w-6xl">
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Link
              to="/history"
              className="text-sm text-text-muted hover:text-text-secondary transition-colors"
            >
              ← Historial
            </Link>
          </div>
          <h1 className="font-display text-3xl font-bold text-text-primary">
            {data.technique.display_name}
          </h1>
          <div className="mt-1 flex items-center gap-2">
            <Badge label={data.technique.discipline} variant="default" />
            <span className="text-xs text-text-muted">
              {formatDate(data.created_at)}
            </span>
          </div>
        </div>
        {/* Download buttons */}
        <div className="flex gap-2">
          <a href={overlayUrl} download target="_blank" rel="noreferrer">
            <Button variant="secondary" size="sm">
              ↓ Overlay
            </Button>
          </a>
          <a href={originalUrl} download target="_blank" rel="noreferrer">
            <Button variant="secondary" size="sm">
              ↓ Original
            </Button>
          </a>
        </div>
      </div>

      {/* Failed state */}
      {data.status === "failed" && (
        <ErrorMessage
          message={
            data.error_message ?? "El análisis falló. Por favor sube el vídeo de nuevo."
          }
        />
      )}

      {/* Main content */}
      {data.status === "completed" && (
        <div className="flex flex-col gap-8">
          {/* Video + Score */}
          <div className="grid gap-6 lg:grid-cols-2">
            <VideoPlayer overlayUrl={overlayUrl} originalUrl={originalUrl} />
            <div className="flex items-center justify-center rounded-lg border border-border bg-bg-secondary p-6">
              <ScoreDisplay analysis={data} />
            </div>
          </div>

          {/* Joint results */}
          {data.joint_results.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-xl font-bold text-text-primary">
                Análisis articular
              </h2>
              <JointResultsTable joints={data.joint_results} />
            </section>
          )}

          {/* Feedback */}
          {data.feedback.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-xl font-bold text-text-primary">
                Correcciones prioritarias
              </h2>
              <FeedbackList feedback={data.feedback} />
            </section>
          )}

          {/* NLP Enriched Feedback */}
          <section>
            <h2 className="mb-3 font-display text-xl font-bold text-text-primary">
              Feedback IA Enriquecido
            </h2>
            {!nlpFeedback && !nlpLoading && (
              <Card>
                <div className="flex flex-col items-center gap-4 py-4 text-center">
                  <p className="text-sm text-text-secondary">
                    Genera un análisis detallado con lenguaje natural basado en tus puntuaciones.
                  </p>
                  <Button onClick={handleGenerateNlpFeedback}>
                    Generar Feedback con IA
                  </Button>
                </div>
              </Card>
            )}
            {nlpLoading && (
              <Card>
                <div className="flex items-center justify-center gap-3 py-6">
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-bg-hover border-t-brand-red" />
                  <span className="text-sm text-text-secondary">Generando feedback con IA...</span>
                </div>
              </Card>
            )}
            {nlpError && !nlpLoading && (
              <div className="flex flex-col gap-3">
                <ErrorMessage
                  message={nlpError}
                  onRetry={handleGenerateNlpFeedback}
                />
              </div>
            )}
            {nlpFeedback && !nlpLoading && (
              <Card className="border-brand-red/30 bg-brand-red/5">
                <CardHeader
                  title="Análisis IA"
                  subtitle="Generado con procesamiento de lenguaje natural"
                  action={
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleGenerateNlpFeedback}
                    >
                      Regenerar
                    </Button>
                  }
                />
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-text-primary">
                  {nlpFeedback}
                </p>
              </Card>
            )}
          </section>
        </div>
      )}

      {/* Processing state */}
      {(data.status === "pending" || data.status === "processing") && (
        <div className="py-16 text-center">
          <Spinner size="lg" motivational />
          <p className="mt-4 text-sm text-text-muted">
            El análisis aún está en proceso. Recarga en unos segundos.
          </p>
        </div>
      )}
    </div>
  );
};

export default AnalysisResultPage;
