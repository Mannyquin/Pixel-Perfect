import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function AuthPage() {
  const { signIn, signUp } = useAuth();
  const navigate = useNavigate();

  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    try {
      setError("");
      setLoading(true);
      await (isLogin ? signIn : signUp)(email, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#05090F] flex items-center justify-center px-4 relative overflow-hidden">
      {/* Ambient glow orbs */}
      <div className="absolute top-[-20%] left-[10%] w-[500px] h-[500px] rounded-full bg-violet-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[5%] w-[400px] h-[400px] rounded-full bg-indigo-500/8 blur-[100px] pointer-events-none" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-md animate-fade-up">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 mb-5 shadow-lg shadow-violet-500/20">
            <span className="text-white text-xl">✦</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            {isLogin ? "Welcome back" : "Get started"}
          </h1>
          <p className="text-slate-500 text-sm mt-2">
            {isLogin
              ? "Sign in to your account to continue"
              : "Create an account — it's free"}
          </p>
        </div>

        {/* Form card */}
        <div className="bg-[#0A1120] border border-[#162033] rounded-2xl p-8 shadow-2xl">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm mb-6 flex items-center gap-2">
              <span>⚠</span>
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5 tracking-wide uppercase">
                Email
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#05090F] border border-[#1C2D45] rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600
                           focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5 tracking-wide uppercase">
                Password
              </label>
              <input
                type="password"
                placeholder="Min. 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                className="w-full bg-[#05090F] border border-[#1C2D45] rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600
                           focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30 transition"
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading || !email || !password}
              className="w-full relative mt-2 py-3 rounded-xl font-semibold text-sm text-white
                         bg-gradient-to-r from-violet-600 to-indigo-600
                         hover:from-violet-500 hover:to-indigo-500
                         disabled:opacity-40 disabled:cursor-not-allowed
                         transition-all duration-200 shadow-lg shadow-violet-500/20
                         focus:outline-none focus:ring-2 focus:ring-violet-500/40"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span
                    className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full inline-block"
                    style={{ animation: "spin 0.7s linear infinite" }}
                  />
                  Please wait…
                </span>
              ) : isLogin ? (
                "Sign in"
              ) : (
                "Create account"
              )}
            </button>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#162033]" />
            </div>
          </div>

          <p className="text-center text-sm text-slate-500">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
              }}
              className="text-violet-400 font-medium hover:text-violet-300 transition"
            >
              {isLogin ? "Sign up" : "Sign in"}
            </button>
          </p>
        </div>

        <p className="text-center text-xs text-slate-700 mt-6">
          AI-powered avatar generation · Final Year Project
        </p>
      </div>
    </div>
  );
}
