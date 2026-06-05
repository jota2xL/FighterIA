/**
 * GymManagementPage
 * Lists all gyms and allows creating new ones via a modal form.
 */
import React from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmService } from "@/services/crm.service";
import type { GymCreate } from "@/types/crm.types";
import Card, { CardHeader } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import toast from "react-hot-toast";

const EMPTY_FORM: GymCreate = { name: "", city: "", country: "", plan: "basic" };

const GymManagementPage = () => {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = React.useState(false);
  const [form, setForm] = React.useState<GymCreate>(EMPTY_FORM);
  const [formError, setFormError] = React.useState<string | null>(null);

  const {
    data: gyms,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["gyms"],
    queryFn: crmService.getGyms,
  });

  const createMutation = useMutation({
    mutationFn: (data: GymCreate) => crmService.createGym(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gyms"] });
      setModalOpen(false);
      setForm(EMPTY_FORM);
      toast.success("Gimnasio creado correctamente");
    },
    onError: () => {
      setFormError("Error al crear el gimnasio. Inténtalo de nuevo.");
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!form.name.trim() || !form.city.trim()) {
      setFormError("El nombre y la ciudad son obligatorios.");
      return;
    }
    createMutation.mutate(form);
  };

  const handleOpenModal = () => {
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-primary">
            Gimnasios
          </h1>
          <p className="text-sm text-text-secondary">
            Gestiona los gimnasios registrados en la plataforma
          </p>
        </div>
        <Button onClick={handleOpenModal}>+ Nuevo Gimnasio</Button>
      </div>

      {/* Content */}
      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage message="Error cargando gimnasios" onRetry={() => refetch()} />
      ) : gyms && gyms.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {gyms.map((gym) => (
            <Card key={gym.id} hoverable>
              <CardHeader
                title={gym.name}
                subtitle={`${gym.city}${gym.country ? `, ${gym.country}` : ""}`}
                action={
                  <span className="rounded-full bg-brand-red/10 px-2 py-0.5 text-xs font-medium text-brand-red uppercase">
                    {gym.plan}
                  </span>
                }
              />
              <div className="mt-3 flex gap-2">
                <Link to={`/gyms/${gym.id}/dashboard`} className="flex-1">
                  <Button variant="secondary" size="sm" className="w-full">
                    Dashboard
                  </Button>
                </Link>
                <Link to={`/gyms/${gym.id}/leads`} className="flex-1">
                  <Button variant="primary" size="sm" className="w-full">
                    Leads
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-dashed border-border p-12 text-center">
          <p className="text-text-muted">No hay gimnasios registrados todavía.</p>
          <Button className="mt-4" onClick={handleOpenModal}>
            Crear el primero
          </Button>
        </div>
      )}

      {/* Create Gym Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Nuevo Gimnasio"
        size="md"
      >
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Nombre del gimnasio"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="CrossFit Madrid Centro"
            required
          />
          <Input
            label="Ciudad"
            name="city"
            value={form.city}
            onChange={handleChange}
            placeholder="Madrid"
            required
          />
          <Input
            label="País"
            name="country"
            value={form.country ?? ""}
            onChange={handleChange}
            placeholder="España"
          />
          <div className="flex flex-col gap-1">
            <label
              htmlFor="plan"
              className="text-sm font-medium text-text-secondary"
            >
              Plan
            </label>
            <select
              id="plan"
              name="plan"
              value={form.plan ?? "basic"}
              onChange={handleChange}
              className="rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-brand-red focus:ring-offset-1 focus:ring-offset-bg-primary hover:border-border-strong transition-colors"
            >
              <option value="basic">Basic</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
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
              Crear Gimnasio
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default GymManagementPage;
