// smart-study-agent/frontend/src/pages/DashboardPage.jsx
// Quick-stats overview for the logged-in student.

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { progressAPI, docsAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  DocumentTextIcon, AcademicCapIcon, BookOpenIcon, ClockIcon,
  FireIcon, ChatBubbleLeftRightIcon, ArrowRightIcon, LightBulbIcon,
} from "@heroicons/react/24/outline";

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-sm text-slate-500">{label}</p>
      </div>
    </div>
  );
}

function QuickAction({ to, icon: Icon, label, desc, color }) {
  return (
    <Link to={to} className="card p-4 hover:shadow-md transition-shadow group">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <p className="font-semibold text-slate-800 text-sm group-hover:text-primary-600">{label}</p>
      <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
      <ArrowRightIcon className="w-4 h-4 text-slate-400 mt-2 group-hover:translate-x-1 transition-transform" />
    </Link>
  );
}

export default function DashboardPage() {
  const { user }          = useAuth();
  const [stats, setStats] = useState(null);
  const [docs, setDocs]   = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([progressAPI.dashboard(), docsAPI.list({ per_page: 5 })])
      .then(([{ data: s }, { data: d }]) => {
        setStats(s);
        setDocs(d.items || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto">
      {/* Greeting */}
      <div className="mb-6">
        <h1 className="page-title">Welcome back, {user?.name?.split(" ")[0]}! 👋</h1>
        <p className="page-subtitle">Here's an overview of your study progress.</p>
      </div>

      {/* Stats grid */}
      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="spinner w-8 h-8" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard icon={DocumentTextIcon} label="Documents"       value={stats?.total_documents   ?? 0} color="bg-primary-600" />
            <StatCard icon={AcademicCapIcon}  label="Avg Quiz Score"  value={`${stats?.avg_quiz_score ?? 0}%`} color="bg-secondary-500" />
            <StatCard icon={BookOpenIcon}     label="Flashcards"      value={stats?.total_flashcards  ?? 0} color="bg-emerald-500" />
            <StatCard icon={FireIcon}         label="Study Streak"    value={`${stats?.study_streak   ?? 0}d`} color="bg-orange-500" />
          </div>

          {/* AI Insights */}
          {stats?.ai_insights && (
            <div className="card p-5 mb-8 border-l-4 border-primary-400">
              <div className="flex items-center gap-2 mb-2">
                <LightBulbIcon className="w-5 h-5 text-primary-600" />
                <h3 className="font-semibold text-slate-800">AI Insights</h3>
                <span className="badge bg-primary-100 text-primary-700">IBM Granite</span>
              </div>
              <p className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{stats.ai_insights}</p>
            </div>
          )}
        </>
      )}

      {/* Quick actions */}
      <h2 className="text-base font-semibold text-slate-700 mb-3">Quick Actions</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <QuickAction to="/documents"  icon={DocumentTextIcon}         label="Upload Notes"     desc="Add PDF, DOCX, TXT"      color="bg-primary-600" />
        <QuickAction to="/chat"       icon={ChatBubbleLeftRightIcon}  label="AI Chat"          desc="Ask your materials"       color="bg-secondary-500" />
        <QuickAction to="/quiz"       icon={AcademicCapIcon}          label="Take Quiz"        desc="Test your knowledge"      color="bg-emerald-500" />
        <QuickAction to="/planner"    icon={ClockIcon}                label="Study Planner"    desc="Plan for your exam"       color="bg-orange-500" />
      </div>

      {/* Recent documents */}
      <h2 className="text-base font-semibold text-slate-700 mb-3">Recent Documents</h2>
      {docs.length === 0 ? (
        <div className="card p-8 text-center text-slate-400">
          <DocumentTextIcon className="w-10 h-10 mx-auto mb-2" />
          <p className="text-sm">No documents yet. <Link to="/documents" className="text-primary-600 underline">Upload your first file.</Link></p>
        </div>
      ) : (
        <div className="card divide-y divide-slate-100">
          {docs.map((d) => (
            <div key={d.id} className="flex items-center gap-3 px-4 py-3">
              <DocumentTextIcon className="w-5 h-5 text-slate-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">{d.original_name}</p>
                <p className="text-xs text-slate-400">{d.word_count?.toLocaleString()} words · {d.file_type?.toUpperCase()}</p>
              </div>
              <span className={`badge ${d.status === "ready" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                {d.status}
              </span>
            </div>
          ))}
          <div className="px-4 py-2.5">
            <Link to="/documents" className="text-xs text-primary-600 hover:underline">View all documents →</Link>
          </div>
        </div>
      )}
    </div>
  );
}
