import { useRef } from "react";

export default function UploadBox({ image, setImage }) {
  const inputRef = useRef();

  function handleChange(e) {
    const file = e.target.files[0];

    if (!file) return;

    setImage(file);
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
      <h2 className="text-xl font-semibold text-white">Upload Portrait</h2>

      <p className="mt-2 text-sm text-slate-400">JPG or PNG • Maximum 10 MB</p>

      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg"
        hidden
        onChange={handleChange}
      />

      <div
        onClick={() => inputRef.current.click()}
        className="
          mt-6
          flex
          h-72
          cursor-pointer
          items-center
          justify-center
          rounded-xl
          border-2
          border-dashed
          border-slate-700
          bg-slate-950/40
          transition
          hover:border-indigo-500
          hover:bg-slate-900
        "
      >
        {image ? (
          <img
            src={URL.createObjectURL(image)}
            alt="Preview"
            className="h-full w-full rounded-xl object-cover"
          />
        ) : (
          <div className="text-center">
            <div className="text-6xl">📷</div>

            <p className="mt-4 text-slate-300">Click to upload</p>

            <p className="mt-2 text-sm text-slate-500">JPG • PNG</p>
          </div>
        )}
      </div>
    </div>
  );
}
