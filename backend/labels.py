import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

from config import (
    THRESHOLD_PATH,
    DEFAULT_BINARY_THRESHOLD,
)

HAIR_COLOR_LABELS = {
    0: "Black",
    1: "Brown",
    2: "Blond",
    3: "Gray",
    4: "Other",
}

HAIR_TEXTURE_LABELS = {
    0: "Straight",
    1: "Wavy",
}

BINARY_ATTRIBUTES = [
    "bald",
    "bangs",
    "receding_hairline",
    "mustache",
    "goatee",
    "sideburns",
    "glasses",
    "hat",
    "earrings",
    "oval_face",
    "high_cheekbones",
    "arched_eyebrows",
    "bushy_eyebrows",
    "big_nose",
    "big_lips",
]

ATTRIBUTE_GROUPS = {
    "hair": [
        "bald",
        "bangs",
        "receding_hairline",
    ],
    "facial_hair": [
        "mustache",
        "goatee",
        "sideburns",
    ],
    "accessories": [
        "glasses",
        "hat",
        "earrings",
    ],
    "face": [
        "oval_face",
        "high_cheekbones",
        "arched_eyebrows",
        "bushy_eyebrows",
        "big_nose",
        "big_lips",
    ],
}


def load_thresholds():

    default_thresholds = {
        attribute: DEFAULT_BINARY_THRESHOLD
        for attribute in BINARY_ATTRIBUTES
    }

    if not THRESHOLD_PATH.exists():
        logger.warning(
            "Threshold file '%s' not found. Using default thresholds.",
            THRESHOLD_PATH.name,
        )
        return default_thresholds

    try:
        with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
            thresholds = json.load(f)

        # Ensure every attribute has a threshold
        for attribute in BINARY_ATTRIBUTES:
            thresholds.setdefault(
                attribute,
                DEFAULT_BINARY_THRESHOLD,
            )

        logger.info(
            "Loaded optimized thresholds from '%s'.",
            THRESHOLD_PATH.name,
        )

        return thresholds

    except (json.JSONDecodeError, OSError):
        logger.exception(
            "Failed to load threshold file '%s'. Falling back to default thresholds.",
            THRESHOLD_PATH.name,
        )

        return default_thresholds