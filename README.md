# Pixel Perfect

A production-oriented Computer Vision system that predicts facial attributes from a single image using Multi-Task Deep Learning and generates identity-aware AI avatars.

Unlike prompt-only avatar generators, this project focuses on extracting meaningful facial attributes first, making avatar generation significantly more consistent and interpretable.

---

## Motivation

Traditional AI avatar generators rely primarily on prompt engineering, which often fails to preserve a person's identity.

This project takes a different approach.

Instead of generating avatars directly from text prompts, it first predicts structured facial attributes using a multi-task computer vision model. These attributes become an interpretable intermediate representation that can be used by multiple downstream avatar generation systems.

This architecture significantly improves consistency while making the system easier to evaluate, debug, and extend.

## Features

- Multi-task EfficientNet Attribute Recognition
- Hair Color Classification
- Hair Texture Classification
- 15 Facial Binary Attribute Predictions
- Automatic Threshold Optimization
- Production-grade Evaluation Pipeline
- FastAPI Backend
- AI Avatar Generation
- Modular Architecture
- Deployment Ready

---

## Project Pipeline

Input Image

↓

Face Attribute Recognition

↓

Structured Attribute Dictionary

↓

Avatar Prompt Generation

↓

AI Avatar Generation

---

## Current Attributes

### Hair Color

- Black
- Brown
- Blond
- Gray
- Other

### Hair Texture

- Straight
- Wavy

### Binary Attributes

Hair

- Bald
- Bangs
- Receding Hairline

Facial Hair

- Mustache
- Goatee
- Sideburns

Accessories

- Glasses
- Hat
- Earrings

Face Features

- Oval Face
- High Cheekbones
- Arched Eyebrows
- Bushy Eyebrows
- Big Nose
- Big Lips

---

## Model Architecture

Backbone

EfficientNet-B0

Prediction Heads

Hair Color Head

Hair Texture Head

Binary Attribute Head

Training

- Transfer Learning
- Mixed Precision Training
- AdamW Optimizer
- Cosine Annealing LR
- Early Stopping
- Checkpointing

---

## Dataset

CelebA Dataset

Custom preprocessing pipeline

Custom train/validation/test splits

Automatic label generation

---

## Evaluation

Hair Color Accuracy

74.09%

Hair Texture Accuracy

92%

Binary Attribute F1

≈69%

Threshold Optimization

Per-attribute threshold calibration improved multiple binary attributes without retraining.

---

## Technologies

Python

PyTorch

FastAPI

OpenCV

MediaPipe

Albumentations

NumPy

Pandas

Scikit-Learn

Matplotlib

---

## Engineering Decisions

- Replaced prompt-first pipeline with attribute-first architecture.
- Built a multi-task EfficientNet model instead of separate classifiers.
- Used transfer learning with staged fine-tuning.
- Added mixed precision training.
- Implemented early stopping and checkpointing.
- Built a complete evaluation pipeline before deployment.
- Used per-attribute threshold optimization instead of unnecessary retraining.
- Designed the backend around modular inference rather than monolithic prediction code.

## Folder Structure

backend/

frontend/

training/

evaluation/

models/

assets/

---

## Future Roadmap

- Integrate Face Shape into the Multi-Task Network
- Add Hair Length Prediction
- Add Curly Hair Classification
- Add Hair Volume Prediction
- ONNX Export
- Docker Deployment
- Cloud Inference API

---

## Author

Manish Kumar

B.Tech Computer Science Engineering

Computer Vision | Deep Learning | Backend Engineering
