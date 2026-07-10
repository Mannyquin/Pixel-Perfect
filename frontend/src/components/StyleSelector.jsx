const styles = [
  {
    id: "ghibli",
    name: "Ghibli",
    emoji: "🌸",
    description: "Soft anime illustration",
  },
  {
    id: "minecraft",
    name: "Minecraft",
    emoji: "🧱",
    description: "Voxel game style",
  },
  {
    id: "cinematic",
    name: "Cinematic",
    emoji: "🎬",
    description: "Photorealistic portrait",
  },
  {
    id: "oil",
    name: "Oil Painting",
    emoji: "🎨",
    description: "Classic painted artwork",
  },
];

export default function StyleSelector({ style, setStyle }) {
  return (
    <div className="mt-8">
      <h2 className="mb-4 text-xl font-semibold text-white">Choose Style</h2>

      <div className="grid grid-cols-2 gap-4">
        {styles.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setStyle(item.id)}
            className={`
              rounded-2xl
              border
              p-5
              text-left
              transition-all
              duration-200

              ${
                style === item.id
                  ? "border-indigo-500 bg-indigo-500/20"
                  : "border-slate-800 bg-slate-900/40 hover:border-slate-600"
              }
            `}
          >
            <div className="text-3xl">{item.emoji}</div>

            <h3 className="mt-3 font-semibold text-white">{item.name}</h3>

            <p className="mt-1 text-sm text-slate-400">{item.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
