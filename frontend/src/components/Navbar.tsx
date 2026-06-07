import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { Button } from "./ui";

function navClass({ isActive }: { isActive: boolean }): string {
  return `rounded-lg px-3 py-2 text-sm font-medium transition ${
    isActive ? "bg-marca-50 text-marca-700" : "text-slate-600 hover:bg-slate-100"
  }`;
}

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-5xl items-center gap-2 px-4 py-3">
        <Link to="/" className="mr-2 text-xl font-extrabold text-marca-600">
          chamb<span className="text-slate-800">app</span>
        </Link>

        <NavLink to="/" className={navClass} end>
          Buscar
        </NavLink>

        {user && (
          <>
            <NavLink to="/publicar" className={navClass}>
              Publicar
            </NavLink>
            <NavLink to="/mis-servicios" className={navClass}>
              Mis servicios
            </NavLink>
            <NavLink to="/agenda" className={navClass}>
              Agenda
            </NavLink>
            <NavLink to="/contrataciones" className={navClass}>
              Contrataciones
            </NavLink>
          </>
        )}

        <div className="ml-auto flex items-center gap-2">
          {user ? (
            <>
              <Link
                to="/perfil"
                className="text-sm font-medium text-slate-600 hover:text-marca-600"
              >
                {user.nombre || user.email}
              </Link>
              <Button variant="secondary" onClick={handleLogout}>
                Salir
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost">Ingresar</Button>
              </Link>
              <Link to="/registro">
                <Button>Crear cuenta</Button>
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
