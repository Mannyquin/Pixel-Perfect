import numpy as np
import pickle
import cv2
import os
from deepface import DeepFace
import tempfile

import mediapipe as mp
from mediapipe.tasks import python as _mp_tasks
from mediapipe.tasks.python import vision as _mp_vision

from ai_generator import build_prompt
from hair_model import predict_hair


# -----------------------------
# PATH SETUP
# -----------------------------
BASE_DIR  = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")


# -----------------------------
# LOAD MODELS
# -----------------------------
face_model   = pickle.load(open(os.path.join(MODEL_DIR, "face_shape_model.pkl"),   "rb"))
face_encoder = pickle.load(open(os.path.join(MODEL_DIR, "face_shape_encoder.pkl"), "rb"))


# -----------------------------
# MEDIAPIPE SETUP
# -----------------------------
_FaceLandmarker        = _mp_vision.FaceLandmarker
_FaceLandmarkerOptions = _mp_vision.FaceLandmarkerOptions
_VisionRunningMode     = _mp_vision.RunningMode

face_landmarker = _FaceLandmarker.create_from_options(
    _FaceLandmarkerOptions(
        base_options=_mp_tasks.BaseOptions(
            model_asset_path=os.path.join(MODEL_DIR, "face_landmarker.task")
        ),
        running_mode=_VisionRunningMode.IMAGE,
        num_faces=1,
    )
)


# ─────────────────────────────────────────────────────────────────────────────
# PREPROCESS
# ─────────────────────────────────────────────────────────────────────────────
def preprocess_image(img):
    img = cv2.resize(img, (640, 640))

    img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(img)

    l = cv2.normalize(l, None, 80, 200, cv2.NORM_MINMAX)

    img = cv2.merge((l, a, b))
    img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# FACE CROP
# ─────────────────────────────────────────────────────────────────────────────
def crop_to_face(img):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    if len(faces) == 0:
        print("⚠️ No face detected for crop — using full image")
        return img

    faces      = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    x, y, w, h = faces[0]

    pad_top    = int(h * 0.6)
    pad_sides  = int(w * 0.15)
    pad_bottom = int(h * 0.2)

    x1 = max(0, x - pad_sides)
    y1 = max(0, y - pad_top)
    x2 = min(img.shape[1], x + w + pad_sides)
    y2 = min(img.shape[0], y + h + pad_bottom)

    cropped = img[y1:y2, x1:x2]
    if cropped.size == 0:
        print("⚠️ Crop resulted in empty image — using full image")
        return img

    print(f"✅ Face cropped: ({x1},{y1}) → ({x2},{y2})")
    return cropped


