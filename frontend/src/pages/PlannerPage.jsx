// smart-study-agent/frontend/src/pages/PlannerPage.jsx
// AI-powered personalised study plan generator.

import React, { useEffect, useState } from "react";
import { docsAPI, plannerAPI } from "../services/api";
import toast from "react-hot-toast";
import { CalendarIcon, PlusIcon, XMarkIcon } from "@heroicons/react/24/outline";

function SessionCard({ session }) {
  const date = new Date(session.date);
  const dayName = date.toLocaleDateString("en-US", { weekday: "short" });
  const dateStr = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });

  return (
    <div className="card p-4 border-l-4 border-primary-400">
      <div className="flex items-center justify-between mb-2">
        <div>
          <span className="font-semibold text-slate-800 text-sm">{dayName}, {dateStr}</span>
          <span className="ml-2 badge bg-primary-100 text-primary-700">{session.duration}h</span>
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {session.topics?.map((t, i) => (
          <span key={i} className="badge bg-slate-100 text-slate-600">{t}</span>
        ))}
      </div>
      {session.resources?.length > 0 && (
        <p className="text-xs text-slate-400">{session.resources.join(" · ")}</p>
      )}
    </div>
  );
}

export default function PlannerPage() {
  const [docs, setDocs]             = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [examDate, setExamDate]     = useState("");
  const [hours, setHours]           = useState(2);
  const [weakInput, setWeakInput]   = useState("");
  const [weakTopics, setWeakTopics] = useState([]);
  const [plan, setPlan]             = useState(null);
  const [loading, setLoading]       = useState(false);

  useEffect(() => {
    docsAPI.list({ per_page: 100 }).then(({ data }) => setDocs(data.items || []));
    // Load existing plan
    plannerAPI.get().then(({ data }) => setPlan(data)).catch(() => {});
  }, []);

  const toggleDoc = (id) =>
    setSelectedDocs((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);

  const addWeakTopic = () => {
    const t = weakInput.trim();
    if (t && !weakTopics.includes(t)) setWeakTopics([...weakTopics, t]);
    setWeakInput("");
  };

  const handleGenerate = async () => {
    if (!examDate) { toast.error("Set your exam date"); return; }
    setLoading(true);
    try {
      const { data } = await plannerAPI.generate({
        document_ids:  selectedDocs,
        exam_date:     examDate,
        hours_per_day: hours,
        weak_topics:   weakTopics,
      });
      setPlan(data);
      toast.success("Study plan generated!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="page-title">Study Planner</h1>
      <p className="page-subtitle">Get a personalised day-by-day study schedule powered by IBM Granite.</p>

      {/* Config form */}
      <div className="card p-6 mb-6">
        <h2 className="font-semibold text-slate-800 mb-4 text-sm">Plan Configuration</h2>

        <div className="grid sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Exam Date</label>
            <input type="date" className="input" value={examDate}
              onChange={(e) => setExamDate(e.target.value)}
              min={new Date().toISOString().split("T")[0]} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Study Hours / Day</label>
            <input type="number" className="input" min={0.5} max={12} step={0.5} value={hours}
              onChange={(e) => setHours(Number(e.target.value))} />
          </div>
        </div>

        {/* Document selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Study Materials</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {docs.map((d) => (
              <label key={d.id} className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer text-xs transition-colors
                ${selectedDocs.includes(d.id) ? "bg-primary-50 border-primary-400" : "bg-white border-slate-200 hover:bg-slate-50"}`}>
                <input type="checkbox" className="text-primary-600 rounded"
                  checked={selectedDocs.includes(d.id)} onChange={() => toggleDoc(d.id)} />
                <span className="truncate text-slate-700">{d.original_name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Weak topics */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">Weak Topics (optional)</label>
          <div className="flex gap-2 mb-2">
            <input type="text" className="input flex-1" placeholder="e.g. Integration, Newton's Laws"
              value={weakInput} onChange={(e) => setWeakInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addWeakTopic()} />
            <button onClick={addWeakTopic} className="btn-secondary px-3">
              <PlusIcon className="w-4 h-4" />
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {weakTopics.map((t) => (
              <span key={t} className="badge bg-orange-100 text-orange-700 flex items-center gap-1">
                {t}
                <button onClick={() => setWeakTopics(weakTopics.filter((x) => x !== t))}>
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        <button onClick={handleGenerate} disabled={loading} className="btn-primary">
          {loading ? <><span className="spinner w-4 h-4" /> Generating Plan…</> : <><CalendarIcon className="w-4 h-4" /> Generate Study Plan</>}
        </button>
      </div>

      {/* Plan sessions */}
      {plan?.sessions?.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-slate-800">
              Study Schedule · {plan.sessions.length} sessions
            </h2>
            <span className="text-xs text-slate-500">Exam: {plan.exam_date}</span>
          </div>
          <div className="space-y-3">
            {plan.sessions.map((s, i) => <SessionCard key={i} session={s} />)}
          </div>
        </div>
      )}
    </div>
  );
}
