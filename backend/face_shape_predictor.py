import logging
import pickle
import cv2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    FACE_SHAPE_MODEL_PATH,
    FACE_SHAPE_ENCODER_PATH,
    FACE_LANDMARKER_PATH,
    CONFIDENCE_DECIMALS,
)


logger = logging.getLogger(__name__)

IMPORTANT_POINTS = [
    10,
    152,
    234,
    454,
    93,
    323,
    58,
    288,
    103,
    332,
    172,
    397,
]

JAW_CURVATURE_POINTS = (
    58,
    172,
    136,
    150,
    149,
    176,
    148,
    152,
)


EMPTY_FACE_SHAPE = {
    "label": None,
    "confidence": 0.0,
}


class FaceShapePredictor:

    def __init__(self):
        logger.info("Initializing Face Shape Predictor...")

        self.pipeline = self._load_pipeline()
        self.encoder = self._load_encoder()
        self.detector = self._create_detector()

        logger.info("Face Shape Predictor initialized.")


    def _load_pipeline(self):
        logger.info("Loading face shape pipeline...")
        with open(FACE_SHAPE_MODEL_PATH, "rb") as f:
            pipeline = pickle.load(f)
        return pipeline
    
    
    def _load_encoder(self):
        logger.info("Loading face shape encoder...")

        with open(FACE_SHAPE_ENCODER_PATH, "rb") as f:
            encoder = pickle.load(f)

        return encoder
    

    def _create_detector(self):

        base_options = python.BaseOptions(
            model_asset_path=str(FACE_LANDMARKER_PATH)
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
        )

        return vision.FaceLandmarker.create_from_options(options)
    

    def _extract_landmarks(self, image_path: str):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        result = self.detector.detect(mp_image)

        if not result.face_landmarks:
            return None

        landmarks = np.array([
            [lm.x, lm.y, lm.z]
            for lm in result.face_landmarks[0]
        ])

        return landmarks
    

    def _extract_landmarks(
        self,
        image_path: str,
    ) -> np.ndarray | None:

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        result = self.detector.detect(mp_image)

        if not result.face_landmarks:
            logger.warning("No face detected.")

            return None

        landmarks = np.array([
            [lm.x, lm.y, lm.z]
            for lm in result.face_landmarks[0]
        ])

        return landmarks
    

    def _normalize_landmarks(
        self,
        landmarks: np.ndarray,
    ) -> np.ndarray:

        points = landmarks[:, :2].copy()

        center = points[1]

        points -= center

        scale = np.linalg.norm(
            points[10] - points[152]
        )

        return points / (scale + 1e-6)
    

    def _build_landmark_features(
        self,
        landmarks: np.ndarray,
    ) -> np.ndarray:

        return landmarks[
            IMPORTANT_POINTS
        ].flatten()
    

    def _build_geometry_features(
        self,
        landmarks: np.ndarray,
    ) -> np.ndarray:

        def distance(a, b):
            return np.linalg.norm(
                landmarks[a] - landmarks[b]
            )

        face_width = distance(234, 454)

        face_height = distance(10, 152)

        cheekbone_width = distance(93, 323)

        jaw_width = distance(58, 288)

        forehead_width = distance(103, 332)

        return np.array([
            face_width,
            face_height,
            cheekbone_width,
            jaw_width,
            forehead_width,

            face_width / face_height,

            cheekbone_width / face_height,

            jaw_width / face_height,

            forehead_width / face_height,

            jaw_width / cheekbone_width,

            forehead_width / jaw_width,
        ])
    
    def _cosine_angle(
        self,
        p1: np.ndarray,
        p2: np.ndarray,
        p3: np.ndarray,
    ) -> float:

        v1 = p1 - p2
        v2 = p3 - p2

        denominator = (
            np.linalg.norm(v1)
            * np.linalg.norm(v2)
            + 1e-6
        )

        return float(
            np.dot(v1, v2) / denominator
        )
    
    def _build_curvature_features(
        self,
        landmarks: np.ndarray,
    ) -> np.ndarray:

        features = []

        for i in range(len(JAW_CURVATURE_POINTS) - 2):

            p1 = landmarks[JAW_CURVATURE_POINTS[i]]
            p2 = landmarks[JAW_CURVATURE_POINTS[i + 1]]
            p3 = landmarks[JAW_CURVATURE_POINTS[i + 2]]

            features.append(
                self._cosine_angle(
                    p1,
                    p2,
                    p3,
                )
            )

        return np.asarray(features, dtype=np.float32)
    
    def _build_feature_vector(
        self,
        landmarks: np.ndarray,
    ) -> np.ndarray:

        normalized = self._normalize_landmarks(
            landmarks
        )

        landmark_features = (
            self._build_landmark_features(
                normalized
            )
        )

        geometry_features = (
            self._build_geometry_features(
                normalized
            )
        )

        curvature_features = (
            self._build_curvature_features(
                normalized
            )
        )

        features = np.concatenate(
            (
                landmark_features,
                geometry_features,
                curvature_features,
            )
        )

        return features.reshape(1, -1)
    

    def _predict(
        self,
        features: np.ndarray,
    ) -> dict:
        probabilities = self.pipeline.predict_proba(features)[0]
        index = int(np.argmax(probabilities))
        confidence = float(probabilities[index])
        label = self.encoder.inverse_transform([index])[0]
        return {
            "label": str(label),
            "confidence": round(
                confidence,
                CONFIDENCE_DECIMALS,
            ),
        }

    def predict(
        self,
        image_path: str,
    ) -> dict:

        landmarks = self._extract_landmarks(
            image_path
        )

        if landmarks is None:

            return EMPTY_FACE_SHAPE.copy()

        features = self._build_feature_vector(
            landmarks
        )

        logger.info(
            "Face shape feature vector shape: %s",
            features.shape,
        )

        return self._predict(features)
    
