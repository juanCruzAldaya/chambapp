import { Outlet } from "react-router-dom";

import { Navbar } from "./Navbar";

export function Layout() {
  return (
    <div className="flex min-h-full flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-400">
        chambapp · marketplace de changas · reconstrucción cloud-native
      </footer>
    </div>
  );
}
