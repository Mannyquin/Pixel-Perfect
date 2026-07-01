FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Backend dependencies ───────────────────────────────────
COPY backend/requirements_deploy.txt .
RUN pip install --no-cache-dir opencv-python-headless==4.9.0.80 && \
    pip install --no-cache-dir -r requirements_deploy.txt && \
    pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null || true

# ── Backend code ───────────────────────────────────────────
COPY backend/ ./backend/

# ── Frontend build ─────────────────────────────────────────
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci

COPY frontend/ ./frontend/

# Build frontend with API pointing to same origin
RUN cd frontend && \
    VITE_API_URL="" \
    VITE_SUPABASE_URL="" \
    VITE_SUPABASE_ANON_KEY="" \
    npm run build

# Move built frontend into backend static folder
RUN mkdir -p ./backend/static && \
    cp -r ./frontend/dist/* ./backend/static/

# ── Expose port ────────────────────────────────────────────
EXPOSE 7860

# ── Start backend ──────────────────────────────────────────
WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]