# ─────────────────────────────────────────────────────────────────────────────
# SKIN TONE DETECTION
# Multi-zone: forehead + both cheeks sampled separately.
# Highlight/shadow pixels excluded by brightness gate (40–220).
# ─────────────────────────────────────────────────────────────────────────────
def detect_skin_tone(img, lm_raw=None):
    h, w = img.shape[:2]
    samples = []

    # ❌ IMPORTANT: NO normalization here anymore (removed double processing)

    # ─────────────────────────────────────────────
    # Landmark-based sampling
    if lm_raw is not None:
        try:
            for point, radius in [(lm_raw[10], 14), (lm_raw[93], 12), (lm_raw[323], 12)]:
                px = int(point[0] * w)
                py = int(point[1] * h)

                patch = img[max(0, py - radius):py + radius,
                            max(0, px - radius):px + radius]

                if patch.size > 0:
                    pixels = patch.reshape(-1, 3).astype(float)
                    brightness = pixels.mean(axis=1)

                    # ✅ FIXED FILTER (balanced for all skin tones)
                    mask = (brightness > 50) & (brightness < 210)

                    if mask.sum() > 5:
                        samples.append(pixels[mask])

        except Exception as e:
            print(f"⚠️ Landmark skin sampling failed: {e}")

    # ─────────────────────────────────────────────
    # Fallback zones
    if not samples:
        for zone in [
            img[int(h * 0.12):int(h * 0.28), int(w * 0.30):int(w * 0.70)],
            img[int(h * 0.42):int(h * 0.58), int(w * 0.18):int(w * 0.38)],
            img[int(h * 0.42):int(h * 0.58), int(w * 0.62):int(w * 0.82)],
        ]:
            if zone.size > 0:
                pixels = zone.reshape(-1, 3).astype(float)
                brightness = pixels.mean(axis=1)

                mask = (brightness > 50) & (brightness < 210)

                if mask.sum() > 5:
                    samples.append(pixels[mask])

    # ─────────────────────────────────────────────
    if not samples:
        return "#c68642"

    all_pixels = np.vstack(samples)

    # ✅ Better than median (reduces shadow bias)
    median_bgr = np.percentile(all_pixels, 60, axis=0)

    brightness = median_bgr.mean()

    # ✅ VERY gentle correction (no color distortion)
    if brightness < 95:
        median_bgr *= 1.08
    elif brightness > 190:
        median_bgr *= 0.97

    median_bgr = np.clip(median_bgr, 0, 255).astype(int)

    b, g, r = median_bgr
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────────────────────
# BEARD DETECTION
# Three-layer gate:
#   1. Hue-similarity — chin hue within 15° of skin → shadow, not beard
#   2. Skin-tier thresholds — dark/medium skin need higher variance to confirm
#   3. Variance + brightness gate
# ─────────────────────────────────────────────────────────────────────────────
def detect_beard(img, lm_raw=None, skin_color=None):
    h, w = img.shape[:2]

    if lm_raw is not None:
        try:
            chin = lm_raw[152]
            ljaw = lm_raw[58]
            rjaw = lm_raw[288]
            cx   = int(chin[0] * w)
            cy   = int(chin[1] * h)
            x1   = max(0, int(ljaw[0] * w))
            x2   = min(w, int(rjaw[0] * w))
            y1   = max(0, cy - 20)
            y2   = min(h, cy + 40)
            chin_crop = img[y1:y2, x1:x2]
        except Exception:
            chin_crop = img[int(h * 0.70):int(h * 0.95), int(w * 0.30):int(w * 0.70)]
    else:
        chin_crop = img[int(h * 0.70):int(h * 0.95), int(w * 0.30):int(w * 0.70)]

    if chin_crop.size == 0:
        return False

    gray            = cv2.cvtColor(chin_crop, cv2.COLOR_BGR2GRAY)
    variance        = gray.var()
    mean_brightness = gray.mean()
    print(f"   Beard region — variance: {variance:.1f}, brightness: {mean_brightness:.1f}")

    # ── Parse skin colour (safe defaults to avoid undefined r/g/b) ────────────
    r_skin = g_skin = b_skin = 128
    avg_brightness = 128
    if skin_color:
        try:
            hx         = skin_color.lstrip("#")
            r_skin     = int(hx[0:2], 16)
            g_skin     = int(hx[2:4], 16)
            b_skin     = int(hx[4:6], 16)
            avg_brightness = (r_skin + g_skin + b_skin) / 3
        except Exception:
            pass

    dark_skin   = avg_brightness < 90
    medium_skin = 90 <= avg_brightness < 140

    # ── Gate 1: hue similarity ────────────────────────────────────────────────
    # Shadow = darkened skin (same hue).  Beard = different hue.
    # If chin hue ≈ skin hue → shadow, return False.
    try:
        chin_hsv = cv2.cvtColor(chin_crop, cv2.COLOR_BGR2HSV)
        chin_hue = float(np.median(chin_hsv[:, :, 0]))

        skin_bgr = np.uint8([[[b_skin, g_skin, r_skin]]])
        skin_hsv = cv2.cvtColor(skin_bgr, cv2.COLOR_BGR2HSV)
        skin_hue = float(skin_hsv[0, 0, 0])

        hue_diff = abs(chin_hue - skin_hue)
        if hue_diff > 90:
            hue_diff = 180 - hue_diff   # OpenCV hue wraps at 180

        print(f"   Hue diff chin/skin: {hue_diff:.1f}°")

        if hue_diff < 15:
            print("⚠️ Chin hue matches skin — likely shadow, not beard")
            return False
    except Exception as e:
        print(f"   ⚠️ Hue gate failed: {e}")

    # ── Gate 2 + 3: skin-tier thresholds + variance/brightness ───────────────
    if dark_skin:
        thr_var, thr_bright = 450, 85
    elif medium_skin:
        thr_var, thr_bright = 320, 108
    else:
        thr_var, thr_bright = 250, 120

    return variance > thr_var and mean_brightness < thr_bright


