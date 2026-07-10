import logging

from inference import AttributePredictor

logger = logging.getLogger(__name__)

_predictor = AttributePredictor()


def predict_attributes(image_path: str) -> dict:
    return _predictor.predict(image_path)