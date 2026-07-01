import torch
import torch.nn.functional as F
import cv2
import numpy as np
from torchvision import transforms, models

DEVICE = "cpu"

checkpoint  = torch.load("models/hair_model.pth", map_location=DEVICE)
class_names = checkpoint["class_names"]

model = models.mobilenet_v2(weights=None)
model.classifier[1] = torch.nn.Linear(model.last_channel, len(class_names))
model.load_state_dict(checkpoint["model_state_dict"])
model = model.to(DEVICE)  # ✅ FIX
model.eval()

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ─────────────────────────────────────────────────────────────────────────────
# FLAT / PARTIAL TIED DETECTION (Improved but safe)
# ─────────────────────────────────────────────────────────────────────────────
def detect_hair_state(img):
    h, w = img.shape[:2]

    top   = img[0:int(h * 0.18), int(w * 0.20):int(w * 0.80)]
    left  = img[int(h * 0.10):int(h * 0.50), 0:int(w * 0.15)]
    right = img[int(h * 0.10):int(h * 0.50), int(w * 0.85):w]

    def safe_var(crop):
        return 999.0 if crop.size == 0 else float(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).var())

    top_var  = safe_var(top)
    side_var = (safe_var(left) + safe_var(right)) / 2

    print(f"   Hair state → top:{top_var:.1f}, side:{side_var:.1f}")

    # Fully flat
    if top_var < 280 and side_var < 140:
        return "flat"

    # Partially tied (new, but safe)
    if top_var < 280 and side_var > 250:
        return "tied_partial"

    return None


# ─────────────────────────────────────────────────────────────────────────────
# CNN PREDICT (device safe)
# ─────────────────────────────────────────────────────────────────────────────
def cnn_predict(img):
    crop = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if crop.size == 0:
        return "unknown", 0.0

    tensor = transform(crop).unsqueeze(0).to(DEVICE)  # ✅ FIX

    with torch.no_grad():
        output = model(tensor)
        probs  = F.softmax(output, dim=1)
        conf, pred = torch.max(probs, 1)

    return class_names[pred.item()], conf.item()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PREDICT
# ─────────────────────────────────────────────────────────────────────────────
def predict_hair(img):

    # ── 1. Flat / tied detection ─────────────────────────────────────────────
    state = detect_hair_state(img)

    if state == "flat":
        print("   ✅ Flat hair detected")
        return "flat", 1.0

    # ── 2. CNN ───────────────────────────────────────────────────────────────
    label, conf = cnn_predict(img)

    print(f"   CNN → {label} ({conf:.2f})")

    # ── 3. Hair structure analysis ───────────────────────────────────────────
    h, w = img.shape[:2]

    left  = img[int(h * 0.20):int(h * 0.60), 0:int(w * 0.20)]
    right = img[int(h * 0.20):int(h * 0.60), int(w * 0.80):w]
    top   = img[0:int(h * 0.20), int(w * 0.30):int(w * 0.70)]

    def var(x):
        return 0 if x.size == 0 else float(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY).var())

    side_var = (var(left) + var(right)) / 2
    top_var  = var(top)

    print(f"   Structure → top:{top_var:.1f}, side:{side_var:.1f}")

    # ── 4. SAFE CORRECTIONS (minimal, high-impact) ───────────────────────────

    # Curly ↔ Long confusion fix
    if label == "curly" and conf < 0.80:
        if side_var < 400:
            label = "natural"
        elif side_var > 700 and top_var > 600:
            label = "long"

    # Long vs wavy correction
    if label == "long" and side_var > 650:
        label = "curly"

    # Bald misclassification fix
    if label == "bald" and side_var > 250:
        label = "short"

    # Short vs long refinement
    if label == "long" and side_var < 200:
        label = "short"

    # Partial tied handling
    if state == "tied_partial":
        print("   ⚠️ Partial tied detected")
        label = "natural"
        conf  = max(conf, 0.75)

    return label, conf