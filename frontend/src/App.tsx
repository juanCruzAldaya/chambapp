import { Link, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Button } from "./components/ui";
import { AgendaPage } from "./pages/AgendaPage";
import { ContractsPage } from "./pages/ContractsPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { MyServicesPage } from "./pages/MyServicesPage";
import { ProfilePage } from "./pages/ProfilePage";
import { PublishServicePage } from "./pages/PublishServicePage";
import { RegisterPage } from "./pages/RegisterPage";
import { ServiceDetailPage } from "./pages/ServiceDetailPage";

function NotFound() {
  return (
    <div className="py-20 text-center">
      <h1 className="text-3xl font-bold text-slate-800">404</h1>
      <p className="mt-2 text-slate-500">Esta página no existe.</p>
      <Link to="/" className="mt-4 inline-block">
        <Button>Volver al inicio</Button>
      </Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Públicas */}
        <Route path="/" element={<HomePage />} />
        <Route path="/servicios/:id" element={<ServiceDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />

        {/* Protegidas */}
        <Route element={<ProtectedRoute />}>
          <Route path="/publicar" element={<PublishServicePage />} />
          <Route path="/mis-servicios" element={<MyServicesPage />} />
          <Route path="/agenda" element={<AgendaPage />} />
          <Route path="/contrataciones" element={<ContractsPage />} />
          <Route path="/perfil" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
