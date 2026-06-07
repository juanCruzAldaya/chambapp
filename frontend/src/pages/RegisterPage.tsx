import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button, Card, ErrorMsg, Field, TextInput } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../lib/api";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres");
      return;
    }
    setLoading(true);
    try {
      await register(email, password, nombre || undefined);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo registrar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-6 text-2xl font-bold text-slate-800">Crear cuenta</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Nombre">
            <TextInput
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Cómo te llamás"
              autoFocus
            />
          </Field>
          <Field label="Email">
            <TextInput
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </Field>
          <Field label="Contraseña" hint="Mínimo 8 caracteres">
            <TextInput
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>
          <ErrorMsg>{error}</ErrorMsg>
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Creando…" : "Crear cuenta"}
          </Button>
        </form>
      </Card>
      <p className="mt-4 text-center text-sm text-slate-500">
        ¿Ya tenés cuenta?{" "}
        <Link to="/login" className="font-semibold text-marca-600">
          Ingresar
        </Link>
      </p>
    </div>
  );
}
