from urllib.parse import quote


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_prompt(pred, style="ghibli"):

    # ── STYLE CONTROL ─────────────────────────────────────────────
    STYLE_PREFIX = {
        "ghibli": "Studio Ghibli anime style portrait of",
        "minecraft": "Minecraft game art style blocky pixel portrait of",
        "cinematic": "cinematic realistic portrait of",
        "oil": "oil painting style portrait of",
    }

    # ── FACE SHAPE ────────────────────────────────────────────────
    FACE = {
        "round":   "round soft face",
        "oval":    "oval balanced face",
        "square":  "square strong jaw",
        "heart":   "heart-shaped face",
        "diamond": "sharp defined cheekbones",
        "unknown": "natural face shape",
    }

    # ── EMOTION ───────────────────────────────────────────────────
    EMOTION = {
        "happy":     "gentle smile",
        "big smile": "bright open smile showing teeth",
        "neutral":   "calm serene expression",
        "sad":       "soft melancholy expression",
        "angry":     "intense focused expression",
        "surprise":  "wide-eyed surprised expression",
    }

    # ── AGE ───────────────────────────────────────────────────────
    AGE = {
        "child": "young child",
        "teen":  "youthful teenager",
        "adult": "young adult",
        "old":   "elderly person",
    }

    # ── GENDER ────────────────────────────────────────────────────
    GENDER = {
        "man":     "person with masculine features",
        "woman":   "person with feminine features",
        "unknown": "person",
    }

    # ── SKIN ──────────────────────────────────────────────────────
    def hex_to_skin_desc(hex_color):
        try:
            hx = hex_color.lstrip("#")
            r = int(hx[0:2], 16)
            g = int(hx[2:4], 16)
            b = int(hx[4:6], 16)
            brightness = (r + g + b) / 3

            if brightness > 215: return "very pale porcelain skin, cool fair complexion"
            elif brightness > 190: return "pale fair skin, light cool undertone"
            elif brightness > 165: return "light beige skin, fair warm complexion"
            elif brightness > 130: return "medium olive skin, warm neutral undertone"
            elif brightness > 95:  return "tan brown skin, warm brown complexion"
            elif brightness > 60:  return "deep brown skin, rich melanin"
            else:                  return "very dark brown skin, deep melanin complexion"
        except:
            return "natural skin tone"

    # ── VALUES ─────────────────────────────────────────────────────
    age  = pred.get("age", "adult")
    hair = pred.get("hair", "natural")
    skin = hex_to_skin_desc(pred.get("skin_color", "#c68642"))
    face = FACE.get(pred.get("face_shape"), "natural face shape")
    emo  = EMOTION.get(pred.get("emotion"), "calm serene expression")

    if age == "child":
        gender_str = "small child with childlike facial proportions"
    else:
        gender_str = GENDER.get(pred.get("gender"), "person")

    age_str = AGE.get(age, "young adult")

    # ── GREY HAIR ─────────────────────────────────────────────────
    is_grey = pred.get("grey_hair", False) or (age == "old")
    color   = "grey " if is_grey else ""

    # ── HAIR ──────────────────────────────────────────────────────
    side_var = pred.get("side_var", 500)

    if hair == "bald":
        hair_str = "bald head, no hair"
    elif hair == "flat":
        hair_str = f"{color}hair neatly pulled back"
    elif hair == "short":
        hair_str = f"short {color}hair"
    elif hair == "long":
        if side_var > 350:
            hair_str = f"long wavy {color}hair"
        else:
            hair_str = f"long sleek straight {color}hair, not wavy"
    elif hair == "curly":
        hair_str = f"voluminous curly {color}hair"
    else:
        hair_str = f"natural {color}hair"

    beard_str = "with short beard, " if pred.get("has_beard") else ""

    # ── STYLE PREFIX ──────────────────────────────────────────────
    style_prefix = STYLE_PREFIX.get(style, STYLE_PREFIX["ghibli"])

        # ── STYLE DETAIL BOOST (SAFE ADDITION) ────────────────────────
    style_extra = ""

    if style == "minecraft":
        mc_model = "Alex slim model" if pred.get("gender") == "woman" else "Steve default model"
        style_extra = f"Minecraft {mc_model}, blocky square face, pixel art texture, 16x16 block aesthetic, flat shading, no gradients"

    elif style == "cinematic":
        style_extra = "8K cinematic, shallow depth of field, film grain, dramatic rim lighting, photorealistic skin pores"

    elif style == "oil":
        style_extra = "thick impasto brush strokes, canvas grain, Rembrandt lighting, rich oil paint texture, painterly edges"

    

    # ── FINAL PROMPT ──────────────────────────────────────────────
    prompt = (
        f"{style_prefix} a {gender_str}, "
        f"{skin}, accurate skin color no warm filter, "
        f"{face}, {emo}, {age_str}, "
        f"{beard_str}"
        f"with {hair_str}, "
        f"{style_extra},"
        f"soft natural lighting, centered portrait, simple clean background, "
        f"detailed face, high quality"
    )

    return prompt


# ─────────────────────────────────────────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_ai_avatar(pred, style="ghibli"):

    final_prompt = build_prompt(pred, style=style)
    final_prompt = final_prompt.replace("\n", " ").strip()
    final_prompt = final_prompt[:300]

    from urllib.parse import quote
    encoded = quote(final_prompt, safe="")

    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?model=flux&width=512&height=512&seed=42&nologo=true&enhance=false"
    )