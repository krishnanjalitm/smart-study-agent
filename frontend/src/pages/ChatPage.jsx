// smart-study-agent/frontend/src/pages/ChatPage.jsx
// AI chat with RAG source citations, powered by IBM Granite.

import React, { useState, useRef, useEffect } from "react";
import { chatAPI, docsAPI } from "../services/api";
import ReactMarkdown from "react-markdown";
import { PaperAirplaneIcon, UserCircleIcon, SparklesIcon, DocumentTextIcon } from "@heroicons/react/24/outline";

function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? "bg-primary-600" : "bg-secondary-500"}`}>
        {isUser
          ? <UserCircleIcon className="w-5 h-5 text-white" />
          : <SparklesIcon    className="w-5 h-5 text-white" />
        }
      </div>
      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        <div className={`px-4 py-3 rounded-2xl text-sm ${
          isUser
            ? "bg-primary-600 text-white rounded-tr-sm"
            : "bg-white border border-slate-200 text-slate-800 rounded-tl-sm"
        }`}>
          {isUser
            ? <p>{msg.content}</p>
            : <ReactMarkdown className="prose prose-sm max-w-none">{msg.content}</ReactMarkdown>
          }
        </div>
        {/* Source citations */}
        {msg.sources?.length > 0 && (
          <div className="space-y-1 w-full">
            <p className="text-xs text-slate-400 font-medium">Sources cited:</p>
            {msg.sources.map((s, i) => (
              <div key={i} className="flex items-start gap-2 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
                <DocumentTextIcon className="w-4 h-4 text-primary-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-slate-700">{s.document_name}</p>
                  <p className="text-xs text-slate-500 line-clamp-2">{s.chunk_text?.slice(0, 120)}…</p>
                  <span className="text-xs text-primary-600">Score: {(s.score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages]     = useState([
    { role: "assistant", content: "Hello! I'm your AI Study Assistant powered by IBM Granite. Upload your study materials and ask me anything about them. I'll answer with source citations from your documents." }
  ]);
  const [input, setInput]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [docs, setDocs]             = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const bottomRef                   = useRef(null);

  useEffect(() => {
    docsAPI.list({ per_page: 50 }).then(({ data }) => setDocs(data.items || []));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const toggleDoc = (id) =>
    setSelectedDocs((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const history = messages.slice(-6).map(({ role, content }) => ({ role, content }));
      const { data } = await chatAPI.ask({
        message:      text,
        document_ids: selectedDocs,
        history,
      });
      setMessages((prev) => [...prev, {
        role:    "assistant",
        content: data.answer,
        sources: data.sources,
      }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex gap-5 h-[calc(100vh-140px)]">
      {/* Sidebar: document selector */}
      <div className="w-52 flex-shrink-0 card p-3 flex flex-col">
        <p className="text-xs font-semibold text-slate-600 mb-2 px-1">Study Materials</p>
        {docs.length === 0 ? (
          <p className="text-xs text-slate-400 px-1">Upload documents to enable context-aware chat.</p>
        ) : (
          <div className="flex-1 overflow-y-auto space-y-1">
            {docs.map((d) => (
              <label key={d.id} className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-slate-300 text-primary-600"
                  checked={selectedDocs.includes(d.id)}
                  onChange={() => toggleDoc(d.id)}
                />
                <span className="text-xs text-slate-700 truncate">{d.original_name}</span>
              </label>
            ))}
          </div>
        )}
        {selectedDocs.length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-100">
            <p className="text-xs text-primary-600 font-medium">{selectedDocs.length} doc{selectedDocs.length !== 1 ? "s" : ""} selected</p>
          </div>
        )}
      </div>

      {/* Chat panel */}
      <div className="flex-1 flex flex-col card overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-100">
          <SparklesIcon className="w-5 h-5 text-secondary-500" />
          <span className="font-semibold text-slate-800 text-sm">AI Study Assistant</span>
          <span className="ml-auto badge bg-secondary-100 text-secondary-600">IBM Granite</span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-secondary-500 flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <div className="px-4 py-3 border-t border-slate-100 flex gap-2">
          <input
            type="text"
            className="input flex-1"
            placeholder="Ask anything about your study materials…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary px-3"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
