import { useEffect, useState } from "react";

export default function AvatarPreview({ imageUrl, style, onImageLoaded }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(false);
  }, [imageUrl]);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="text-xl font-semibold text-white">Generated Avatar</h2>

      <p className="mt-2 text-sm text-slate-400">
        Your AI-generated avatar will appear here.
      </p>

      <div className="relative mt-6 flex h-96 overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
        {imageUrl ? (
          <img
            key={imageUrl}
            src={imageUrl}
            alt="Generated Avatar"
            onLoad={() => {
              setVisible(true);
              onImageLoaded?.();
            }}
            onError={() => {
              onImageLoaded?.();
            }}
            className={`
                absolute
                h-full
                w-full
                object-cover
                transition-opacity
                duration-500
                ${visible ? "opacity-100" : "opacity-0"}
              `}
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center text-center">
            <div className="text-7xl">🎨</div>

            <p className="mt-4 text-slate-400">
              Your generated avatar will appear here
            </p>
          </div>
        )}
      </div>

      {imageUrl && (
        <div className="mt-6">
          <div className="flex justify-between text-sm text-slate-400">
            <span>Resolution</span>

            <span>512 × 512</span>
          </div>

          <div className="mt-2 flex justify-between text-sm text-slate-400">
            <span>Style</span>

            <span className="capitalize">{style}</span>
          </div>

          <button
            onClick={async () => {
              try {
                const response = await fetch(imageUrl);
                const blob = await response.blob();

                const url = window.URL.createObjectURL(blob);

                const link = document.createElement("a");
                link.href = url;
                link.download = `pixel-perfect-${Date.now()}.png`;

                document.body.appendChild(link);
                link.click();
                link.remove();

                window.URL.revokeObjectURL(url);
              } catch (err) {
                console.error(err);
              }
            }}
            className="
              mt-6
              flex
              w-full
              items-center
              justify-center
              rounded-xl
              bg-indigo-600
              py-3
              font-semibold
              transition
              hover:bg-indigo-500
            "
          >
            Download Avatar
          </button>
        </div>
      )}
    </div>
  );
}
