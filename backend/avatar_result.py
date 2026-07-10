from dataclasses import dataclass

from prompt_result import PromptResult


@dataclass(slots=True)
class AvatarResult:
    image_url: str

    prompt: PromptResult