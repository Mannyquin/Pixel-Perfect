export const API_BASE = import.meta.env.VITE_API_URL;

export async function generateAvatar(image, style) {
  const formData = new FormData();

  formData.append("file", image);
  formData.append("style", style);

  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Avatar generation failed.");
  }

  return await response.json();
}
