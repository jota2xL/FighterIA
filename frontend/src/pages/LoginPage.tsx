/**
 * LoginPage
 * Authentication form with email/password and links to register and forgot password.
 */
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/hooks/useAuth";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "La contraseña es requerida"),
});

type FormData = z.infer<typeof schema>;

const LoginPage = () => {
  const { loginMutation } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = (data: FormData) => loginMutation.mutate(data);

  return (
    <div className="rounded-xl border border-border bg-bg-secondary p-8">
      <h2 className="mb-1 font-display text-2xl font-bold text-text-primary">
        Iniciar sesión
      </h2>
      <p className="mb-6 text-sm text-text-secondary">
        Bienvenido de vuelta, guerrero.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
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
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />

        <div className="text-right">
          <button
            type="button"
            className="text-xs text-text-muted hover:text-text-secondary transition-colors"
          >
            ¿Olvidaste tu contraseña?
          </button>
        </div>

        {loginMutation.isError && (
          <p className="rounded-md bg-brand-red/10 px-3 py-2 text-sm text-brand-red-light">
            Email o contraseña incorrectos.
          </p>
        )}

        <Button
          type="submit"
          size="lg"
          className="mt-2 w-full"
          isLoading={loginMutation.isPending}
        >
          Entrar al dojo
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-text-muted">
        ¿No tienes cuenta?{" "}
        <Link to="/register" className="font-medium text-brand-red hover:text-brand-red-light">
          Regístrate gratis
        </Link>
      </p>
    </div>
  );
};

export default LoginPage;
