// smart-study-agent/frontend/src/pages/RegisterPage.jsx

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { AcademicCapIcon } from "@heroicons/react/24/outline";

export default function RegisterPage() {
  const { register }          = useAuth();
  const navigate              = useNavigate();
  const [form, setForm]       = useState({ name: "", email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) {
      setError("Passwords do not match");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await register(form.name, form.email, form.password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-white px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary-600 mb-4">
            <AcademicCapIcon className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Smart Study Agent</h1>
          <p className="text-slate-500 text-sm mt-1">Create your account</p>
        </div>

        <div className="card p-8">
          <h2 className="text-xl font-semibold text-slate-800 mb-6">Get Started</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { key: "name",    label: "Full Name",       type: "text",     ph: "Jane Smith" },
              { key: "email",   label: "Email Address",   type: "email",    ph: "jane@example.com" },
              { key: "password", label: "Password",       type: "password", ph: "Min. 8 characters" },
              { key: "confirm",  label: "Confirm Password", type: "password", ph: "Repeat password" },
            ].map(({ key, label, type, ph }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
                <input
                  type={type}
                  className="input"
                  placeholder={ph}
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  required
                />
              </div>
            ))}

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
              {loading ? <span className="spinner w-4 h-4" /> : "Create Account"}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