# ─────────────────────────────────────────────────────────────────────────────
# SMILE / TEETH DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def detect_smile_intensity(img, lm_raw=None):
    h, w = img.shape[:2]

    if lm_raw is not None:
        try:
            upper_lip = lm_raw[13]
            lower_lip = lm_raw[14]
            cx        = int((upper_lip[0] + lower_lip[0]) / 2 * w)
            cy        = int((upper_lip[1] + lower_lip[1]) / 2 * h)
            mouth_crop = img[max(0, cy - 10):min(h, cy + 20),
                             max(0, cx - 30):min(w, cx + 30)]
        except Exception:
            mouth_crop = img[int(h * 0.65):int(h * 0.80), int(w * 0.35):int(w * 0.65)]
    else:
        mouth_crop = img[int(h * 0.65):int(h * 0.80), int(w * 0.35):int(w * 0.65)]

    if mouth_crop.size == 0:
        return False

    gray       = cv2.cvtColor(mouth_crop, cv2.COLOR_BGR2GRAY)
    brightness = gray.mean()
    max_bright = gray.max()
    print(f"   Mouth region — brightness: {brightness:.1f}, max: {max_bright:.1f}")

    return max_bright > 180 and brightness > 100


# ─────────────────────────────────────────────────────────────────────────────
# HAIR SIDE VOLUME DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def detect_hair_sides(img):
    h, w = img.shape[:2]

    left  = img[int(h * 0.15):int(h * 0.55), 0:int(w * 0.18)]
    right = img[int(h * 0.15):int(h * 0.55), int(w * 0.82):w]
    top   = img[0:int(h * 0.18),              int(w * 0.25):int(w * 0.75)]

    def var(crop):
        return 0 if crop.size == 0 else float(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).var())

    # ✅ NEW: normalize against full image variance
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    global_var = gray.var() + 1e-6

    left_var  = var(left) / global_var
    right_var = var(right) / global_var
    top_var   = var(top) / global_var
    side_var  = (left_var + right_var) / 2

    print(f"   Hair variance — top: {top_var:.2f}, sides: {side_var:.2f}")
    return {"top_var": top_var, "side_var": side_var}

