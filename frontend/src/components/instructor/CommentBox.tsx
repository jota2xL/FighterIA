/**
 * CommentBox
 * Instructor comment form for leaving feedback on a student's progress.
 */
import React from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { instructorService } from "@/services/instructor.service";
import type { CommentCreate } from "@/types/instructor.types";
import Button from "@/components/ui/Button";
import toast from "react-hot-toast";

interface CommentBoxProps {
  studentId: number;
  analysisId?: number;
}

const CommentBox = ({ studentId, analysisId }: CommentBoxProps) => {
  const [content, setContent] = React.useState("");
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: CommentCreate) => instructorService.addComment(data),
    onSuccess: () => {
      setContent("");
      toast.success("Comentario enviado");
      queryClient.invalidateQueries({ queryKey: ["student", studentId] });
    },
    onError: () => toast.error("Error al enviar el comentario"),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    mutation.mutate({ content: content.trim(), student_id: studentId, analysis_id: analysisId });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Escribe un comentario para el alumno..."
        rows={3}
        className="w-full resize-none rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-brand-red"
      />
      <Button
        type="submit"
        size="sm"
        isLoading={mutation.isPending}
        disabled={!content.trim()}
        className="self-end"
      >
        Enviar comentario
      </Button>
    </form>
  );
};

export default CommentBox;
