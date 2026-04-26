import ollama
from typing import Optional


MODELS = [
    "translategemma:12b",
    "translategemma:4b",
    "gemma4:26b",
    "gemma4:14b",
    "gemma4:2b",
    "gemma3:12b",
    "gemma3:4b",
]

TRANSLATION_PREFIX = "Translate to Traditional Chinese (Taiwan). Only output the translation, no explanation. Preserve horror atmosphere: "


def translate(
    text: str,
    model: Optional[str] = None,
    prefix: str = TRANSLATION_PREFIX,
) -> str:
    """
    Translate text to Traditional Chinese using Ollama.

    Args:
        text: Text to translate
        model: Model to use (auto-fallback if not specified)
        prefix: Prompt prefix for translation

    Returns:
        Translated text in Traditional Chinese
    """
    if model is None:
        model = find_available_model()

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "user", "content": prefix + text},
            ],
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        if "not found" in str(e).lower():
            fallback_model = find_available_model(exclude=model)
            if fallback_model:
                return translate(text, model=fallback_model, prefix=prefix)
        raise


def find_available_model(exclude: Optional[str] = None) -> Optional[str]:
    """
    Find the first available model from the models list.

    Args:
        exclude: Model to exclude from selection

    Returns:
        Available model name or None
    """
    for model in MODELS:
        if model != exclude:
            try:
                ollama.show(model)
                return model
            except ollama.ResponseError:
                continue
    return None