// smart-study-agent/frontend/src/pages/QuizPage.jsx
// AI-generated quiz with MCQ, True/False, and Short Answer support.

import React, { useEffect, useState } from "react";
import { docsAPI, quizAPI } from "../services/api";
import toast from "react-hot-toast";
import { AcademicCapIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";

const QTYPES = [
  { id: "mcq",          label: "Multiple Choice" },
  { id: "true_false",   label: "True / False" },
  { id: "short_answer", label: "Short Answer" },
];

export default function QuizPage() {
  const [docs, setDocs]             = useState([]);
  const [docId, setDocId]           = useState("");
  const [selectedTypes, setTypes]   = useState(["mcq"]);
  const [count, setCount]           = useState(10);
  const [quiz, setQuiz]             = useState(null);
  const [answers, setAnswers]       = useState({});
  const [result, setResult]         = useState(null);
  const [loading, setLoading]       = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    docsAPI.list({ per_page: 100 }).then(({ data }) => setDocs(data.items || []));
  }, []);

  const toggleType = (t) =>
    setTypes((prev) => prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]);

  const handleGenerate = async () => {
    if (!docId)             { toast.error("Select a document"); return; }
    if (!selectedTypes.length) { toast.error("Select at least one question type"); return; }
    setLoading(true);
    setQuiz(null);
    setResult(null);
    setAnswers({});
    try {
      const { data } = await quizAPI.generate({
        document_id:    docId,
        question_types: selectedTypes,
        count,
      });
      setQuiz(data);
      toast.success(`${data.questions?.length} questions generated!`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const { data } = await quizAPI.submit({ quiz_id: quiz.quiz_id, answers });
      setResult(data);
    } finally {
      setSubmitting(false);
    }
  };

  const scoreColor = (s) => s >= 80 ? "text-emerald-600" : s >= 50 ? "text-yellow-600" : "text-red-600";
  const answered   = quiz ? Object.keys(answers).length : 0;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="page-title">Quiz Generator</h1>
      <p className="page-subtitle">Test your knowledge with AI-generated questions.</p>

      {/* Setup card */}
      {!quiz && (
        <div className="card p-6 mb-6">
          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Document</label>
              <select className="input" value={docId} onChange={(e) => setDocId(e.target.value)}>
                <option value="">Choose a document…</option>
                {docs.map((d) => <option key={d.id} value={d.id}>{d.original_name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Question Types</label>
              <div className="space-y-2">
                {QTYPES.map(({ id, label }) => (
                  <label key={id} className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="rounded border-slate-300 text-primary-600"
                      checked={selectedTypes.includes(id)} onChange={() => toggleType(id)} />
                    <span className="text-sm text-slate-700">{label}</span>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Number of Questions</label>
              <input type="number" className="input" min={3} max={30} value={count}
                onChange={(e) => setCount(Number(e.target.value))} />
            </div>
          </div>
          <button onClick={handleGenerate} disabled={loading} className="btn-primary">
            {loading ? <><span className="spinner w-4 h-4" /> Generating Quiz…</> : <><AcademicCapIcon className="w-4 h-4" /> Generate Quiz</>}
          </button>
        </div>
      )}

      {/* Quiz questions */}
      {quiz && !result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-600 font-medium">{answered} / {quiz.questions?.length} answered</p>
            <button onClick={() => setQuiz(null)} className="btn-secondary text-xs">New Quiz</button>
          </div>

          {quiz.questions?.map((q, i) => (
            <div key={q.id} className="card p-5">
              <div className="flex items-start gap-3 mb-3">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-primary-100 text-primary-700 text-sm font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                <p className="text-sm font-medium text-slate-800">{q.question}</p>
              </div>

              {/* MCQ / True-False options */}
              {q.options && (
                <div className="space-y-2 ml-10">
                  {q.options.map((opt) => (
                    <label key={opt.label} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors
                      ${answers[q.id] === opt.label
                        ? "bg-primary-50 border-primary-400"
                        : "bg-white border-slate-200 hover:bg-slate-50"}`}>
                      <input type="radio" name={q.id} value={opt.label} className="text-primary-600"
                        checked={answers[q.id] === opt.label}
                        onChange={() => setAnswers({ ...answers, [q.id]: opt.label })} />
                      <span className="text-sm text-slate-700"><strong>{opt.label}.</strong> {opt.text}</span>
                    </label>
                  ))}
                </div>
              )}

              {/* Short answer */}
              {!q.options && (
                <textarea
                  className="input mt-2 ml-10 h-20 resize-none"
                  placeholder="Type your answer…"
                  value={answers[q.id] || ""}
                  onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                />
              )}
            </div>
          ))}

          <button
            onClick={handleSubmit}
            disabled={submitting || answered === 0}
            className="btn-primary w-full justify-center py-3"
          >
            {submitting ? <><span className="spinner w-4 h-4" /> Evaluating…</> : "Submit Quiz"}
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="card p-6 text-center">
            <p className="text-sm text-slate-500 mb-1">Your Score</p>
            <p className={`text-5xl font-bold ${scoreColor(result.score)}`}>{result.score}%</p>
            <p className="text-slate-500 text-sm mt-1">{result.correct} / {result.total} correct</p>
            <button onClick={() => { setQuiz(null); setResult(null); }} className="btn-primary mt-4">
              New Quiz
            </button>
          </div>

          {result.feedback?.map((f, i) => (
            <div key={i} className={`card p-4 border-l-4 ${f.is_correct ? "border-emerald-400" : "border-red-400"}`}>
              <div className="flex items-start gap-2">
                {f.is_correct
                  ? <CheckCircleIcon className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                  : <XCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                }
                <div>
                  <p className="text-sm font-medium text-slate-800">{f.question}</p>
                  {!f.is_correct && <p className="text-xs text-red-600 mt-1">Your answer: {f.submitted || "(blank)"}</p>}
                  <p className="text-xs text-emerald-600 mt-1">Correct: {f.correct_answer}</p>
                  {f.explanation && <p className="text-xs text-slate-500 mt-1">{f.explanation}</p>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
