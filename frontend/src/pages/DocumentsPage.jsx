// smart-study-agent/frontend/src/pages/DocumentsPage.jsx
// Upload, list, search, and delete study documents.

import React, { useEffect, useState, useCallback, useRef } from "react";
import { docsAPI } from "../services/api";
import toast from "react-hot-toast";
import {
  DocumentArrowUpIcon, MagnifyingGlassIcon, TrashIcon,
  DocumentTextIcon, TagIcon,
} from "@heroicons/react/24/outline";

export default function DocumentsPage() {
  const [docs, setDocs]       = useState([]);
  const [total, setTotal]     = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQ, setSearchQ] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileRef               = useRef(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await docsAPI.list({ per_page: 50 });
      setDocs(data.items || []);
      setTotal(data.total || 0);
    } catch {
      /* handled globally */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleUpload = async (files) => {
    if (!files?.length) return;
    setUploading(true);
    for (const file of Array.from(files)) {
      const fd = new FormData();
      fd.append("file", file);
      try {
        await docsAPI.upload(fd);
        toast.success(`${file.name} uploaded`);
      } catch {
        /* handled globally */
      }
    }
    setUploading(false);
    load();
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    await docsAPI.delete(id);
    toast.success("Document deleted");
    load();
  };

  const filtered = searchQ.trim()
    ? docs.filter((d) =>
        d.original_name?.toLowerCase().includes(searchQ.toLowerCase()) ||
        d.tags?.some((t) => t.toLowerCase().includes(searchQ.toLowerCase()))
      )
    : docs;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="page-title">Documents</h1>
      <p className="page-subtitle">Upload and manage your study materials.</p>

      {/* Upload zone */}
      <div
        className={`card p-8 mb-6 text-center cursor-pointer border-2 border-dashed transition-colors
          ${dragging ? "border-primary-400 bg-primary-50" : "border-slate-300 hover:border-primary-400 hover:bg-primary-50"}`}
        onClick={() => fileRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handleUpload(e.dataTransfer.files); }}
      >
        <input
          ref={fileRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
          className="hidden"
          onChange={(e) => handleUpload(e.target.files)}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <div className="spinner w-8 h-8" />
            <p className="text-sm text-slate-500">Processing your files…</p>
          </div>
        ) : (
          <>
            <DocumentArrowUpIcon className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <p className="font-medium text-slate-700">Drag & drop or click to upload</p>
            <p className="text-sm text-slate-400 mt-1">PDF, DOCX, TXT, PNG, JPG supported · Max 16 MB</p>
          </>
        )}
      </div>

      {/* Search bar */}
      <div className="relative mb-4">
        <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search documents…"
          className="input pl-9"
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
        />
      </div>

      {/* Document list */}
      {loading ? (
        <div className="flex justify-center py-12"><div className="spinner w-8 h-8" /></div>
      ) : filtered.length === 0 ? (
        <div className="card p-10 text-center text-slate-400">
          <DocumentTextIcon className="w-10 h-10 mx-auto mb-2" />
          <p>{searchQ ? "No results found." : "No documents uploaded yet."}</p>
        </div>
      ) : (
        <div className="card divide-y divide-slate-100">
          <div className="px-4 py-2 text-xs text-slate-500 font-medium bg-slate-50 rounded-t-xl">
            {filtered.length} document{filtered.length !== 1 ? "s" : ""}
          </div>
          {filtered.map((d) => (
            <div key={d.id} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50">
              <DocumentTextIcon className="w-5 h-5 text-primary-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">{d.original_name}</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  <span className="text-xs text-slate-400">
                    {d.word_count?.toLocaleString()} words · {d.file_type?.toUpperCase()} · {d.page_count} page{d.page_count !== 1 ? "s" : ""}
                  </span>
                  {d.tags?.map((t) => (
                    <span key={t} className="badge bg-slate-100 text-slate-500 flex items-center gap-0.5">
                      <TagIcon className="w-3 h-3" />{t}
                    </span>
                  ))}
                </div>
              </div>
              <span className={`badge flex-shrink-0 ${
                d.status === "ready" ? "bg-green-100 text-green-700"
                : d.status === "error" ? "bg-red-100 text-red-700"
                : "bg-yellow-100 text-yellow-700"
              }`}>
                {d.status}
              </span>
              <button
                onClick={() => handleDelete(d.id, d.original_name)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
