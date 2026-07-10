import { useState } from "react";

import Header from "../components/Header";
import UploadBox from "../components/UploadBox";
import StyleSelector from "../components/StyleSelector";
import AvatarPreview from "../components/AvatarPreview";
import PredictionCard from "../components/PredictionCard";
import Footer from "../components/Footer";
import LoadingOverlay from "../components/LoadingOverlay";

import { API_BASE, generateAvatar } from "../services/api";

export default function Home() {
  const [image, setImage] = useState(null);

  const [style, setStyle] = useState("ghibli");

  const [isGenerating, setIsGenerating] = useState(false);

  const [isImageLoading, setIsImageLoading] = useState(false);

  const [prediction, setPrediction] = useState(null);

  const [prompt, setPrompt] = useState("");

  const [imageUrl, setImageUrl] = useState("");

  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!image) {
      setError("Please select an image first.");
      return;
    }

    const MIN_GENERATION_TIME = 1200;

    try {
      setIsGenerating(true);
      setIsImageLoading(false);
      setError("");

      setPrediction(null);
      setPrompt("");
      setImageUrl("");

      const start = Date.now();

      const result = await generateAvatar(image, style);

      const elapsed = Date.now() - start;

      if (elapsed < MIN_GENERATION_TIME) {
        await new Promise((resolve) =>
          setTimeout(resolve, MIN_GENERATION_TIME - elapsed),
        );
      }

      setPrediction(result.prediction);

      setPrompt(result.prompt);

      setImageUrl(
        `${API_BASE}/proxy-image?url=${encodeURIComponent(
          result.image_url,
        )}&t=${Date.now()}`,
      );
      setIsImageLoading(true);
    } catch (err) {
      let message = "Avatar generation failed.";

      if (err.message.includes("504")) {
        message = "The AI model took too long to respond. Please try again.";
      } else if (err.message.includes("Failed to fetch")) {
        message = "Unable to connect to the backend server.";
      } else {
        message = err.message;
      }

      setError(message);
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#05090f] text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <Header />

        <div className="mt-12 grid gap-8 lg:grid-cols-2">
          {/* LEFT PANEL */}

          <div className="space-y-6">
            <UploadBox image={image} setImage={setImage} />

            <StyleSelector style={style} setStyle={setStyle} />

            <button
              onClick={handleGenerate}
              disabled={isGenerating || isImageLoading || !image}
              className="
                w-full
                rounded-xl
                bg-indigo-600
                py-4
                text-lg
                font-semibold
                transition
                hover:bg-indigo-500
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              {isGenerating || isImageLoading
                ? "Generating Avatar..."
                : "Generate Avatar"}
            </button>
          </div>

          {/* RIGHT PANEL */}

          <div>
            <AvatarPreview
              imageUrl={imageUrl}
              style={style}
              onImageLoaded={() => {
                setIsImageLoading(false);
              }}
            />
          </div>
        </div>

        {/* Prediction */}

        <PredictionCard prediction={prediction} prompt={prompt} />

        <Footer />
      </div>
      <LoadingOverlay loading={isGenerating || isImageLoading} />
    </div>
  );
}
