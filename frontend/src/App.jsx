import { useState, useRef } from "react";

const STYLES = [
  { key: "ghibli", label: "Ghibli", icon: "✪", desc: "Soft anime art" },
  {
    key: "minecraft",
    label: "Minecraft",
    icon: "🎮",
    desc: "Steve & Alex style",
  },
  { key: "cinematic", label: "Cinematic", icon: "🎬", desc: "Photorealistic" },
  { key: "oil", label: "Oil Paint", icon: "🎨", desc: "Classic painted" },
];

const API_URL = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [style, setStyle] = useState("ghibli");
  const [imgLoading, setImgLoading] = useState(false);
  const [imgRetry, setImgRetry] = useState(0);
  const [imgFailed, setImgFailed] = useState(false);

  const fileInputRef = useRef();

  function handleFile(file) {
    if (!file) return;
    if (!/\.(jpg|jpeg|png)$/i.test(file.name)) {
      setError("Please upload a JPEG or PNG file");
      return;
    }
    setError(null);
    setSelectedFile(file);
    setAvatarUrl(null);
    setPreview(URL.createObjectURL(file));
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  }

  async function generateAvatar() {
    if (!selectedFile) {
      setError("Upload a photo first");
      return;
    }

    setLoading(true);
    setError(null);
    setAvatarUrl(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const res = await fetch(`${API_URL}/generate?style=${style}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to generate avatar");
      const data = await res.json();

      setAvatarUrl(data.avatar_url);
      setImgRetry(0);
      setImgFailed(false);
      setImgLoading(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="min-h-screen bg-[#05090F] text-white relative"
      style={{ fontFamily: "'Outfit', sans-serif" }}
    >
      {/* Ambient glow */}
      <div className="fixed top-0 left-1/4 w-[600px] h-[300px] rounded-full bg-violet-600/5 blur-[140px] pointer-events-none" />

      {/* NAV */}
      <nav className="relative z-10 border-b border-[#162033] px-8 py-4 flex items-center gap-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <span className="text-white text-sm">✪</span>
          </div>
          <span className="font-bold tracking-wide text-white">
            Pixel Perfect
          </span>
        </div>
      </nav>

      {/* MAIN */}
      <main className="relative z-10 max-w-6xl mx-auto px-8 py-12">
        <div className="mb-10">
          <h1 className="text-4xl font-bold tracking-tight">
            Generate your{" "}
            <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
              AI Avatar
            </span>
          </h1>
          <p className="text-slate-500 mt-2 text-sm">
            Upload a photo, choose a style, and get your avatar in seconds.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* LEFT PANEL */}
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-widest mb-3">
                Photo
              </label>
              <div
                onClick={() => fileInputRef.current.click()}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                className={`relative rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200 overflow-hidden aspect-square
                ${
                  dragOver
                    ? "border-violet-500/60 bg-violet-500/5"
                    : preview
                      ? "border-[#1C2D45]"
                      : "border-[#1C2D45] hover:border-[#2a3f5f] bg-[#0A1120]"
                }`}
              >
                {preview ? (
                  <div className="relative">
                    <img
                      src={preview}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 hover:opacity-100 transition">
                      <span className="text-white text-sm font-medium">
                        Change photo
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="h-48 flex flex-col items-center justify-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-[#162033] flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-slate-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
                        />
                      </svg>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-slate-400 font-medium">
                        Drop photo here
                      </p>
                      <p className="text-xs text-slate-600 mt-0.5">
                        JPG or PNG · Max 10MB
                      </p>
                    </div>
                  </div>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".jpg,.jpeg,.png"
                  onChange={(e) => handleFile(e.target.files[0])}
                />
              </div>
            </div>

            {/* Style selector */}
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-widest mb-3">
                Style
              </label>
              <div className="grid grid-cols-2 gap-2.5">
                {STYLES.map((s) => (
                  <button
                    key={s.key}
                    onClick={() => setStyle(s.key)}
                    className={`group p-4 rounded-xl border text-left transition-all duration-200 ${
                      style === s.key
                        ? "border-violet-500/60 bg-violet-500/10 shadow-lg shadow-violet-500/10"
                        : "border-[#162033] bg-[#0A1120] hover:border-[#1C2D45]"
                    }`}
                  >
                    <div
                      className={`text-lg mb-2 transition ${style === s.key ? "opacity-100" : "opacity-50 group-hover:opacity-70"}`}
                    >
                      {s.icon}
                    </div>
                    <div className="font-semibold text-sm text-white">
                      {s.label}
                    </div>
                    <div className="text-xs text-slate-600 mt-0.5">
                      {s.desc}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Generate button */}
            <button
              onClick={generateAvatar}
              disabled={loading || !selectedFile}
              className="w-full py-3.5 rounded-xl font-semibold text-sm text-white
                         bg-gradient-to-r from-violet-600 to-indigo-600
                         hover:from-violet-500 hover:to-indigo-500
                         disabled:opacity-40 disabled:cursor-not-allowed
                         transition-all duration-200 shadow-lg shadow-violet-500/20
                         flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span
                    className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                    style={{ animation: "spin 0.7s linear infinite" }}
                  />
                  Analysing photo…
                </>
              ) : (
                <>
                  <span>✪</span>
                  Generate Avatar
                </>
              )}
            </button>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
                <span>⚠</span> {error}
              </div>
            )}
          </div>

          {/* RIGHT PANEL */}
          <div>
            <label className="block text-xs font-medium text-slate-500 uppercase tracking-widest mb-3">
              Result
            </label>
            <div className="bg-[#0A1120] border border-[#162033] rounded-2xl overflow-hidden aspect-square flex items-center justify-center relative">
              {!avatarUrl && !loading && (
                <span className="text-3xl opacity-10">✪</span>
              )}

              {loading && (
                <div className="text-center px-4">
                  <div
                    className="w-10 h-10 rounded-full border-2 border-violet-500/20 border-t-violet-500 mx-auto mb-4"
                    style={{ animation: "spin 1s linear infinite" }}
                  />
                  <p className="text-slate-400 text-xs">Analysing…</p>
                </div>
              )}

              {avatarUrl && imgLoading && !imgFailed && (
                <div className="text-center px-4">
                  <div
                    className="w-10 h-10 rounded-full border-2 border-indigo-500/20 border-t-indigo-400 mx-auto mb-4"
                    style={{ animation: "spin 1s linear infinite" }}
                  />
                  <p className="text-slate-400 text-xs">Rendering…</p>
                  {imgRetry > 0 && (
                    <p className="text-slate-600 text-xs mt-1">
                      Retry {imgRetry}/3
                    </p>
                  )}
                </div>
              )}

              {avatarUrl && !imgFailed && (
                <img
                  key={`avatar-${imgRetry}`}
                  src={`${API_URL}/proxy-image?url=${encodeURIComponent(avatarUrl)}`}
                  alt="Generated avatar"
                  className={`w-full h-full object-cover transition-opacity duration-700 ${imgLoading ? "hidden" : "opacity-100"}`}
                  onLoad={() => setImgLoading(false)}
                  onError={() => {
                    setImgLoading(false);
                    if (imgRetry < 3) {
                      setTimeout(() => {
                        setImgRetry((r) => r + 1);
                        setImgLoading(true);
                      }, 2000);
                    } else {
                      setImgFailed(true);
                    }
                  }}
                />
              )}

              {imgFailed && (
                <div className="text-center px-4">
                  <p className="text-slate-500 text-xs mb-3">Timed out</p>
                  <button
                    onClick={() => {
                      setImgRetry(0);
                      setImgFailed(false);
                      setImgLoading(true);
                    }}
                    className="px-4 py-2 rounded-lg border border-[#1C2D45] text-xs text-slate-300 hover:border-violet-500/40 transition"
                  >
                    Retry
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
