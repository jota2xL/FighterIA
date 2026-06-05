/**
 * ProfilePage
 * User profile display and edit form with avatar upload.
 */
import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { getBeltLabel, formatXP } from "@/utils/format";
import toast from "react-hot-toast";

const schema = z.object({
  full_name: z.string().min(2, "Mínimo 2 caracteres"),
  bio: z.string().max(300, "Máximo 300 caracteres").optional(),
  gym: z.string().max(100).optional(),
  city: z.string().max(100).optional(),
  country: z.string().max(100).optional(),
});

type FormData = z.infer<typeof schema>;

const ProfilePage = () => {
  const { user, setUser } = useAuthStore();
  const queryClient = useQueryClient();
  const fileRef = React.useRef<HTMLInputElement>(null);
  const [previewAvatar, setPreviewAvatar] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: user?.full_name ?? "",
      bio: user?.bio ?? "",
      gym: user?.gym ?? "",
      city: user?.city ?? "",
      country: user?.country ?? "",
    },
  });

  const mutation = useMutation({
    mutationFn: (formData: FormData) => {
      const fd = new FormData();
      Object.entries(formData).forEach(([k, v]) => {
        if (v !== undefined) fd.append(k, v);
      });
      if (fileRef.current?.files?.[0]) {
        fd.append("avatar", fileRef.current.files[0]);
      }
      return authService.updateProfile(fd);
    },
    onSuccess: (data) => {
      setUser(data);
      queryClient.invalidateQueries({ queryKey: ["me"] });
      toast.success("Perfil actualizado");
    },
    onError: () => toast.error("Error al actualizar el perfil"),
  });

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewAvatar(url);
    }
  };

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 font-display text-3xl font-bold text-text-primary">
        Mi perfil
      </h1>

      <div className="rounded-xl border border-border bg-bg-secondary p-6">
        {/* Avatar */}
        <div className="mb-6 flex items-center gap-4">
          <div className="relative">
            {previewAvatar || user.avatar_url ? (
              <img
                src={previewAvatar ?? user.avatar_url!}
                alt={user.username}
                className="h-20 w-20 rounded-full object-cover border-2 border-border"
              />
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-brand-red text-2xl font-bold text-white">
                {user.username[0].toUpperCase()}
              </div>
            )}
            <button
              onClick={() => fileRef.current?.click()}
              className="absolute -bottom-1 -right-1 rounded-full border border-border bg-bg-tertiary p-1.5 text-text-muted hover:text-text-primary transition-colors"
              aria-label="Cambiar avatar"
            >
              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleAvatarChange}
            />
          </div>
          <div>
            <p className="font-display text-xl font-bold text-text-primary">
              @{user.username}
            </p>
            <p className="text-sm text-text-secondary">{user.email}</p>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-xs text-brand-gold font-semibold">
                {formatXP(user.xp)} XP
              </span>
              <span className="text-xs text-text-muted">·</span>
              <span className="text-xs text-text-muted capitalize">
                Cinturón {getBeltLabel(user.belt_level)}
              </span>
            </div>
          </div>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit((d) => mutation.mutate(d))}
          className="flex flex-col gap-4"
        >
          <Input
            label="Nombre completo"
            error={errors.full_name?.message}
            {...register("full_name")}
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-text-secondary">Bio</label>
            <textarea
              {...register("bio")}
              rows={3}
              className="resize-none rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-brand-red"
              placeholder="Cuéntanos sobre ti..."
            />
            {errors.bio && (
              <p className="text-xs text-brand-red-light">{errors.bio.message}</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Gimnasio"
              error={errors.gym?.message}
              {...register("gym")}
            />
            <Input
              label="Ciudad"
              error={errors.city?.message}
              {...register("city")}
            />
          </div>
          <Input
            label="País"
            error={errors.country?.message}
            {...register("country")}
          />

          <Button
            type="submit"
            isLoading={mutation.isPending}
            disabled={!isDirty && !previewAvatar}
            className="mt-2 self-end"
          >
            Guardar cambios
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
