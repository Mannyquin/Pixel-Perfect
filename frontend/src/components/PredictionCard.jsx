function Info({ title, value, confidence }) {
  return (
    <div className="rounded-xl bg-slate-900 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{title}</p>

      <p className="mt-2 text-lg font-semibold text-white">{value}</p>

      {confidence !== undefined && (
        <p className="mt-1 text-xs text-indigo-300">
          {(confidence * 100).toFixed(1)}%
        </p>
      )}
    </div>
  );
}

export default function PredictionCard({ prediction, prompt }) {
  if (!prediction) return null;

  const hair = prediction.hair;
  const face = prediction.face;

  return (
    <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="text-2xl font-bold text-white">Prediction Summary</h2>

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Info title="Hair Color" value={hair.color.label} />

        <Info title="Hair Texture" value={hair.texture.label} />

        <Info
          title="Face Shape"
          value={face.oval_face.value ? "Oval" : "Unknown"}
        />

        <Info title="Style" value="AI Generated" />
      </div>

      <div className="mt-8 rounded-xl bg-slate-950 p-5">
        <h3 className="font-semibold text-white">Generated Prompt</h3>

        <p className="mt-3 text-slate-400 leading-relaxed">{prompt}</p>
      </div>
    </div>
  );
}
