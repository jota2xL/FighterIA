/**
 * NotFoundPage
 * 404 page with navigation back to dashboard.
 */
import { Link } from "react-router-dom";
import Button from "@/components/ui/Button";

const NotFoundPage = () => (
  <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-bg-primary text-center px-4">
    <span className="font-display text-8xl font-bold text-brand-red">404</span>
    <div>
      <h1 className="font-display text-3xl font-bold text-text-primary">
        Página no encontrada
      </h1>
      <p className="mt-2 text-text-secondary">
        El combate que buscas no existe en este dojo.
      </p>
    </div>
    <Link to="/dashboard">
      <Button size="lg">Volver al dashboard</Button>
    </Link>
  </div>
);

export default NotFoundPage;
