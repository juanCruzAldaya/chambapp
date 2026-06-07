import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { Button, Card, ErrorMsg, Field, TextInput } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../lib/api";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo ingresar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-6 text-2xl font-bold text-slate-800">Ingresar</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Email">
            <TextInput
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </Field>
          <Field label="Contraseña">
            <TextInput
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>
          <ErrorMsg>{error}</ErrorMsg>
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Ingresando…" : "Ingresar"}
          </Button>
        </form>
      </Card>
      <p className="mt-4 text-center text-sm text-slate-500">
        ¿No tenés cuenta?{" "}
        <Link to="/registro" className="font-semibold text-marca-600">
          Crear una
        </Link>
      </p>
    </div>
  );
}
