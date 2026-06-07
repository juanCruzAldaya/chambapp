# chambapp — Frontend

SPA del marketplace de changas. Consume la API FastAPI (`/api/v1`).

## Stack

- **React 19** + **TypeScript**
- **Vite 6** (dev server + build)
- **Tailwind CSS v4** (plugin de Vite, sin archivo de config)
- **react-router v7** (ruteo + rutas protegidas)
- Cliente HTTP propio tipado con `fetch` (sin dependencias extra), JWT en `localStorage`.

## Cómo correr

```bash
cd frontend
npm install
cp .env.example .env   # opcional; por defecto usa /api/v1 vía proxy de Vite
npm run dev            # http://localhost:5173
```

El backend tiene que estar corriendo en `http://localhost:8000`. En dev, Vite
proxea `/api → :8000` (config en `vite.config.ts`), así que no hay problemas de CORS.

```bash
npm run build       # tsc -b && vite build -> dist/
npm run preview     # sirve el build
npm run typecheck   # solo chequeo de tipos
```

## Estructura

```
src/
  lib/
    api.ts        cliente HTTP tipado (auth, errores, todos los endpoints)
    types.ts      tipos espejo de los schemas Pydantic del backend
    format.ts     helpers (rating, fechas, horas)
  context/
    auth-context.ts   definición del contexto
    AuthContext.tsx   provider (hidrata el usuario, escucha logout por 401)
  hooks/
    useAuth.ts        acceso al contexto
    useCategorias.ts  carga del árbol de categorías
  components/
    Layout, Navbar, ProtectedRoute, ServiceCard, ui (Button/Card/Field/…)
  pages/
    HomePage           búsqueda de servicios con filtros
    ServiceDetailPage  detalle + contratar (elegir turno) + reseñas
    PublishServicePage publicar un servicio
    MyServicesPage     servicios propios
    AgendaPage         calendarios + turnos de disponibilidad
    ContractsPage      contrataciones por rol (cliente / profesional)
    ProfilePage        editar perfil
    Login / Register
  App.tsx        ruteo
  main.tsx       entrypoint (BrowserRouter + AuthProvider)
```

## Flujos cubiertos

- **Auth**: registro + login (OAuth2 password flow), token persistido, rutas
  protegidas, logout automático ante un 401.
- **Cliente**: buscar servicios, ver detalle, contratar eligiendo un turno
  disponible del profesional, dejar reseñas, ver "Contraté".
- **Profesional**: publicar servicios, gestionar agenda (turnos), ver
  "Me contrataron" y cambiar el estado de las contrataciones.
