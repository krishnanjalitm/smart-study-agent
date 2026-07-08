// smart-study-agent/frontend/src/pages/FlashcardsPage.jsx
// Generate and review interactive flashcards.

import React, { useEffect, useState } from "react";
import { docsAPI, flashcardAPI } from "../services/api";
import toast from "react-hot-toast";
import { BookOpenIcon, ArrowLeftIcon, ArrowRightIcon, ArrowPathIcon } from "@heroicons/react/24/outline";

function FlashCard({ card, index, total }) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div className="flex flex-col items-center">
      <p className="text-sm text-slate-500 mb-3">Card {index + 1} of {total}</p>

      {/* Card flip */}
      <div
        className="w-full max-w-xl h-56 cursor-pointer relative"
        style={{ perspective: "1000px" }}
        onClick={() => setFlipped(!flipped)}
      >
        <div
          className="relative w-full h-full transition-transform duration-500"
          style={{ transformStyle: "preserve-3d", transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)" }}
        >
          {/* Front */}
          <div
            className="absolute inset-0 card flex flex-col items-center justify-center p-8 bg-primary-50 border-primary-200"
            style={{ backfaceVisibility: "hidden" }}
          >
            <span className="badge bg-primary-100 text-primary-600 mb-4">Question</span>
            <p className="text-lg font-semibold text-slate-800 text-center">{card.front}</p>
            <p className="text-xs text-slate-400 mt-4">Click to reveal answer</p>
          </div>
          {/* Back */}
          <div
            className="absolute inset-0 card flex flex-col items-center justify-center p-8 bg-emerald-50 border-emerald-200"
            style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
          >
            <span className="badge bg-emerald-100 text-emerald-700 mb-4">Answer</span>
            <p className="text-base text-slate-800 text-center">{card.back}</p>
            {card.hint && <p className="text-xs text-slate-500 mt-3 italic">Hint: {card.hint}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FlashcardsPage() {
  const [docs, setDocs]         = useState([]);
  const [docId, setDocId]       = useState("");
  const [count, setCount]       = useState(10);
  const [cards, setCards]       = useState([]);
  const [index, setIndex]       = useState(0);
  const [loading, setLoading]   = useState(false);

  useEffect(() => {
    docsAPI.list({ per_page: 100 }).then(({ data }) => setDocs(data.items || []));
  }, []);

  const handleGenerate = async () => {
    if (!docId) { toast.error("Select a document"); return; }
    setLoading(true);
    setCards([]);
    setIndex(0);
    try {
      const { data } = await flashcardAPI.generate({ document_id: docId, count });
      setCards(data.cards || []);
      toast.success(`${data.cards?.length} flashcards generated!`);
    } finally {
      setLoading(false);
    }
  };

  const markReviewed = async () => {
    await flashcardAPI.reviewed({ count: 1 });
    toast("Session logged ✓");
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="page-title">Flashcards</h1>
      <p className="page-subtitle">AI-generated question-answer cards to boost retention.</p>

      {/* Setup */}
      <div className="card p-5 mb-6">
        <div className="grid sm:grid-cols-3 gap-4 mb-4">
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1">Document</label>
            <select className="input" value={docId} onChange={(e) => setDocId(e.target.value)}>
              <option value="">Select document…</option>
              {docs.map((d) => <option key={d.id} value={d.id}>{d.original_name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Cards</label>
            <input type="number" className="input" min={1} max={50} value={count}
              onChange={(e) => setCount(Number(e.target.value))} />
          </div>
        </div>
        <button onClick={handleGenerate} disabled={loading} className="btn-primary">
          {loading ? <><span className="spinner w-4 h-4" /> Generating…</> : <><BookOpenIcon className="w-4 h-4" /> Generate Flashcards</>}
        </button>
      </div>

      {/* Flashcard viewer */}
      {cards.length > 0 && (
        <>
          <FlashCard card={cards[index]} index={index} total={cards.length} />

          <div className="flex items-center justify-center gap-4 mt-6">
            <button onClick={() => setIndex(Math.max(0, index - 1))} disabled={index === 0}
              className="btn-secondary px-3">
              <ArrowLeftIcon className="w-5 h-5" />
            </button>

            <span className="text-sm text-slate-500">{index + 1} / {cards.length}</span>

            {index < cards.length - 1 ? (
              <button onClick={() => setIndex(index + 1)} className="btn-primary px-3">
                <ArrowRightIcon className="w-5 h-5" />
              </button>
            ) : (
              <button onClick={() => { setIndex(0); markReviewed(); }} className="btn-primary">
                <ArrowPathIcon className="w-4 h-4" /> Restart & Log
              </button>
            )}
          </div>

          {/* Progress bar */}
          <div className="mt-4 bg-slate-200 rounded-full h-1.5">
            <div
              className="bg-primary-600 h-1.5 rounded-full transition-all"
              style={{ width: `${((index + 1) / cards.length) * 100}%` }}
            />
          </div>
        </>
      )}
    </div>
  );
}
