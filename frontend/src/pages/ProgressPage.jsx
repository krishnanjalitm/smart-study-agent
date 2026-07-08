// smart-study-agent/frontend/src/pages/ProgressPage.jsx
// Learning analytics dashboard with charts.

import React, { useEffect, useState } from "react";
import { progressAPI } from "../services/api";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadialBarChart, RadialBar, PieChart, Pie, Cell,
} from "recharts";
import { FireIcon, AcademicCapIcon, BookOpenIcon, ClockIcon, LightBulbIcon } from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";

function StatBox({ icon: Icon, label, value, color }) {
  return (
    <div className="card p-4 flex items-center gap-3">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-xl font-bold text-slate-900">{value}</p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </div>
  );
}

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b"];

export default function ProgressPage() {
  const [data, setData]   = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    progressAPI.dashboard()
      .then(({ data: d }) => setData(d))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="spinner w-10 h-10" />
    </div>
  );

  if (!data) return <p className="text-slate-500">Could not load progress data.</p>;

  const radial = [
    { name: "Quiz Score", value: data.avg_quiz_score, fill: "#3b82f6" },
  ];

  const pieData = [
    { name: "Documents",    value: data.total_documents   || 1 },
    { name: "Flashcards",   value: data.total_flashcards  || 1 },
    { name: "Study Hours",  value: data.total_study_hours || 1 },
    { name: "Streak Days",  value: data.study_streak      || 1 },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="page-title">Progress Dashboard</h1>
        <p className="page-subtitle">Track your learning analytics and stay motivated.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBox icon={AcademicCapIcon} label="Avg Quiz Score"   value={`${data.avg_quiz_score}%`}  color="bg-primary-600" />
        <StatBox icon={BookOpenIcon}    label="Flashcards"       value={data.total_flashcards}       color="bg-secondary-500" />
        <StatBox icon={ClockIcon}       label="Study Hours"      value={`${data.total_study_hours}h`} color="bg-emerald-500" />
        <StatBox icon={FireIcon}        label="Day Streak"       value={`${data.study_streak}d`}     color="bg-orange-500" />
      </div>

      {/* Charts row */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Quiz score trend */}
        <div className="card p-5">
          <h3 className="font-semibold text-slate-700 text-sm mb-4">Quiz Score Trend</h3>
          {data.quiz_trend?.length > 1 ? (
            <ResponsiveContainer width="100%" height={160}>
              <AreaChart data={data.quiz_trend}>
                <defs>
                  <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v) => `${v}%`} />
                <Area type="monotone" dataKey="score" stroke="#3b82f6" fill="url(#cg)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-40 text-slate-400 text-sm">
              Take more quizzes to see trend data.
            </div>
          )}
        </div>

        {/* Activity breakdown */}
        <div className="card p-5">
          <h3 className="font-semibold text-slate-700 text-sm mb-4">Activity Breakdown</h3>
          <div className="flex items-center justify-center h-40">
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3} dataKey="value">
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-1 mt-1">
            {pieData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[i] }} />
                <span className="text-xs text-slate-500">{d.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Insights */}
      {data.ai_insights && (
        <div className="card p-5 border-l-4 border-primary-400">
          <div className="flex items-center gap-2 mb-3">
            <LightBulbIcon className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-slate-800">AI Coach Insights</h3>
            <span className="badge bg-primary-100 text-primary-700 ml-auto">IBM Granite</span>
          </div>
          <div className="prose prose-sm max-w-none text-slate-700">
            <ReactMarkdown>{data.ai_insights}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
