import { useEffect, useState } from "react";

export default function LoadingOverlay({ loading }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!loading) {
      setStep(0);
      return;
    }

    setStep(1);

    const timer1 = setTimeout(() => setStep(2), 900);
    const timer2 = setTimeout(() => setStep(3), 1800);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [loading]);

  if (!loading) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#05090f]/90 backdrop-blur-md">
      <div className="w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900 p-10 shadow-2xl">
        <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-slate-700 border-t-indigo-500"></div>

        <h2 className="mt-8 text-center text-2xl font-bold text-white">
          Generating your avatar
        </h2>

        <p className="mt-3 text-center text-slate-400">
          Please wait while AI processes your portrait.
        </p>

        <div className="mt-8 space-y-5">
          <Step
            text="Uploading image"
            status={step >= 1 ? "done" : "pending"}
          />

          <Step
            text="Detecting facial attributes"
            status={step >= 2 ? "done" : step === 1 ? "active" : "pending"}
          />

          <Step
            text="Generating AI artwork"
            status={step >= 3 ? "active" : "pending"}
          />
        </div>

        <p className="mt-8 text-center text-sm text-slate-500">
          Usually completes in 5–15 seconds
        </p>
      </div>
    </div>
  );
}

function Step({ text, status }) {
  return (
    <div className="flex items-center gap-4">
      {status === "done" && (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500 font-bold text-white">
          ✓
        </div>
      )}

      {status === "active" && (
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-indigo-500"></div>
      )}

      {status === "pending" && (
        <div className="h-8 w-8 rounded-full border border-slate-700"></div>
      )}

      <span className={status === "pending" ? "text-slate-500" : "text-white"}>
        {text}
      </span>
    </div>
  );
}
