from pathlib import Path
import torch
import random


# file paths

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

ATTRIBUTE_MODEL_FILENAME = "avatar_attribute_model.pth"

THRESHOLD_FILENAME = "thresholds.json"

FACE_SHAPE_MODEL_PATH = MODEL_DIR / "face_shape_model.pkl"

FACE_SHAPE_ENCODER_PATH = MODEL_DIR / "face_shape_encoder.pkl"

FACE_LANDMARKER_PATH = MODEL_DIR / "face_landmarker.task"

FACE_SHAPE_THRESHOLD = 0.45

CHECKPOINT_PATH = MODEL_DIR / ATTRIBUTE_MODEL_FILENAME

THRESHOLD_PATH = MODEL_DIR / THRESHOLD_FILENAME




# Model info

MODEL_NAME = "efficientnet_b0"
MODEL_VERSION = "2.0.0"


# Device

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")



# IMG preprocessing

IMAGE_SIZE = 224

MEAN = (0.485, 0.456, 0.406)

STD = (0.229, 0.224, 0.225)


# Model outputs

NUM_HAIR_COLOR = 5

NUM_HAIR_TEXTURE = 2

NUM_BINARY = 15


# Network Architecture

HIDDEN_COLOR = 256

HIDDEN_TEXTURE = 128

HIDDEN_BINARY = 512


# Inference

DEFAULT_BINARY_THRESHOLD = 0.50

PROMPT_CONFIDENCE_THRESHOLD = 0.55

CONFIDENCE_DECIMALS = 4

DROPOUT = 0.3


# Avatar Generation Configuration

DEFAULT_STYLE = "ghibli"

SUPPORTED_STYLES = (
    "ghibli",
    "minecraft",
    "cinematic",
    "oil",
)
DEFAULT_IMAGE_SIZE = 512

DEFAULT_SEED = 42

POLLINATIONS_MODEL = "flux"

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"


# API 
MAX_UPLOAD_SIZE_MB = 10

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
}


# Randomness
RANDOM_SEED = random.randint(1, 99999999)