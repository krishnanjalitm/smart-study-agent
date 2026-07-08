// smart-study-agent/frontend/src/components/Layout.jsx
// Persistent sidebar + topbar shell for authenticated pages.

import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  HomeIcon, DocumentTextIcon, LightBulbIcon, BookOpenIcon,
  AcademicCapIcon, CalendarIcon, ChartBarIcon, ChatBubbleLeftRightIcon,
  Bars3Icon, XMarkIcon, ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";

const nav = [
  { label: "Dashboard",  to: "/",           icon: HomeIcon },
  { label: "Documents",  to: "/documents",  icon: DocumentTextIcon },
  { label: "AI Chat",    to: "/chat",        icon: ChatBubbleLeftRightIcon },
  { label: "Summary",    to: "/summary",    icon: LightBulbIcon },
  { label: "Flashcards", to: "/flashcards", icon: BookOpenIcon },
  { label: "Quiz",       to: "/quiz",       icon: AcademicCapIcon },
  { label: "Planner",    to: "/planner",    icon: CalendarIcon },
  { label: "Progress",   to: "/progress",   icon: ChartBarIcon },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate         = useNavigate();
  const [open, setOpen]  = useState(false);

  const handleLogout = () => { logout(); navigate("/login"); };

  const Sidebar = () => (
    <nav className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-200">
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
          <AcademicCapIcon className="w-5 h-5 text-white" />
        </div>
        <span className="font-bold text-slate-900 text-base">StudyAgent</span>
      </div>

      {/* Nav items */}
      <ul className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {nav.map(({ label, to, icon: Icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={to === "/"}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                 ${isActive
                   ? "bg-primary-50 text-primary-700 border border-primary-200"
                   : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                 }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {label}
            </NavLink>
          </li>
        ))}
      </ul>

      {/* User + Logout */}
      <div className="border-t border-slate-200 px-4 py-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-xs font-bold">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 truncate">{user?.name}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button onClick={handleLogout} className="btn-secondary w-full justify-center text-xs">
          <ArrowRightOnRectangleIcon className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </nav>
  );

  return (
    <div className="flex h-screen bg-surface overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-60 bg-white border-r border-slate-200 flex-shrink-0">
        <Sidebar />
      </aside>

      {/* Mobile overlay sidebar */}
      {open && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <div className="w-60 bg-white border-r border-slate-200 flex flex-col z-50">
            <Sidebar />
          </div>
          <div className="flex-1 bg-black/40" onClick={() => setOpen(false)} />
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="flex items-center gap-4 px-5 py-3 bg-white border-b border-slate-200 flex-shrink-0">
          <button className="md:hidden text-slate-600" onClick={() => setOpen(true)}>
            {open ? <XMarkIcon className="w-6 h-6" /> : <Bars3Icon className="w-6 h-6" />}
          </button>
          <h1 className="font-semibold text-slate-800 text-base">Smart Study Generator</h1>
          <span className="ml-auto text-xs text-slate-500 bg-primary-50 text-primary-700 px-2 py-1 rounded-full font-medium">
            IBM watsonx.ai
          </span>
        </header>

        {/* Page outlet */}
        <main className="flex-1 overflow-y-auto p-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
