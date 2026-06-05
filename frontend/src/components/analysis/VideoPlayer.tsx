/**
 * VideoPlayer
 * Video player component for overlay and original video display with toggle.
 */
import React from "react";
import { cn } from "@/utils/cn";

interface VideoPlayerProps {
  overlayUrl: string;
  originalUrl: string;
}

const VideoPlayer = ({ overlayUrl, originalUrl }: VideoPlayerProps) => {
  const [showOverlay, setShowOverlay] = React.useState(true);
  const videoRef = React.useRef<HTMLVideoElement>(null);

  const currentUrl = showOverlay ? overlayUrl : originalUrl;

  return (
    <div className="flex flex-col gap-2">
      <div className="overflow-hidden rounded-lg border border-border bg-black">
        <video
          ref={videoRef}
          key={currentUrl}
          src={currentUrl}
          controls
          className="w-full"
          aria-label={showOverlay ? "Vídeo con overlay de análisis" : "Vídeo original"}
        />
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => setShowOverlay(true)}
          className={cn(
            "flex-1 rounded-md py-1.5 text-sm font-medium transition-colors",
            showOverlay
              ? "bg-brand-red text-white"
              : "bg-bg-tertiary text-text-secondary hover:bg-bg-hover"
          )}
        >
          Con overlay IA
        </button>
        <button
          onClick={() => setShowOverlay(false)}
          className={cn(
            "flex-1 rounded-md py-1.5 text-sm font-medium transition-colors",
            !showOverlay
              ? "bg-brand-red text-white"
              : "bg-bg-tertiary text-text-secondary hover:bg-bg-hover"
          )}
        >
          Original
        </button>
      </div>
    </div>
  );
};

export default VideoPlayer;
