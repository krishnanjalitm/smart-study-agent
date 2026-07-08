// smart-study-agent/frontend/src/App.jsx
// Root component — wires routing, auth context, and toast notifications.

import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import { AuthProvider, useAuth } from "./context/AuthContext";
import Layout         from "./components/Layout";
import LoginPage      from "./pages/LoginPage";
import RegisterPage   from "./pages/RegisterPage";
import DashboardPage  from "./pages/DashboardPage";
import DocumentsPage  from "./pages/DocumentsPage";
import SummaryPage    from "./pages/SummaryPage";
import FlashcardsPage from "./pages/FlashcardsPage";
import QuizPage       from "./pages/QuizPage";
import PlannerPage    from "./pages/PlannerPage";
import ProgressPage   from "./pages/ProgressPage";
import ChatPage       from "./pages/ChatPage";

/** Guard: redirect to /login if not authenticated */
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="spinner w-10 h-10" />
    </div>
  );
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { borderRadius: "10px", background: "#1e293b", color: "#f1f5f9" },
          }}
        />
        <Routes>
          {/* Public */}
          <Route path="/login"    element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected — wrapped in sidebar layout */}
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            <Route index                element={<DashboardPage />} />
            <Route path="documents"     element={<DocumentsPage />} />
            <Route path="summary"       element={<SummaryPage />} />
            <Route path="flashcards"    element={<FlashcardsPage />} />
            <Route path="quiz"          element={<QuizPage />} />
            <Route path="planner"       element={<PlannerPage />} />
            <Route path="progress"      element={<ProgressPage />} />
            <Route path="chat"          element={<ChatPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
