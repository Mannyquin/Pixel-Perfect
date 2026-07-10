from urllib.parse import quote

from config import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_SEED,
    DEFAULT_STYLE,
    POLLINATIONS_BASE_URL,
    POLLINATIONS_MODEL,
)

from avatar_result import AvatarResult
from prompt_builder import PromptBuilder


class AvatarGenerator:
    def __init__(self):
        self.prompt_builder = PromptBuilder()


    # Public API

    def generate(
        self,
        prediction: dict,
        style: str = DEFAULT_STYLE,
    ) -> AvatarResult:

        prompt_result = self.prompt_builder.build(
            prediction,
            style,
        )

        image_url = self._build_url(
            prompt_result.prompt
        )

        print("AI_GENERATOR STYLE:", repr(style))

        return AvatarResult(
            image_url=image_url,
            prompt=prompt_result,
        )


    # Private Helpers

    def _encode_prompt(
        self,
        prompt: str,
    ) -> str:

        return quote(
            prompt,
            safe="",
        )

    def _build_url(
        self,
        prompt: str,
    ) -> str:

        encoded = self._encode_prompt(prompt)

        return (
            f"{POLLINATIONS_BASE_URL}/{encoded}"
            f"?model={POLLINATIONS_MODEL}"
            f"&width={DEFAULT_IMAGE_SIZE}"
            f"&height={DEFAULT_IMAGE_SIZE}"
            f"&seed={DEFAULT_SEED}"
            f"&nologo=true"
            f"&enhance=false"
        )



# Singleton
_generator = AvatarGenerator()



def generate_avatar(
    prediction: dict,
    style: str = DEFAULT_STYLE,
) -> AvatarResult:
    """
    Generate avatar from structured prediction.
    """

    return _generator.generate(
        prediction,
        style,
    )