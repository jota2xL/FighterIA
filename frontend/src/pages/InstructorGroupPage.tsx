/**
 * InstructorGroupPage
 * Detail view of an instructor group with students table.
 */
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { instructorService } from "@/services/instructor.service";
import StudentRow from "@/components/instructor/StudentRow";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import EmptyState from "@/components/ui/EmptyState";

const InstructorGroupPage = () => {
  const { groupId } = useParams<{ groupId: string }>();
  const id = Number(groupId);

  const { data: groups } = useQuery({
    queryKey: ["instructor-groups"],
    queryFn: instructorService.getGroups,
  });

  const { data: students, isLoading, isError, refetch } = useQuery({
    queryKey: ["group-students", id],
    queryFn: () => instructorService.getGroupStudents(id),
    enabled: !!id,
  });

  const group = groups?.find((g) => g.id === id);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link
          to="/instructor"
          className="text-sm text-text-muted hover:text-text-secondary transition-colors"
        >
          ← Panel Instructor
        </Link>
        <h1 className="mt-1 font-display text-3xl font-bold text-text-primary">
          {group?.name ?? "Grupo"}
        </h1>
        {group && (
          <p className="text-sm text-text-muted">
            {students?.length ?? 0} alumno{students?.length !== 1 ? "s" : ""}
          </p>
        )}
      </div>

      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage message="Error cargando alumnos" onRetry={() => refetch()} />
      ) : !students || students.length === 0 ? (
        <EmptyState
          message="Sin alumnos en este grupo"
          description="Comparte el código de invitación para que los alumnos se unan."
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-bg-tertiary">
                <th className="px-4 py-3 text-left font-semibold text-text-secondary">Alumno</th>
                <th className="px-4 py-3 text-left font-semibold text-text-secondary">Cinturón</th>
                <th className="px-4 py-3 text-right font-semibold text-text-secondary">Media</th>
                <th className="px-4 py-3 text-center font-semibold text-text-secondary">Análisis</th>
                <th className="px-4 py-3 text-right font-semibold text-text-secondary hidden md:table-cell">
                  Último
                </th>
                <th className="px-4 py-3 text-right font-semibold text-text-secondary">Racha</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <StudentRow key={s.id} student={s} groupId={id} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default InstructorGroupPage;
