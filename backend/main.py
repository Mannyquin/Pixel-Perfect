from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import requests

from predict import predict_all
from ai_generator import generate_ai_avatar

app = FastAPI(title="Avatar Generation App")


# ─────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# NORMALIZE FEATURES (SAFE FALLBACK)
# ─────────────────────────────────────────────────────────────
def normalize_features(pred):
    return {
        "emotion":    pred.get("emotion",    "neutral").lower(),
        "gender":     pred.get("gender",     "unknown").lower(),
        "hair":       pred.get("hair",       "unknown").lower(),
        "age":        str(pred.get("age",    "adult")).lower(),
        "face_shape": pred.get("face_shape", "unknown").lower(),
        "skin_color": pred.get("skin_color", "#c68642"),
        "has_beard":  bool(pred.get("has_beard", False)),
        "grey_hair":  bool(pred.get("grey_hair", False)),
        "side_var":   float(pred.get("side_var", 500.0)),
    }


# ─────────────────────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Avatar API is running"}


@app.get("/ping")
def ping():
    return {"message": "pong"}


# ─────────────────────────────────────────────────────────────
# IMAGE PROXY
# ─────────────────────────────────────────────────────────────
@app.get("/proxy-image")
def proxy_image(url: str):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "image/*"}

    for attempt in range(2):
        try:
            res = requests.get(url, headers=headers, timeout=30)

            if res.status_code == 200:
                return Response(content=res.content, media_type="image/png")

            print(f"⚠️ Proxy attempt {attempt + 1}: status {res.status_code}")

        except requests.exceptions.ReadTimeout:
            print(f"⏱️ Proxy timeout attempt {attempt + 1}/2")

        except Exception as e:
            print(f"⚠️ Proxy error attempt {attempt + 1}: {e}")

    raise HTTPException(status_code=504, detail="Pollinations timed out")


# ─────────────────────────────────────────────────────────────
# MAIN ENDPOINT (FIXED WITH STYLE SUPPORT)
# ─────────────────────────────────────────────────────────────
@app.post("/generate")
async def generate_avatar(
    file: UploadFile = File(...),
    style: str = "ghibli"   # ✅ ADDED
):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG supported")

    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Max size 10MB")

    tmp_path = None

    try:
        # ── Save temp file ─────────────────────────────
        suffix = ".jpg" if file.content_type == "image/jpeg" else ".png"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        print(f"✅ Saved to {tmp_path}")

        # ── Predict ───────────────────────────────────
        try:
            result = predict_all(tmp_path)
            print(f"✅ predict_all: {result}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[PREDICT ERROR] {e}")

        # ── Parse features ────────────────────────────
        try:
            if "features" in result:
                features = result["features"]
                prompt   = result.get("prompt")
            else:
                features = normalize_features(result)
                prompt   = None

            print(f"✅ Features: {features}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[FEATURE PARSE ERROR] {e}")

        # ── Generate avatar  ───────────
        try:
            avatar_url = generate_ai_avatar(
                features,
                style=style   
            )
            print(f"✅ Avatar URL: {avatar_url}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"[AVATAR ERROR] {e}")

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[FILE ERROR] {e}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    return {
        "success": True,
        "avatar_url": avatar_url,
        "features": features,
        "prompt": prompt,
        "style": style,  
    }

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")