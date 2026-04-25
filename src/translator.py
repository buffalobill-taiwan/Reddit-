import ollama
from typing import Optional


TRANSLATION_PROMPT = """Translate the following text from English to Traditional Chinese (Taiwan).
You are a translator specialized in horror stories.
Must preserve:
- The scary atmosphere and emotion
- The tight pacing of the story
- Conversational dialogue style
Only output the translation result, no explanation."""


MODELS = [
    "translategemma:4b",
    "gemma4:26b",
    "gemma4:14b",
    "gemma4:2b",
    "gemma3:12b",
    "gemma3:4b",
]


def translate(
    text: str,
    model: Optional[str] = None,
    system_prompt: str = TRANSLATION_PROMPT,
) -> str:
    """
    Translate text to Traditional Chinese using Ollama.

    Args:
        text: Text to translate
        model: Model to use (auto-fallback if not specified)
        system_prompt: System prompt for translation

    Returns:
        Translated text in Traditional Chinese
    """
    if model is None:
        model = find_available_model()

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        if "not found" in str(e).lower():
            fallback_model = find_available_model(exclude=model)
            if fallback_model:
                return translate(text, model=fallback_model, system_prompt=system_prompt)
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