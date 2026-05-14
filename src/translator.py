import ollama
from typing import Optional


MODELS = [
    "gemma4:26b",
    "translategemma:12b",
    "translategemma:4b",
    "gemma4:14b",
    "gemma4:2b",
    "gemma3:12b",
    "gemma3:4b",
]

SUBREDDIT_PROMPTS = {
    "tifu": "翻譯成正體中文。只輸出翻譯結果。保留原文的幽默風趣和口語化表達。請原文的「TIFU」不要翻譯，保留英文。",
    "nosleep": "翻譯成正體中文。只輸出翻譯結果。保留恐怖氛圍和緊湊節奏。",
    "shortscarystories": "翻譯成正體中文。只輸出翻譯結果。保留驚悚氛圍。",
}

DEFAULT_PREFIX = "翻譯成正體中文。只輸出翻譯結果，保留原文風格和語氣。"


CHUNK_SIZE = 1500  # 字元數，超過則分段翻譯


def get_prefix(subreddit: str) -> str:
    """Get translation prefix for a subreddit."""
    normalized = subreddit.lower().strip("/")
    return SUBREDDIT_PROMPTS.get(normalized, DEFAULT_PREFIX)


TRANSLATION_PREFIX = "Translate to Traditional Chinese (Taiwan). Only output the translation, no explanation. Preserve horror atmosphere: "


def translate(
    text: str,
    model: Optional[str] = None,
    prefix: str = TRANSLATION_PREFIX,
) -> str:
    """
    Translate text to Traditional Chinese using Ollama.

    Auto-chunks long text into smaller pieces to avoid context window issues.
    Each chunk (except the first) includes the previous translation as reference
    to keep names and terms consistent.

    Args:
        text: Text to translate
        model: Model to use (auto-fallback if not specified)
        prefix: Prompt prefix for translation

    Returns:
        Translated text in Traditional Chinese
    """
    if model is None:
        model = find_available_model()

    if len(text) > CHUNK_SIZE:
        return _translate_chunked(text, model, prefix)

    return _translate_single(text, model, prefix)


def _translate_chunked(text: str, model: str, prefix: str) -> str:
    """Split long text by paragraphs and translate each chunk sequentially."""
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    chunks = []
    current = []
    size = 0

    for para in paragraphs:
        if size + len(para) > CHUNK_SIZE and current:
            chunks.append('\n\n'.join(current))
            current = []
            size = 0
        current.append(para)
        size += len(para)

    if current:
        chunks.append('\n\n'.join(current))

    results = []
    for i, chunk in enumerate(chunks):
        reference = None
        if i > 0:
            reference = f"前文翻譯（請保持人名譯名一致）：\n{results[-1]}"

        result = _translate_single(chunk, model, prefix, reference=reference)
        results.append(result)

    return '\n\n'.join(results)


def _translate_single(
    text: str,
    model: str,
    prefix: str,
    reference: Optional[str] = None,
) -> str:
    """Translate a single chunk of text to Traditional Chinese using Ollama."""
    estimated_tokens = int(len(text) * 1.5)
    num_predict = max(2048, int(estimated_tokens * 1.5))
    num_predict = min(num_predict, 8192)

    user_content = text
    if reference:
        user_content = f"{reference}\n\n---\n\n{text}"

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": prefix},
                {"role": "user", "content": user_content},
            ],
            options={
                "num_predict": num_predict,
                "temperature": 0.3,
                "repeat_penalty": 1.2,
                "top_p": 0.9,
            }
        )
        content = response["message"]["content"]
        if not content.strip():
            fallback_model = find_available_model(exclude=model)
            if fallback_model:
                return _translate_single(text, model=fallback_model, prefix=prefix, reference=reference)
            raise RuntimeError(f"Model {model} returned empty output and no fallback available")
        return content
    except ollama.ResponseError as e:
        if "not found" in str(e).lower():
            fallback_model = find_available_model(exclude=model)
            if fallback_model:
                return _translate_single(text, model=fallback_model, prefix=prefix, reference=reference)
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
