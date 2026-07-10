import albumentations as A
from albumentations.pytorch import ToTensorV2

from config import (
    IMAGE_SIZE,
    MEAN,
    STD,
)

def get_eval_transform():

    return A.Compose([
        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE,
        ),

        A.Normalize(
            mean=MEAN,
            std=STD,
        ),

        ToTensorV2(),
    ])
