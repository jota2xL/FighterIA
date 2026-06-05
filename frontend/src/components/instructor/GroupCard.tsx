/**
 * GroupCard
 * Displays an instructor group with invite code and navigation to detail.
 */
import { useNavigate } from "react-router-dom";
import type { InstructorGroup } from "@/types/instructor.types";
import Button from "@/components/ui/Button";
import toast from "react-hot-toast";

interface GroupCardProps {
  group: InstructorGroup;
}

const GroupCard = ({ group }: GroupCardProps) => {
  const navigate = useNavigate();

  const copyCode = () => {
    navigator.clipboard.writeText(group.invite_code);
    toast.success("Código copiado al portapapeles");
  };

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-bg-secondary p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-display text-lg font-semibold text-text-primary">
            {group.name}
          </h3>
          {group.description && (
            <p className="mt-0.5 text-sm text-text-muted">{group.description}</p>
          )}
        </div>
        <span className="text-xs text-text-muted">
          {group.student_count} alumno{group.student_count !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="flex items-center gap-2 rounded-md bg-bg-tertiary px-3 py-2">
        <span className="text-xs text-text-muted">Código:</span>
        <code className="flex-1 text-sm font-mono text-brand-gold">
          {group.invite_code}
        </code>
        <button
          onClick={copyCode}
          className="rounded p-1 text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors"
          aria-label="Copiar código"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
      </div>

      <Button
        size="sm"
        variant="secondary"
        onClick={() => navigate(`/instructor/groups/${group.id}`)}
        className="w-full"
      >
        Ver grupo
      </Button>
    </div>
  );
};

export default GroupCard;
