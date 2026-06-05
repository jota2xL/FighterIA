/**
 * LeadPipelinePage
 * Kanban-style pipeline view for CRM leads within a specific gym.
 */
import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmService } from "@/services/crm.service";
import type { Lead, LeadCreate } from "@/types/crm.types";
import Card, { CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import toast from "react-hot-toast";

type LeadStatus = "new" | "contacted" | "converted" | "lost";

const COLUMNS: { status: LeadStatus; label: string; color: string }[] = [
  { status: "new", label: "Nuevos", color: "border-blue-500/40 bg-blue-500/5" },
  { status: "contacted", label: "Contactados", color: "border-yellow-500/40 bg-yellow-500/5" },
  { status: "converted", label: "Convertidos", color: "border-green-500/40 bg-green-500/5" },
  { status: "lost", label: "Perdidos", color: "border-red-500/40 bg-red-500/5" },
];

const STATUS_BADGE: Record<LeadStatus, string> = {
  new: "bg-blue-500/15 text-blue-400",
  contacted: "bg-yellow-500/15 text-yellow-400",
  converted: "bg-green-500/15 text-green-400",
  lost: "bg-red-500/15 text-red-400",
};

const EMPTY_FORM: LeadCreate = {
  name: "",
  email: "",
  phone: "",
  status: "new",
  source: "manual",
  notes: "",
};

const LeadPipelinePage = () => {
  const { gymId } = useParams<{ gymId: string }>();
  const parsedGymId = Number(gymId);
  const queryClient = useQueryClient();

  const [modalOpen, setModalOpen] = React.useState(false);
  const [form, setForm] = React.useState<LeadCreate>(EMPTY_FORM);
  const [formError, setFormError] = React.useState<string | null>(null);

  const {
    data: leads,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["leads", parsedGymId],
    queryFn: () => crmService.getLeads(parsedGymId),
    enabled: !isNaN(parsedGymId),
  });

  const createMutation = useMutation({
    mutationFn: (data: LeadCreate) => crmService.createLead(parsedGymId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads", parsedGymId] });
      setModalOpen(false);
      setForm(EMPTY_FORM);
      toast.success("Lead añadido correctamente");
    },
    onError: () => {
      setFormError("Error al crear el lead. Inténtalo de nuevo.");
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ leadId, status }: { leadId: number; status: string }) =>
      crmService.updateLead(parsedGymId, leadId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads", parsedGymId] });
    },
    onError: () => {
      toast.error("Error al actualizar el estado del lead");
    },
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!form.name.trim() || !form.email.trim()) {
      setFormError("El nombre y el email son obligatorios.");
      return;
    }
    createMutation.mutate(form);
  };

  const handleOpenModal = () => {
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const getLeadsForStatus = (status: LeadStatus): Lead[] =>
    (leads ?? []).filter((l) => l.status === status);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link
            to="/gyms"
            className="text-sm text-text-muted hover:text-text-secondary transition-colors"
          >
            ← Gimnasios
          </Link>
          <h1 className="font-display text-3xl font-bold text-text-primary mt-1">
            Pipeline de Leads
          </h1>
          <p className="text-sm text-text-secondary">Gestiona los leads del gimnasio</p>
        </div>
        <Button onClick={handleOpenModal}>+ Añadir Lead</Button>
      </div>

      {/* Content */}
      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage message="Error cargando leads" onRetry={() => refetch()} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {COLUMNS.map(({ status, label, color }) => {
            const columnLeads = getLeadsForStatus(status);
            return (
              <div
                key={status}
                className={`rounded-lg border p-3 ${color} flex flex-col gap-3`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-text-primary">
                    {label}
                  </span>
                  <span className="rounded-full bg-bg-secondary px-2 py-0.5 text-xs font-medium text-text-muted">
                    {columnLeads.length}
                  </span>
                </div>

                {columnLeads.length === 0 ? (
                  <div className="rounded-md border border-dashed border-border p-4 text-center">
                    <p className="text-xs text-text-muted">Sin leads</p>
                  </div>
                ) : (
                  columnLeads.map((lead) => (
                    <Card key={lead.id} className="flex flex-col gap-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold text-text-primary">
                            {lead.name}
                          </p>
                          <p className="truncate text-xs text-text-muted">
                            {lead.email}
                          </p>
                          {lead.phone && (
                            <p className="truncate text-xs text-text-muted">
                              {lead.phone}
                            </p>
                          )}
                        </div>
                        <span
                          className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[lead.status as LeadStatus] ?? ""}`}
                        >
                          {lead.status}
                        </span>
                      </div>
                      {/* Quick status change */}
                      <select
                        value={lead.status}
                        onChange={(e) =>
                          updateStatusMutation.mutate({
                            leadId: lead.id,
                            status: e.target.value,
                          })
                        }
                        className="w-full rounded border border-border bg-bg-tertiary px-2 py-1 text-xs text-text-secondary focus:outline-none focus:ring-1 focus:ring-brand-red"
                        aria-label={`Cambiar estado de ${lead.name}`}
                      >
                        <option value="new">Nuevo</option>
                        <option value="contacted">Contactado</option>
                        <option value="converted">Convertido</option>
                        <option value="lost">Perdido</option>
                      </select>
                    </Card>
                  ))
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add Lead Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Nuevo Lead"
        size="md"
      >
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Nombre"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Juan García"
            required
          />
          <Input
            label="Email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="juan@example.com"
            required
          />
          <Input
            label="Teléfono"
            name="phone"
            type="tel"
            value={form.phone ?? ""}
            onChange={handleChange}
            placeholder="+34 600 000 000"
          />
          <div className="flex flex-col gap-1">
            <label
              htmlFor="source"
              className="text-sm font-medium text-text-secondary"
            >
              Fuente
            </label>
            <select
              id="source"
              name="source"
              value={form.source ?? "manual"}
              onChange={handleChange}
              className="rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-red focus:ring-offset-1 focus:ring-offset-bg-primary hover:border-border-strong transition-colors"
            >
              <option value="manual">Manual</option>
              <option value="web">Web</option>
              <option value="referral">Referido</option>
              <option value="social">Redes Sociales</option>
              <option value="ads">Publicidad</option>
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label
              htmlFor="notes"
              className="text-sm font-medium text-text-secondary"
            >
              Notas
            </label>
            <textarea
              id="notes"
              name="notes"
              value={form.notes ?? ""}
              onChange={handleChange}
              rows={3}
              placeholder="Observaciones sobre el lead..."
              className="rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-brand-red focus:ring-offset-1 focus:ring-offset-bg-primary hover:border-border-strong transition-colors resize-none"
            />
          </div>

          {formError && (
            <p className="text-xs text-brand-red-light">{formError}</p>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="secondary"
              type="button"
              onClick={() => setModalOpen(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" isLoading={createMutation.isPending}>
              Añadir Lead
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default LeadPipelinePage;
