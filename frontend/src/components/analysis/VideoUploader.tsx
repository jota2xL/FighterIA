/**
 * VideoUploader
 * Drag & drop video upload with client-side format and duration validation.
 */
import React from "react";
import { cn } from "@/utils/cn";

const ALLOWED_EXTENSIONS = ["mp4", "mov", "avi"];
const MAX_DURATION_SECONDS = 60;

interface VideoUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  error?: string | null;
}

const VideoUploader = ({ onFileSelect, selectedFile, error }: VideoUploaderProps) => {
  const [dragging, setDragging] = React.useState(false);
  const [validationError, setValidationError] = React.useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const validateAndSelect = (file: File) => {
    setValidationError(null);
    const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setValidationError("Formato no válido. Usa MP4, MOV o AVI.");
      return;
    }

    const url = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.preload = "metadata";
    video.src = url;
    video.onloadedmetadata = () => {
      if (video.duration > MAX_DURATION_SECONDS) {
        setValidationError(
          `El vídeo supera los ${MAX_DURATION_SECONDS} segundos (duración: ${Math.round(video.duration)}s).`
        );
        URL.revokeObjectURL(url);
        return;
      }
      setPreviewUrl(url);
      onFileSelect(file);
    };
    video.onerror = () => {
      setValidationError("No se pudo leer el vídeo. Verifica el archivo.");
      URL.revokeObjectURL(url);
    };
  };

  React.useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) validateAndSelect(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) validateAndSelect(file);
  };

  const displayError = error ?? validationError;

  return (
    <div className="flex flex-col gap-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors",
          dragging
            ? "border-brand-red bg-brand-red/5"
            : "border-border hover:border-border-strong hover:bg-bg-hover",
          displayError && "border-brand-red-light"
        )}
        role="button"
        aria-label="Subir vídeo"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".mp4,.mov,.avi,video/mp4,video/quicktime,video/x-msvideo"
          className="hidden"
          onChange={handleChange}
        />
        <svg
          className="mx-auto mb-3 h-12 w-12 text-text-muted"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M15 10l4.553-2.069A1 1 0 0121 8.82v6.36a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
        {selectedFile ? (
          <div>
            <p className="font-medium text-text-primary">{selectedFile.name}</p>
            <p className="mt-1 text-sm text-text-muted">
              {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
            </p>
          </div>
        ) : (
          <div>
            <p className="font-medium text-text-secondary">
              Arrastra tu vídeo aquí o haz clic para seleccionar
            </p>
            <p className="mt-1 text-sm text-text-muted">
              MP4, MOV o AVI — máximo 60 segundos
            </p>
          </div>
        )}
      </div>

      {displayError && (
        <p className="text-sm text-brand-red-light">{displayError}</p>
      )}

      {previewUrl && (
        <div className="overflow-hidden rounded-lg border border-border">
          <video
            src={previewUrl}
            controls
            className="w-full max-h-64 bg-black"
            aria-label="Vista previa del vídeo"
          />
        </div>
      )}
    </div>
  );
};

export default VideoUploader;
