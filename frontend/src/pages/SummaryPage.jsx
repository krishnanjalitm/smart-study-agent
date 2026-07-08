// smart-study-agent/frontend/src/pages/SummaryPage.jsx
// AI-generated document summaries (Short / Medium / Detailed).

import React, { useEffect, useState } from "react";
import { docsAPI, summaryAPI } from "../services/api";
import ReactMarkdown from "react-markdown";
import { LightBulbIcon, DocumentTextIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

const LENGTHS = ["short", "medium", "detailed"];

export default function SummaryPage() {
  const [docs, setDocs]       = useState([]);
  const [docId, setDocId]     = useState("");
  const [length, setLength]   = useState("medium");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    docsAPI.list({ per_page: 100 }).then(({ data }) => setDocs(data.items || []));
  }, []);

  const handleGenerate = async () => {
    if (!docId) { toast.error("Select a document first"); return; }
    setLoading(true);
    setSummary(null);
    try {
      const { data } = await summaryAPI.generate({ document_id: docId, length });
      setSummary(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="page-title">AI Summary</h1>
      <p className="page-subtitle">Generate concise or detailed summaries of your study materials.</p>

      {/* Controls */}
      <div className="card p-5 mb-6">
        <div className="grid sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Document</label>
            <select className="input" value={docId} onChange={(e) => setDocId(e.target.value)}>
              <option value="">Select a document…</option>
              {docs.map((d) => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Summary Length</label>
            <div className="flex gap-2">
              {LENGTHS.map((l) => (
                <button
                  key={l}
                  onClick={() => setLength(l)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-colors capitalize
                    ${length === l
                      ? "bg-primary-600 text-white border-primary-600"
                      : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                    }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
        </div>
        <button onClick={handleGenerate} disabled={loading} className="btn-primary">
          {loading ? <><span className="spinner w-4 h-4" /> Generating…</> : <><LightBulbIcon className="w-4 h-4" /> Generate Summary</>}
        </button>
      </div>

      {/* Summary output */}
      {summary && (
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-4">
            <DocumentTextIcon className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-slate-800 capitalize">{summary.length} Summary</h3>
            <span className="badge bg-primary-100 text-primary-700 ml-auto">IBM Granite</span>
          </div>
          <div className="prose prose-sm max-w-none text-slate-700">
            <ReactMarkdown>{summary.content}</ReactMarkdown>
          </div>
          <p className="text-xs text-slate-400 mt-4 pt-4 border-t border-slate-100">
            Generated at {new Date(summary.created_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}
