// smart-study-agent/frontend/src/services/api.js
// Centralised Axios instance. Attaches JWT automatically from localStorage.

import axios from "axios";
import toast from "react-hot-toast";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000/api",
  timeout: 60000,
});

// ── Request interceptor: attach bearer token ──────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Response interceptor: handle auth expiry ─────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            {},
            { headers: { Authorization: `Bearer ${refresh}` } }
          );
          localStorage.setItem("access_token", data.access_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.clear();
          window.location.href = "/login";
        }
      }
    }
    const msg = err.response?.data?.error || "An unexpected error occurred";
    if (err.response?.status !== 401) toast.error(msg);
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  login:    (data) => api.post("/auth/login", data),
  refresh:  ()     => api.post("/auth/refresh"),
  me:       ()     => api.get("/auth/me"),
};

// ── Documents ─────────────────────────────────────────────────────────────────
export const docsAPI = {
  upload:  (formData) => api.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  list:    (params)   => api.get("/documents/", { params }),
  get:     (id)       => api.get(`/documents/${id}`),
  delete:  (id)       => api.delete(`/documents/${id}`),
  search:  (q)        => api.get("/documents/search", { params: { q } }),
};

// ── Summary ───────────────────────────────────────────────────────────────────
export const summaryAPI = {
  generate: (body)    => api.post("/summary/generate", body),
  get:      (id, len) => api.get(`/summary/${id}`, { params: { length: len } }),
};

// ── Flashcards ────────────────────────────────────────────────────────────────
export const flashcardAPI = {
  generate: (body)  => api.post("/flashcards/generate", body),
  get:      (docId) => api.get(`/flashcards/${docId}`),
  reviewed: (body)  => api.post("/flashcards/reviewed", body),
};

// ── Quiz ──────────────────────────────────────────────────────────────────────
export const quizAPI = {
  generate: (body)  => api.post("/quiz/generate", body),
  submit:   (body)  => api.post("/quiz/submit", body),
  history:  ()      => api.get("/quiz/history"),
};

// ── Planner ───────────────────────────────────────────────────────────────────
export const plannerAPI = {
  generate: (body) => api.post("/planner/generate", body),
  get:      ()     => api.get("/planner/"),
};

// ── Progress ──────────────────────────────────────────────────────────────────
export const progressAPI = {
  dashboard: ()     => api.get("/progress/dashboard"),
  log:       (body) => api.post("/progress/log", body),
};

// ── Chat ──────────────────────────────────────────────────────────────────────
export const chatAPI = {
  ask: (body) => api.post("/chat/ask", body),
};

export default api;
