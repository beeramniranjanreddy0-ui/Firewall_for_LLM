import { Activity, FileText, LayoutDashboard, Shield, TerminalSquare } from "lucide-react";
import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

type LayoutProps = {
  children: ReactNode;
};

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/prompt-testing", label: "Prompt Testing", icon: TerminalSquare },
  { to: "/logs", label: "Logs", icon: FileText },
  { to: "/security-events", label: "Security Events", icon: Activity },
];

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-firewall-bg text-slate-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-slate-800 bg-slate-950/90 px-5 py-6 backdrop-blur lg:block">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-firewall-primary/15 text-firewall-primary">
            <Shield size={24} aria-hidden />
          </div>
          <div>
            <p className="text-sm uppercase text-slate-500">Adaptive</p>
            <h1 className="text-lg font-semibold text-white">AI Firewall</h1>
          </div>
        </div>
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition ${
                    isActive
                      ? "bg-firewall-primary text-white shadow-glow"
                      : "text-slate-400 hover:bg-slate-900 hover:text-slate-100"
                  }`
                }
              >
                <Icon size={18} aria-hidden />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/85 px-4 py-3 backdrop-blur lg:hidden">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-firewall-primary/15 text-firewall-primary">
              <Shield size={22} aria-hidden />
            </div>
            <div>
              <p className="text-xs uppercase text-slate-500">Adaptive</p>
              <h1 className="text-base font-semibold text-white">AI Firewall</h1>
            </div>
          </div>
          <nav className="grid grid-cols-4 gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    `flex h-11 items-center justify-center rounded-lg text-sm transition ${
                      isActive ? "bg-firewall-primary text-white" : "bg-slate-900 text-slate-400"
                    }`
                  }
                  title={item.label}
                >
                  <Icon size={18} aria-hidden />
                  <span className="sr-only">{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </header>
        <main className="mx-auto min-h-screen w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
