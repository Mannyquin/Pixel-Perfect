from dataclasses import dataclass


@dataclass(slots=True)
class PromptResult:

    prompt: str

    descriptors: list[str]

    style: str