# 🎨 Pixel Perfect -- AI Avatar Generator

> **A modular AI-powered avatar generation system that combines deep
> learning, computer vision, semantic prompt engineering, and generative
> AI to create stylized avatars.**

Pixel Perfect is a portfolio-quality AI application that analyzes facial
attributes using deep learning, converts them into structured semantic
descriptions, and generates artistic avatars using multiple visual
styles.

Unlike identity-preserving avatar generators, Pixel Perfect focuses on
**semantic attribute preservation** (hair, face shape, facial features,
accessories, etc.) while allowing the image generation model to create
an entirely new artistic character.

---

# ✨ Features

- Multi-head EfficientNet-B0 facial attribute recognition
- Face Shape prediction using MediaPipe + XGBoost
- Hair Color prediction
- Hair Texture prediction
- Facial Hair detection
- Face Feature detection
- Accessory detection
- Structured prompt generation
- Multiple artistic styles
- FastAPI inference backend
- Modern React + Tailwind frontend
- Download generated avatars

---

# 🏗 System Architecture

```text
                User Image
                     │
                     ▼
      EfficientNet-B0 Attribute Predictor
                     │
                     ▼
     Face Shape Predictor (MediaPipe + XGBoost)
                     │
                     ▼
      Structured Attribute Dictionary
                     │
                     ▼
            Prompt Builder
                     │
                     ▼
         Pollinations AI (Flux)
                     │
                     ▼
             Generated Avatar
```

---

# 🧠 Machine Learning Pipeline

The system predicts:

## Hair

- Hair Color
- Hair Texture
- Bald
- Bangs
- Receding Hairline

## Face

- Face Shape
- High Cheekbones
- Arched Eyebrows
- Bushy Eyebrows
- Big Nose
- Big Lips

## Accessories

- Glasses
- Earrings
- Hat

## Facial Hair

- Mustache
- Goatee
- Sideburns

---

# 🛠 Tech Stack

## Backend

- FastAPI
- PyTorch
- OpenCV
- MediaPipe
- XGBoost
- NumPy

## Frontend

- React
- Vite
- Tailwind CSS

## AI Models

- EfficientNet-B0
- Pollinations AI (Flux)

---

# 📊 Model Performance

## Hair Color Classification

- Overall Accuracy: **\~74%**
- CPU Inference: **\~60--120 ms**

![Hair Confusion Matrix](README_assets/hair_color_confusion_matrix.png)

![Normalized Matrix](README_assets/hair_color_confusion_matrix_normalized.png)

### Binary Attribute Performance

![Binary F1 Scores](README_assets/binary_f1_scores.png)

Highlights: - Glasses ≈ 0.95 F1 - High Cheekbones ≈ 0.84 F1 - Hat ≈ 0.83
F1 - Bangs ≈ 0.82 F1

### Threshold Optimization

![Threshold Optimization](README_assets/threshold_improvement.png)

Threshold tuning improved several attributes, especially: - Bald -
Receding Hairline - Sideburns - Mustache

---

# 🖼 Example Results

<table>
<tr>
<td align="center"><b>Input</b></td>
<td align="center"><b>Output</b></td>
</tr>

<tr>
<td><img src="README_assets/input-1.jpg" width="300"></td>
<td><img src="README_assets/output-1.png" width="300"></td>
</tr>

<tr>
<td><img src="README_assets/input-2.jpg" width="300"></td>
<td><img src="README_assets/output-2.png" width="300"></td>
</tr>

<tr>
<td><img src="README_assets/input-3.jpg" width="300"></td>
<td><img src="README_assets/output-3.png" width="300"></td>
</tr>

<tr>
<td><img src="README_assets/input-4.jpg" width="300"></td>
<td><img src="README_assets/output-4.png" width="300"></td>
</tr
</table>

**Design Goal**

The generated avatar intentionally **does not preserve identity**.

Instead, the system preserves semantic facial attributes while
generating a new artistic character.

---

# 📁 Project Structure

```text
backend/
│
├── ai_generator.py
├── inference.py
├── predict.py
├── prompt_builder.py
├── face_shape_predictor.py
├── style_profiles.py
├── labels.py
├── config.py
│
frontend/
│
├── components/
├── pages/
├── services/
```

---

# 🚀 API

## POST /generate

### Request

- multipart/form-data
- image
- style

### Response

```json
{
  "success": true,
  "prediction": {},
  "prompt": "...",
  "image_url": "...",
  "style": "ghibli"
}
```

---

# 💻 Local Setup

```bash
git clone <repository-url>

cd avatar-app

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

---

# 📈 Development Journey

Pixel Perfect evolved from an experimental research prototype into a
modular production-style AI application.

Major engineering improvements include:

- Refactored a legacy notebook-based codebase into a clean FastAPI
  backend.
- Consolidated the inference pipeline to **PyTorch**, removing
  TensorFlow dependencies.
- Redesigned the hair attribute model using a multi-head
  EfficientNet-B0 architecture.
- Integrated a MediaPipe + XGBoost face shape predictor into the
  production pipeline.
- Added threshold optimization for binary attributes.
- Built a modular prompt generation system.
- Developed a responsive React frontend with multiple artistic styles.
- Improved maintainability through modular architecture and reusable
  components.

---

# 🔮 Future Improvements

- Hair Length Prediction
- Gender Classification
- Age Prediction
- Additional artistic styles
- Improved prompt engineering
- Alternative image generation backends
- Batch generation
- Performance optimization

---

# ⭐ What Makes Pixel Perfect Different?

Most avatar generators directly transform an image into artwork.

Pixel Perfect instead separates **computer vision** from **image
generation**.

The application first predicts semantic facial attributes using deep
learning, converts them into structured natural language descriptions,
and finally generates artwork using a generative AI model.

This modular architecture allows individual models (hair, face shape,
gender, age, etc.) to be upgraded independently without changing the
overall pipeline.

---

## License

This project was developed for educational and portfolio purposes.
