/**
 * InstructorPanelPage
 * Instructor dashboard: list of groups and option for students to join a group.
 */
import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { instructorService } from "@/services/instructor.service";
import { useAuthStore } from "@/store/auth.store";
import GroupCard from "@/components/instructor/GroupCard";
import Modal from "@/components/ui/Modal";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import EmptyState from "@/components/ui/EmptyState";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";

const createSchema = z.object({
  name: z.string().min(2, "Mínimo 2 caracteres").max(80),
  description: z.string().max(200).optional(),
});

const joinSchema = z.object({
  invite_code: z.string().min(4, "Introduce el código de invitación"),
});

type CreateForm = z.infer<typeof createSchema>;
type JoinForm = z.infer<typeof joinSchema>;

const InstructorPanelPage = () => {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [createOpen, setCreateOpen] = React.useState(false);
  const [joinOpen, setJoinOpen] = React.useState(false);

  const { data: groups, isLoading, isError, refetch } = useQuery({
    queryKey: ["instructor-groups"],
    queryFn: instructorService.getGroups,
    enabled: user?.account_type === "instructor",
  });

  const createForm = useForm<CreateForm>({ resolver: zodResolver(createSchema) });
  const joinForm = useForm<JoinForm>({ resolver: zodResolver(joinSchema) });

  const createMutation = useMutation({
    mutationFn: (data: CreateForm) => instructorService.createGroup(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["instructor-groups"] });
      setCreateOpen(false);
      createForm.reset();
      toast.success("Grupo creado");
    },
    onError: () => toast.error("Error al crear el grupo"),
  });

  const joinMutation = useMutation({
    mutationFn: (data: JoinForm) => instructorService.joinGroup(data.invite_code),
    onSuccess: () => {
      setJoinOpen(false);
      joinForm.reset();
      toast.success("Te has unido al grupo");
    },
    onError: () => toast.error("Código inválido o expirado"),
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl font-bold text-text-primary">
          Panel Instructor
        </h1>
        {user?.account_type === "instructor" ? (
          <Button onClick={() => setCreateOpen(true)}>Crear grupo</Button>
        ) : (
          <Button variant="secondary" onClick={() => setJoinOpen(true)}>
            Unirse a un grupo
          </Button>
        )}
      </div>

      {user?.account_type === "alumno" && (
        <div className="rounded-lg border border-brand-gold/20 bg-brand-gold/5 p-4">
          <p className="text-sm text-text-secondary">
            Eres alumno. Puedes unirte a grupos usando el código que te proporcione tu instructor.
          </p>
        </div>
      )}

      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage message="Error cargando grupos" onRetry={() => refetch()} />
      ) : !groups || groups.length === 0 ? (
        <EmptyState
          message="Sin grupos creados"
          description="Crea tu primer grupo para invitar alumnos."
          actionLabel="Crear grupo"
          onAction={() => setCreateOpen(true)}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {groups.map((g) => (
            <GroupCard key={g.id} group={g} />
          ))}
        </div>
      )}

      {/* Create group modal */}
      <Modal isOpen={createOpen} onClose={() => setCreateOpen(false)} title="Crear grupo">
        <form
          onSubmit={createForm.handleSubmit((d) => createMutation.mutate(d))}
          className="flex flex-col gap-4"
        >
          <Input
            label="Nombre del grupo"
            error={createForm.formState.errors.name?.message}
            {...createForm.register("name")}
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-text-secondary">
              Descripción (opcional)
            </label>
            <textarea
              {...createForm.register("description")}
              rows={2}
              className="resize-none rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-brand-red"
            />
          </div>
          <Button
            type="submit"
            isLoading={createMutation.isPending}
            className="self-end"
          >
            Crear grupo
          </Button>
        </form>
      </Modal>

      {/* Join group modal */}
      <Modal isOpen={joinOpen} onClose={() => setJoinOpen(false)} title="Unirse a un grupo">
        <form
          onSubmit={joinForm.handleSubmit((d) => joinMutation.mutate(d))}
          className="flex flex-col gap-4"
        >
          <Input
            label="Código de invitación"
            placeholder="Introduce el código..."
            error={joinForm.formState.errors.invite_code?.message}
            {...joinForm.register("invite_code")}
          />
          <Button
            type="submit"
            isLoading={joinMutation.isPending}
            className="self-end"
          >
            Unirse
          </Button>
        </form>
      </Modal>
    </div>
  );
};

export default InstructorPanelPage;
