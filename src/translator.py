import ollama
from typing import Optional


TRANSLATION_PROMPT = """你是一個專業翻譯師，擅長翻譯恐怖故事。請將以下Reddit貼文翻譯成正體中文，
必須保留：
- 原文的驚悚氛圍和情緒
- 故事的緊湊節奏
- 對話的口語化表達
只輸出翻譯結果，不要解釋。"""


MODELS = [
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