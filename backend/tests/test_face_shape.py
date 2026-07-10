import sys
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).resolve().parent.parent))

from face_shape_predictor import FaceShapePredictor

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

predictor = FaceShapePredictor()

result = predictor.predict(
    "tests/test_images/person.jpg"
)

print(result)