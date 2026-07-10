import timm
import torch.nn as nn
import torch

from config import (
    MODEL_NAME,
    NUM_HAIR_COLOR,
    NUM_HAIR_TEXTURE,
    NUM_BINARY,
    HIDDEN_COLOR,
    HIDDEN_TEXTURE,
    HIDDEN_BINARY,
)

import timm
import torch.nn as nn

from config import (
    MODEL_NAME,
    NUM_HAIR_COLOR,
    NUM_HAIR_TEXTURE,
    NUM_BINARY,
    HIDDEN_COLOR,
    HIDDEN_TEXTURE,
    HIDDEN_BINARY,
    DROPOUT,
)


def _build_head(input_dim, hidden_dim, output_dim):
    return nn.Sequential(
        nn.Linear(input_dim, hidden_dim),
        nn.BatchNorm1d(hidden_dim),
        nn.ReLU(inplace=True),
        nn.Dropout(DROPOUT),
        nn.Linear(hidden_dim, output_dim),
    ) 


class AvatarAttributeModel(nn.Module):    



    def __init__(self):
        super().__init__()

        # ==========================================================
        # Backbone
        # ==========================================================

        self.backbone = timm.create_model(
            MODEL_NAME,
            pretrained=False,
            num_classes=0,
            global_pool="avg",
        )

        feature_dim = self.backbone.num_features

        # ==========================================================
        # Hair Color Head
        # ==========================================================

        self.hair_color = _build_head(
            feature_dim,
            HIDDEN_COLOR,
            NUM_HAIR_COLOR,
        )

        self.hair_texture = _build_head(
            feature_dim,
            HIDDEN_TEXTURE,
            NUM_HAIR_TEXTURE,
        )

        self.binary = _build_head(
            feature_dim,
            HIDDEN_BINARY,
            NUM_BINARY,
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> dict[str, torch.Tensor]:

        features = self.backbone(x)

        return {
            "hair_color": self.hair_color(features),
            "hair_texture": self.hair_texture(features),
            "binary": self.binary(features),
        }
    
