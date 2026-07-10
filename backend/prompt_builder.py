from config import (
    DEFAULT_STYLE,
    PROMPT_CONFIDENCE_THRESHOLD,
)

from prompt_result import PromptResult
from prompt_templates import (
    DEFAULT_SUBJECT,
    HAIR_COLOR,
    HAIR_TEXTURE,
    FACE_SHAPES,
    FACE_FEATURES,
    ACCESSORIES,
    FACIAL_HAIR,
)

from style_profiles import STYLE_PROFILES


class PromptBuilder:
    def __init__(self):

        self.style_profiles = STYLE_PROFILES

    # ==========================================================
    # Public API
    # ==========================================================

    def build(
        self,
        prediction: dict,
        style: str = DEFAULT_STYLE,
    ) -> PromptResult:

        descriptors = self._build_descriptors(
            prediction
        )

        return self._finalize(
            descriptors,
            style,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _is_confident(
        self,
        prediction: dict,
    ) -> bool:

        return (
            prediction["confidence"]
            >= PROMPT_CONFIDENCE_THRESHOLD
        )

    def _join_items(
        self,
        items: list[str],
    ) -> str:

        if not items:
            return ""

        if len(items) == 1:
            return items[0]

        if len(items) == 2:
            return (
                f"{items[0]} and {items[1]}"
            )

        return (
            ", ".join(items[:-1])
            + f", and {items[-1]}"
        )

    # ==========================================================
    # Descriptor Builder
    # ==========================================================

    def _build_descriptors(
        self,
        prediction: dict,
    ) -> list[str]:

        return [
            descriptor
            for descriptor in (
                self._build_hair(prediction["hair"]),
                self._build_face(prediction["face"]),
                self._build_accessories(prediction["accessories"]),
                self._build_facial_hair(prediction["facial_hair"]),
            )
            if descriptor
        ]
    
    # ==========================================================
    # Hair        
    # ==========================================================

    def _build_hair(
        self,
        hair: dict,
    ) -> str | None:

        if (
            hair["bald"]["value"]
            and self._is_confident(hair["bald"])
        ):
            return "a completely bald head"

        color = None
        texture = None

        if (
            self._is_confident(hair["color"])
            and hair["color"]["label"] in HAIR_COLOR
        ):
            color = HAIR_COLOR[hair["color"]["label"]]

        if (
            self._is_confident(hair["texture"])
            and hair["texture"]["label"] in HAIR_TEXTURE
        ):
            texture = HAIR_TEXTURE[hair["texture"]["label"]]

        parts = []

        if texture:
            parts.append(f"soft {texture}")

        if color:
            parts.append(color)

        parts.append("hair")

        if len(parts) == 1:
            return None

        sentence = " ".join(parts)

        if (
            hair["bangs"]["value"]
            and self._is_confident(hair["bangs"])
        ):
            sentence += " with soft bangs"

        if (
            hair["receding_hairline"]["value"]
            and self._is_confident(hair["receding_hairline"])
        ):
            sentence = "slightly receding " + sentence

        return sentence
    
    # ==========================================================
    # Face
    # ==========================================================

    def _build_face(
        self,
        face: dict,
    ) -> str | None:

        face_description = None

        shape = face.get("shape")

        if (
            shape
            and shape["label"]
            and shape["label"] in FACE_SHAPES
        ):
            face_description = FACE_SHAPES[
                shape["label"]
            ]

        details = []

        for key in (
            "high_cheekbones",
            "arched_eyebrows",
            "bushy_eyebrows",
            "big_nose",
            "big_lips",
        ):
            if (
                face[key]["value"]
                and self._is_confident(face[key])
            ):
                details.append(
                    FACE_FEATURES[key]
                )

        if face_description and details:
            return (
                face_description
                + " with "
                + self._join_items(details)
            )

        if face_description:
            return face_description

        if details:
            return self._join_items(details)

        return None
    
    # ==========================================================
    # Accessories
    # ==========================================================

    def _build_accessories(
        self,
        accessories: dict,
    ) -> str | None:

        items = []

        for key, value in ACCESSORIES.items():

            if (
                accessories[key]["value"]
                and self._is_confident(accessories[key])
            ):
                items.append(value)

        if not items:
            return None

        return f"wearing {self._join_items(items)}"


    # ==========================================================
    # Facial Hair
    # ==========================================================

    def _build_facial_hair(
        self,
        facial_hair: dict,
    ) -> str | None:

        items = []

        for key, value in FACIAL_HAIR.items():

            if (
                facial_hair[key]["value"]
                and self._is_confident(facial_hair[key])
            ):
                items.append(value)

        if not items:
            return None

        return f"with {self._join_items(items)}"
        


    # ==========================================================
    # Final Prompt
    # ==========================================================

    def _finalize(
        self,
        descriptors: list[str],
        style: str,
    ) -> PromptResult:

        if style not in self.style_profiles:
            style = DEFAULT_STYLE

        profile = self.style_profiles[style]

        descriptors = [
        descriptor.strip()
        for descriptor in descriptors
        if descriptor
        ]

        subject = (
            f"{DEFAULT_SUBJECT} with {', '.join(descriptors)}"
            if descriptors
            else DEFAULT_SUBJECT
        )

        prompt = (
        f"{profile['prefix']} "
        f"{subject}, "
        f"{profile['lighting']}, "
        f"{profile['rendering']}, "
        f"{profile['quality']}."
        )   

        prompt = " ".join(prompt.split())

        return PromptResult(
            prompt=prompt,
            descriptors=descriptors,
            style=style,
        )