# ─────────────────────────────────────────────────────────────────────────────
# GREY HAIR DETECTION  (image-based, not age-based)
# Checks the top-centre hair region for achromatic (grey/white) pixels.
# Works regardless of what DeepFace predicts for age, which skews young
# and routinely puts a 57-year-old in the "adult" bucket.
# ─────────────────────────────────────────────────────────────────────────────
def detect_grey_hair(img):
    h, w        = img.shape[:2]
    hair_region = img[0:int(h * 0.22), int(w * 0.20):int(w * 0.80)]

    if hair_region.size == 0:
        return False

    hsv        = cv2.cvtColor(hair_region, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value      = hsv[:, :, 2]

    # Exclude near-black pixels (shadow) AND near-white pixels (background/highlight)
    # V > 40 excludes dark shadow; V < 210 excludes white walls/backgrounds
    non_black_mask = (value > 40) & (value < 210)
    low_sat_mask = (saturation < 40) & (value > 120) & (value < 210)
    non_black_count = int(np.sum(non_black_mask))

    if non_black_count == 0:
        return False

    grey_ratio = float(np.sum(low_sat_mask)) / non_black_count
    print(f"   Grey hair ratio: {grey_ratio:.2f} ({int(np.sum(low_sat_mask))}/{non_black_count} px)")

    return grey_ratio > 0.35


# ─────────────────────────────────────────────────────────────────────────────
# DEEPFACE  — emotion, age, gender
#
#   • Age thresholds: child <13, teen <20, adult <45, old ≥45  (was 18/25/45)
#   • Child gender forced to "unknown" INSIDE this function, not downstream
#   • happy_score threshold: 65  (was 85 — too strict, missed most smiles)
#   • Hair-gender correction skipped for children
# ─────────────────────────────────────────────────────────────────────────────
def analyze_face(img_path, hair="unknown", img=None, lm_raw=None):
    try:
        result = DeepFace.analyze(
            img_path=img_path,
            actions=["emotion", "age", "gender"],
            enforce_detection=False,
            detector_backend="retinaface"
        )[0]
    except Exception as e:
        print(f"❌ DeepFace failed: {e}")
        return "neutral", "adult", "unknown"

    # ── GENDER ───────────────────────────────────────────────────────────────
    gender_data = result.get("gender", {})
    man_score   = gender_data.get("Man",   0)
    woman_score = gender_data.get("Woman", 0)
    diff        = abs(man_score - woman_score)

    print(f"   Gender scores — Man: {man_score:.1f}, Woman: {woman_score:.1f}, diff: {diff:.1f}")

    gender = "man" if (diff >= 40 and man_score > woman_score) else \
             "woman" if (diff >= 40) else "unknown"

    # Jaw texture gate — smooth jaw → likely woman
    if gender == "man" and diff < 80 and img is not None:
        h, w = img.shape[:2]
        jaw  = img[int(h * 0.6):int(h * 0.8), int(w * 0.2):int(w * 0.8)]
        if jaw.size > 0:
            jaw_var = float(cv2.cvtColor(jaw, cv2.COLOR_BGR2GRAY).var())
            print(f"   Jaw texture variance: {jaw_var:.1f}")
            if jaw_var < 180:
                gender = "unknown"
                print(f"⚠️ Smooth jaw ({jaw_var:.1f}) — downgraded to unknown")

    # ── AGE  (corrected thresholds) ───────────────────────────────────────────
    age_val = result.get("age", 25)
    if   age_val < 13: age = "child"
    elif age_val < 20: age = "teen"
    elif age_val < 45: age = "adult"
    else:              age = "old"
    print(f"   Age: {age_val:.1f} → {age}")

    # Forehead-ratio heuristic: children have large foreheads relative to face
    if age == "teen" and age_val < 22 and img is not None:
        h, w        = img.shape[:2]
        forehead    = img[int(h * 0.05):int(h * 0.25), int(w * 0.25):int(w * 0.75)]
        face_center = img[int(h * 0.25):int(h * 0.75), int(w * 0.25):int(w * 0.75)]
        if forehead.size > 0 and face_center.size > 0:
            f_bright = float(cv2.cvtColor(forehead,    cv2.COLOR_BGR2GRAY).mean())
            c_bright = float(cv2.cvtColor(face_center, cv2.COLOR_BGR2GRAY).mean())
            ratio    = f_bright / (c_bright + 1e-6)
            print(f"   Forehead/face ratio: {ratio:.2f}")
            if ratio > 1.1:
                age = "child"
                print(f"⚠️ Downgraded to child — large forehead ({ratio:.2f})")

    if age == "child":
        gender = "unknown"
        print("⚠️ Child detected — gender forced to unknown")

    # ── EMOTION + TEETH ───────────────────────────────────────────────────────
    emotion        = result.get("dominant_emotion", "neutral")
    emotion_scores = result.get("emotion", {})
    happy_score    = emotion_scores.get("happy", 0)
    print(f"   Emotion: {emotion}, happy score: {happy_score:.1f}")


    # smiles that DeepFace scores at 65-84.
    if emotion == "happy" and img is not None:
        has_teeth = detect_smile_intensity(img, lm_raw=lm_raw)
        if has_teeth and happy_score > 65:
            emotion = "big smile"
            print("✅ Upgraded to big smile — teeth detected")

    # ── HAIR-BASED GENDER CORRECTION (children excluded above) ───────────────
    if age != "child":
        if gender == "man" and hair in ("long", "flat"):
            gender = "woman"
            print(f"⚠️ Gender → woman (hair='{hair}')")
        elif gender == "man" and hair in ("short", "natural") and diff < 70:
            gender = "unknown"
            print(f"⚠️ Low-confidence man (diff={diff:.1f}) + ambiguous hair → unknown")

    return emotion, age, gender


# ─────────────────────────────────────────────────────────────────────────────
# LANDMARK PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
IMPORTANT_POINTS = [10, 152, 234, 454, 93, 323, 58, 288, 103, 332, 172, 397]


def normalize_landmarks(lm):
    lm     = lm.reshape(-1, 3)[:, :2]
    center = lm[1]
    lm     = lm - center
    scale  = np.linalg.norm(lm[10] - lm[152])
    return lm / (scale + 1e-6)


def select_landmarks(lm):
    return lm[IMPORTANT_POINTS].flatten()


def extract_features(lm):
    def d(a, b): return np.linalg.norm(lm[a] - lm[b])
    W = d(234, 454); H = d(10, 152); C = d(93, 323); J = d(58, 288); F = d(103, 332)
    return np.array([W, H, C, J, F, W/H, C/H, J/H, F/H, J/C, F/J])


def curvature_features(lm):
    pts   = [58, 172, 136, 150, 149, 176, 148, 152]
    curve = []
    for i in range(len(pts) - 2):
        v1 = lm[pts[i]]   - lm[pts[i+1]]
        v2 = lm[pts[i+2]] - lm[pts[i+1]]
        cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        curve.append(cos)
    return np.array(curve)


def get_landmarks(img):
    img_rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    result   = face_landmarker.detect(mp_image)
    if not result.face_landmarks:
        return None
    coords = []
    for lm in result.face_landmarks[0]:
        coords.extend([lm.x, lm.y, lm.z])
    return np.array(coords)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def predict_all(img_path):

    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"[CV2 ERROR] Could not read: {img_path}")

    img = preprocess_image(img)
    print("✅ Preprocessed")

    img = crop_to_face(img)
    print(f"✅ Cropped — shape: {img.shape}")

    # Save for DeepFace
    preprocessed_path = img_path
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            cv2.imwrite(tmp.name, img)
            preprocessed_path = tmp.name
    except Exception as e:
        print(f"⚠️ Temp file save failed: {e}")

    # ── Hair ─────────────────────────────────────────────────────────────────

    print("⏳ Hair model...")
    try:
        hair, conf = predict_hair(img)
        print(f"✅ Hair: {hair} ({conf:.2f})")
    except Exception as e:
        print(f"❌ Hair model failed: {e}")
        import traceback; traceback.print_exc()
        hair, conf = "unknown", 0.0

    # Confidence gate

    if hair == "flat":
        curly_needs_confirmation = False
    elif conf < 0.55:
        hair, curly_needs_confirmation = "natural", False
    elif hair == "curly" and conf < 0.80:
        curly_needs_confirmation = True
    else:
        curly_needs_confirmation = False

    # ── Hair side variance ────────────────────────────────────────────────────
    print("⏳ Hair sides...")
    try:
        hair_stats = detect_hair_sides(img)
        top_var    = hair_stats["top_var"]
        side_var   = hair_stats["side_var"]
    except Exception as e:
        print(f"❌ Hair sides failed: {e}")
        top_var, side_var = 500, 500

    # ── Hair key resolution ───────────────────────────────────────────────────
    if hair != "flat":

    # ── Flat detection (normalized)
        if hair != "curly" and conf < 0.75:
            if top_var < 0.6 and side_var < 0.5:
                hair = "flat"
                curly_needs_confirmation = False
                print(f"   Flat confirmed (safe)")

    # ── Low-confidence curly
        elif curly_needs_confirmation:
            if side_var > 1.4 and top_var > 1.2:
                hair = "long"
                print(f"⚠️ Low-conf curly → long")
            elif side_var > 1.2:
                print(f"✅ Curly confirmed by variance")
            else:
                hair = "natural"
                print(f"⚠️ Curly → natural (low variance)")

    # ── High-confidence curly
        elif hair == "curly" and conf >= 0.80:
            if side_var > 1.5 and top_var < 0.9:
                hair = "long"
                print(f"⚠️ Curly → long (spread pattern)")

    # ── Bald correction
        elif hair == "bald" and side_var > 0.9:
            hair = "short"
            print(f"⚠️ Bald → short (variance too high)")

        elif hair == "short":
            if side_var > 2.2 and top_var < 0.65:
                hair = "natural"
                print(f"⚠️ Short → natural (true spread)")
            else:
                print(f"✅ Short preserved")

    # ── Safety fallback
        elif hair not in ("short", "long", "curly", "bald", "flat"):
            hair = "natural"

    print(f"✅ Final hair: {hair} (top={top_var:.1f}, side={side_var:.1f})")

    # ── DeepFace ──────────────────────────────────────────────────────────────
    print("⏳ DeepFace...")
    try:
        emotion, age, gender = analyze_face(
            preprocessed_path, hair=hair, img=img, lm_raw=None
        )
        print(f"✅ DeepFace — emotion:{emotion}  age:{age}  gender:{gender}")
    except Exception as e:
        print(f"❌ DeepFace failed: {e}")
        import traceback; traceback.print_exc()
        emotion, age, gender = "neutral", "adult", "unknown"

    # ── Landmarks, face-shape, skin tone ─────────────────────────────────────
    face_shape  = "unknown"
    skin_color  = "#c68642"
    has_beard   = False
    lm_for_skin = None

    print("⏳ Landmarks...")
    try:
        lm_raw = get_landmarks(img)
        if lm_raw is not None:
            lm_for_skin  = lm_raw.reshape(-1, 3)
            lm_norm      = normalize_landmarks(lm_raw)
            feat_arr     = np.concatenate([
                select_landmarks(lm_norm),
                extract_features(lm_norm),
                curvature_features(lm_norm)
            ]).reshape(1, -1)

            proba     = face_model.predict_proba(feat_arr)[0]
            max_conf  = proba.max()
            top_class = proba.argmax()

            if max_conf > 0.45:
                face_shape = str(face_encoder.inverse_transform([top_class])[0]).lower()
                print(f"✅ Face shape: {face_shape} ({max_conf:.2f})")
            else:
                face_shape = "oval"
                print(f"⚠️ Low shape confidence — defaulting to oval")

            skin_color = detect_skin_tone(img, lm_raw=lm_for_skin)
            print(f"✅ Skin: {skin_color}")

            # Landmark-guided smile re-check
            if emotion == "happy":
                if detect_smile_intensity(img, lm_raw=lm_for_skin):
                    emotion = "big smile"
                    print("✅ Teeth detected via landmarks → big smile")
        else:
            print("⚠️ No landmarks — fallback skin")
            skin_color = detect_skin_tone(img)

    except Exception as e:
        print(f"❌ Landmarks failed: {e}")
        import traceback; traceback.print_exc()
        skin_color = detect_skin_tone(img)

    # ── Beard (men only) ──────────────────────────────────────────────────────
    if gender == "man" and lm_for_skin is not None:
        print("⏳ Beard...")
        try:
            has_beard = detect_beard(img, lm_raw=lm_for_skin, skin_color=skin_color)
            print(f"✅ Beard: {has_beard}")
        except Exception as e:
            print(f"❌ Beard failed: {e}")
            has_beard = False

    # ── Grey hair ─────────────────────────────────────────────────────────────
    print("⏳ Grey hair...")
    try:
        grey_hair = detect_grey_hair(img)
        print(f"✅ Grey hair: {grey_hair}")
    except Exception as e:
        print(f"❌ Grey hair failed: {e}")
        grey_hair = False

    # ── Cleanup ───────────────────────────────────────────────────────────────
    if preprocessed_path != img_path:
        try: os.remove(preprocessed_path)
        except Exception: pass

    # ── Final features ────────────────────────────────────────────────────────
    features = {
        "emotion":    emotion,
        "gender":     gender,
        "hair":       hair,
        "age":        age,
        "face_shape": face_shape,
        "skin_color": skin_color,
        "has_beard":  bool(has_beard),
        "grey_hair":  bool(grey_hair),
        "side_var":   float(side_var),   
    }

    print(f"✅ Final features: {features}")
    return {"features": features, "prompt": build_prompt(features)}