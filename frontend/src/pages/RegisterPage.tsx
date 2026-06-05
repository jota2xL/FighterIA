/**
 * RegisterPage
 * New account creation form with validation and account type selection.
 */
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/hooks/useAuth";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { cn } from "@/utils/cn";

const schema = z
  .object({
    email: z.string().email("Email inválido"),
    username: z
      .string()
      .min(3, "Mínimo 3 caracteres")
      .max(30, "Máximo 30 caracteres")
      .regex(/^[a-zA-Z0-9_]+$/, "Solo letras, números y _"),
    full_name: z.string().min(2, "Introduce tu nombre completo"),
    password: z.string().min(8, "Mínimo 8 caracteres"),
    confirm_password: z.string(),
    account_type: z.enum(["alumno", "instructor"]),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: "Las contraseñas no coinciden",
    path: ["confirm_password"],
  });

type FormData = z.infer<typeof schema>;

const RegisterPage = () => {
  const { registerMutation } = useAuth();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { account_type: "alumno" },
  });

  const accountType = watch("account_type");

  const onSubmit = ({ confirm_password: _, ...data }: FormData) =>
    registerMutation.mutate(data);

  return (
    <div className="rounded-xl border border-border bg-bg-secondary p-8">
      <h2 className="mb-1 font-display text-2xl font-bold text-text-primary">
        Crear cuenta
      </h2>
      <p className="mb-6 text-sm text-text-secondary">
        Únete a FighterIA y empieza a entrenar.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
        <Input
          label="Nombre completo"
          autoComplete="name"
          error={errors.full_name?.message}
          {...register("full_name")}
        />
        <Input
          label="Nombre de usuario"
          autoComplete="username"
          error={errors.username?.message}
          hint="Solo letras, números y _"
          {...register("username")}
        />
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Input
          label="Contraseña"
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Input
          label="Confirmar contraseña"
          type="password"
          autoComplete="new-password"
          error={errors.confirm_password?.message}
          {...register("confirm_password")}
        />

        {/* Account type */}
        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-text-secondary">
            Tipo de cuenta
          </span>
          <div className="grid grid-cols-2 gap-2">
            {(["alumno", "instructor"] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setValue("account_type", type)}
                className={cn(
                  "rounded-md border py-3 text-sm font-medium capitalize transition-colors",
                  accountType === type
                    ? "border-brand-red bg-brand-red/10 text-text-primary"
                    : "border-border bg-bg-tertiary text-text-secondary hover:bg-bg-hover"
                )}
              >
                {type === "alumno" ? "🥋 Alumno" : "👨‍🏫 Instructor"}
              </button>
            ))}
          </div>
          {errors.account_type && (
            <p className="text-xs text-brand-red-light">
              {errors.account_type.message}
            </p>
          )}
        </div>

        {registerMutation.isError && (
          <p className="rounded-md bg-brand-red/10 px-3 py-2 text-sm text-brand-red-light">
            Error al crear la cuenta. Puede que el email o username ya existan.
          </p>
        )}

        <Button
          type="submit"
          size="lg"
          className="mt-2 w-full"
          isLoading={registerMutation.isPending}
        >
          Crear cuenta
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-text-muted">
        ¿Ya tienes cuenta?{" "}
        <Link to="/login" className="font-medium text-brand-red hover:text-brand-red-light">
          Inicia sesión
        </Link>
      </p>
    </div>
  );
};

export default RegisterPage;
