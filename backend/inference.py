import cv2
import torch
import logging
import numpy as np
import time

from config import (
    DEVICE,
    CHECKPOINT_PATH,
    MODEL_VERSION,
    CONFIDENCE_DECIMALS,
)

from model import AvatarAttributeModel
from face_shape_predictor import FaceShapePredictor

from transforms import get_eval_transform

from labels import (
    HAIR_COLOR_LABELS,
    HAIR_TEXTURE_LABELS,
    BINARY_ATTRIBUTES,
    ATTRIBUTE_GROUPS,
    load_thresholds,
)

logger = logging.getLogger(__name__)


class AttributePredictor:

    def __init__(self):
        logger.info("Initializing Attribute Predictor...")
        self.model = self._load_model()
        self.transform = get_eval_transform()
        self.thresholds = load_thresholds()
        logger.info("Attribute Predictor initialized successfully.")
        self.face_shape_predictor = FaceShapePredictor()

    

    def _load_model(self) -> AvatarAttributeModel:

        logger.info("Loading attribute recognition model...")

        try:
            model = AvatarAttributeModel()

            checkpoint = torch.load(
                CHECKPOINT_PATH,
                map_location=DEVICE,
                weights_only=True,
            )

            # Support both training and deployment checkpoints
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint

            model.load_state_dict(state_dict)

            model.to(DEVICE)
            model.eval()

            logger.info(
                "Model loaded successfully from '%s' on %s.",
                CHECKPOINT_PATH.name,
                DEVICE,
            )

            return model

        except FileNotFoundError:
            logger.exception(
                "Checkpoint '%s' was not found.",
                CHECKPOINT_PATH,
            )
            raise

        except RuntimeError:
            logger.exception(
                "Checkpoint is incompatible with the current model architecture."
            )
            raise

        except Exception:
            logger.exception(
                "Unexpected error while loading the model."
            )
            raise



    def _preprocess(
        self,
        image_path: str,
    ) -> torch.Tensor:
    
        image = cv2.imread(image_path)
    
        if image is None:
            logger.error(
                "Unable to read image '%s'.",
                image_path,
            )
            raise FileNotFoundError(image_path)
    
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )
    
        image = self.transform(
            image=image
        )["image"]
    
        image = image.unsqueeze(0)
    
        image = image.to(DEVICE)
    
        return image
    
    
    
    def _forward(
        self,
        image: torch.Tensor,
    ) -> dict[str, torch.Tensor]:

        with torch.no_grad ():
        
            outputs = self.model(image)

        return outputs
    

    
    def _decode_multiclass(
        self,
        logits: torch.Tensor,
        labels: dict[int, str],
    ) -> dict:


        probabilities = torch.softmax(
            logits,
            dim=1,
        )

        confidence, prediction = torch.max(
            probabilities,
            dim=1,
        )

        prediction = prediction.item()

        return {
            "label": labels[prediction],
            "confidence": round(
                confidence.item(),
                CONFIDENCE_DECIMALS,
            ),
        }
    


    def _decode_binary(
        self,
        logits: torch.Tensor,
    ) -> dict:

        probabilities = torch.sigmoid(logits)

        probabilities = (
            probabilities
            .squeeze(0)
            .cpu()
            .numpy()
        )

        decoded = {}

        for attribute, probability in zip(
            BINARY_ATTRIBUTES,
            probabilities,
        ):

            threshold = self.thresholds[attribute]

            decoded[attribute] = {
                "value": bool(probability >= threshold),
                "confidence": round(
                    float(probability),
                    CONFIDENCE_DECIMALS,
                ),
            }

        grouped = {}

        for group, attributes in ATTRIBUTE_GROUPS.items():

            grouped[group] = {}

            for attribute in attributes:

                grouped[group][attribute] = decoded[attribute]

        return grouped



    def _decode(
        self,
        outputs: dict[str, torch.Tensor],
    ) -> dict:

        hair_color = self._decode_multiclass(
            outputs["hair_color"],
            HAIR_COLOR_LABELS,
        )

        hair_texture = self._decode_multiclass(
            outputs["hair_texture"],
            HAIR_TEXTURE_LABELS,
        )

        binary = self._decode_binary(
            outputs["binary"],
        )

        return {
            "hair": {
                "color": hair_color,
                "texture": hair_texture,
                **binary["hair"],
            },
            "facial_hair": binary["facial_hair"],
            "accessories": binary["accessories"],
            "face": binary["face"],
        }

    def predict(
        self,
        image_path: str,
    ) -> dict:
        logger.info(
            "Running inference on '%s'.",
            image_path,
        )

        start = time.perf_counter()

        image = self._preprocess(image_path)

        outputs = self._forward(image)

        prediction = self._decode(outputs)

        prediction["face"]["shape"] = (
            self.face_shape_predictor.predict(image_path)
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        prediction["metadata"] = {
            "model_version": MODEL_VERSION,
            "device": str(DEVICE),
            "inference_time_ms": round(elapsed, 2),
        }

        return prediction