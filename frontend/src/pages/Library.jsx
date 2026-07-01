import { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { supabase } from "../lib/supabase";

function SkeletonCard() {
  return (
    <div className="rounded-2xl overflow-hidden border border-[#162033] bg-[#0A1120] aspect-square animate-shimmer" />
  );
}

export default function Library() {
  const [avatars, setAvatars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);
  const { signOut } = useAuth();

  useEffect(() => {
    async function fetchAvatars() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from("avatars")
        .select("id, avatar_url, created_at")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });

      if (!error) setAvatars(data || []);
      setLoading(false);
    }
    fetchAvatars();
  }, []);

  async function handleDelete(id) {
    setDeleting(id);
    const { error } = await supabase.from("avatars").delete().eq("id", id);
    if (!error) setAvatars((prev) => prev.filter((a) => a.id !== id));
    setDeleting(null);
  }

  function formatDate(ts) {
    return new Date(ts).toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  return (
    <div
      className="min-h-screen bg-[#05090F] text-white relative"
      style={{ fontFamily: "'Outfit', sans-serif" }}
    >
      {/* Ambient glow */}
      <div className="fixed top-0 right-1/4 w-[500px] h-[300px] rounded-full bg-indigo-600/5 blur-[140px] pointer-events-none" />

      {/* ── NAV ─────────────────────────────────────────────────── */}
      <nav className="relative z-10 border-b border-[#162033] px-8 py-4 flex items-center gap-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <span className="text-white text-sm">✦</span>
          </div>
          <span className="font-bold tracking-wide text-white">AvatarAI</span>
        </div>

        <div className="flex items-center gap-1 bg-[#0A1120] border border-[#162033] rounded-xl p-1">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? "bg-[#162033] text-white shadow"
                  : "text-slate-500 hover:text-slate-300"
              }`
            }
          >
            Generator
          </NavLink>
          <NavLink
            to="/library"
            className={({ isActive }) =>
              `px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? "bg-[#162033] text-white shadow"
                  : "text-slate-500 hover:text-slate-300"
              }`
            }
          >
            Library
          </NavLink>
        </div>

        <button
          onClick={signOut}
          className="ml-auto text-sm text-slate-600 hover:text-red-400 transition"
        >
          Sign out
        </button>
      </nav>

      {/* ── MAIN ─────────────────────────────────────────────────── */}
      <main className="relative z-10 max-w-6xl mx-auto px-8 py-12">
        {/* Header */}
        <div className="flex items-end justify-between mb-10">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">
              Your{" "}
              <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                Library
              </span>
            </h1>
            <p className="text-slate-500 mt-2 text-sm">
              {loading
                ? "Loading…"
                : `${avatars.length} avatar${avatars.length !== 1 ? "s" : ""} generated`}
            </p>
          </div>

          {avatars.length > 0 && (
            <NavLink
              to="/"
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600
                         hover:from-violet-500 hover:to-indigo-500 text-sm font-medium text-white transition shadow-lg shadow-violet-500/20"
            >
              <span>✦</span>
              New avatar
            </NavLink>
          )}
        </div>

        {/* Loading skeletons */}
        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && avatars.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 text-center">
            <div className="w-20 h-20 rounded-3xl bg-[#0A1120] border border-[#1C2D45] flex items-center justify-center mb-6">
              <span className="text-3xl opacity-20">✦</span>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              No avatars yet
            </h2>
            <p className="text-slate-500 text-sm mb-8 max-w-xs">
              Generate your first AI avatar and it will appear here
              automatically.
            </p>
            <NavLink
              to="/"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600
                         hover:from-violet-500 hover:to-indigo-500 text-sm font-semibold text-white transition shadow-lg shadow-violet-500/20"
            >
              <span>✦</span>
              Generate your first avatar
            </NavLink>
          </div>
        )}

        {/* Avatar grid */}
        {!loading && avatars.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {avatars.map((avatar) => (
              <AvatarCard
                key={avatar.id}
                avatar={avatar}
                deleting={deleting === avatar.id}
                onDelete={() => handleDelete(avatar.id)}
                formatDate={formatDate}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function AvatarCard({ avatar, deleting, onDelete, formatDate }) {
  const [loaded, setLoaded] = useState(false);
  const [confirm, setConfirm] = useState(false);

  const proxyUrl = `${import.meta.env.VITE_API_URL}/proxy-image?url=${encodeURIComponent(avatar.avatar_url)}`;

  return (
    <div className="group relative rounded-2xl overflow-hidden border border-[#162033] bg-[#0A1120] aspect-square">
      {/* Skeleton while loading */}
      {!loaded && <div className="absolute inset-0 animate-shimmer" />}

      <img
        src={proxyUrl}
        alt="Avatar"
        className={`w-full h-full object-cover transition-opacity duration-500 ${loaded ? "opacity-100" : "opacity-0"}`}
        onLoad={() => setLoaded(true)}
        onError={() => setLoaded(true)}
      />

      {/* Hover overlay */}
      <div
        className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent
                      opacity-0 group-hover:opacity-100 transition-all duration-200 flex flex-col justify-end p-3"
      >
        <p className="text-xs text-slate-400 mb-2 font-mono">
          {formatDate(avatar.created_at)}
        </p>

        {!confirm ? (
          <button
            onClick={() => setConfirm(true)}
            className="w-full py-1.5 rounded-lg bg-red-500/20 border border-red-500/30
                       text-red-400 text-xs font-medium hover:bg-red-500/30 transition"
          >
            Delete
          </button>
        ) : (
          <div className="flex gap-1.5">
            <button
              onClick={onDelete}
              disabled={deleting}
              className="flex-1 py-1.5 rounded-lg bg-red-600 text-white text-xs font-medium
                         hover:bg-red-500 transition disabled:opacity-50"
            >
              {deleting ? "…" : "Confirm"}
            </button>
            <button
              onClick={() => setConfirm(false)}
              className="flex-1 py-1.5 rounded-lg bg-white/10 text-white text-xs font-medium hover:bg-white/20 transition"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
