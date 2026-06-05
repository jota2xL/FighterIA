/**
 * CertificatePage
 * Verifies a blockchain certificate by hash and displays its details with a QR code.
 */
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { blockchainService } from "@/services/blockchain.service";
import Card, { CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { formatDate } from "@/utils/format";

const CertificatePage = () => {
  const { hash } = useParams<{ hash: string }>();

  const {
    data,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["certificate", hash],
    queryFn: () => blockchainService.verifyCertificate(hash!),
    enabled: Boolean(hash),
    retry: false,
  });

  if (isLoading) return <Spinner />;
  if (isError)
    return (
      <ErrorMessage
        message="Error al verificar el certificado"
        onRetry={() => refetch()}
      />
    );

  return (
    <div className="mx-auto max-w-2xl">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/dashboard"
          className="text-sm text-text-muted hover:text-text-secondary transition-colors"
        >
          ← Dashboard
        </Link>
        <h1 className="mt-1 font-display text-3xl font-bold text-text-primary">
          Verificación de Certificado
        </h1>
      </div>

      {data?.valid && data.certificate ? (
        <div className="flex flex-col gap-6">
          {/* Valid banner */}
          <div className="flex items-center gap-3 rounded-lg border border-green-500/30 bg-green-500/10 px-5 py-4">
            <svg
              className="h-6 w-6 shrink-0 text-green-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <p className="text-sm font-semibold text-green-400">Certificado válido</p>
              <p className="text-xs text-green-400/70">
                Este certificado ha sido verificado en blockchain
              </p>
            </div>
          </div>

          {/* Certificate details */}
          <Card>
            <CardHeader title="Detalles del Certificado" />
            <dl className="flex flex-col gap-3">
              <div className="flex flex-col gap-0.5">
                <dt className="text-xs font-medium text-text-muted uppercase tracking-wide">
                  Hash de certificado
                </dt>
                <dd className="break-all rounded bg-bg-tertiary px-3 py-2 font-mono text-xs text-text-primary">
                  {data.certificate.hash}
                </dd>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-0.5">
                  <dt className="text-xs font-medium text-text-muted uppercase tracking-wide">
                    ID de Análisis
                  </dt>
                  <dd className="text-sm font-semibold text-text-primary">
                    #{data.certificate.analysis_id}
                  </dd>
                </div>
                <div className="flex flex-col gap-0.5">
                  <dt className="text-xs font-medium text-text-muted uppercase tracking-wide">
                    Verificaciones
                  </dt>
                  <dd className="text-sm font-semibold text-text-primary">
                    {data.certificate.verified_count}
                  </dd>
                </div>
                <div className="flex flex-col gap-0.5">
                  <dt className="text-xs font-medium text-text-muted uppercase tracking-wide">
                    Fecha de emisión
                  </dt>
                  <dd className="text-sm font-semibold text-text-primary">
                    {formatDate(data.certificate.issued_at)}
                  </dd>
                </div>
                <div className="flex flex-col gap-0.5">
                  <dt className="text-xs font-medium text-text-muted uppercase tracking-wide">
                    ID Certificado
                  </dt>
                  <dd className="text-sm font-semibold text-text-primary">
                    #{data.certificate.id}
                  </dd>
                </div>
              </div>
            </dl>
          </Card>

          {/* QR Code */}
          <Card>
            <CardHeader
              title="Código QR de verificación"
              subtitle="Escanea para verificar la autenticidad del certificado"
            />
            <div className="flex flex-col items-center gap-4">
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(data.certificate.hash)}&size=200x200`}
                alt={`QR del certificado ${data.certificate.hash}`}
                width={200}
                height={200}
                className="rounded-lg border border-border bg-white p-2"
              />
              <p className="text-xs text-text-muted text-center">
                El código QR contiene el hash del certificado para verificación externa
              </p>
            </div>
          </Card>

          {/* Link to analysis */}
          <Link to={`/analysis/${data.certificate.analysis_id}`}>
            <Button variant="secondary" className="w-full">
              Ver Análisis #{data.certificate.analysis_id}
            </Button>
          </Link>
        </div>
      ) : (
        /* Invalid certificate */
        <div className="flex flex-col items-center gap-4 rounded-lg border border-brand-red/30 bg-brand-red/5 px-6 py-12 text-center">
          <svg
            className="h-12 w-12 text-brand-red"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h2 className="text-lg font-semibold text-brand-red-light">
              Certificado no válido
            </h2>
            <p className="mt-1 text-sm text-text-muted">
              {data?.message ?? "El hash proporcionado no corresponde a ningún certificado registrado."}
            </p>
          </div>
          <Link to="/dashboard">
            <Button variant="secondary">Volver al Dashboard</Button>
          </Link>
        </div>
      )}
    </div>
  );
};

export default CertificatePage;
