import base64
import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"
OPENROUTER_TIMEOUT_SECONDS = 15

VERIFICATION_PROMPT = """You are verifying a charity donation delivery photo.

The receiver is confirming they received this SPECIFIC item:
- Item: {item_name}
- Category: {category}
- Description: {description}

Look at the attached photo carefully. Does it show the specific item named above —
not just any item from the same general category? For example, if the item is
"Pencil", a photo of a book, notebook, or other stationery does NOT count as a
match even though it is in the same category ({category}) — the photo must show
pencils specifically. Minor variations in packaging, angle, lighting, or quantity
are fine, but the core object shown must genuinely be the named item.

Respond in strict JSON: {{"match": <true or false>, "reason": "<one sentence>"}}"""


def _call_openrouter_vision(prompt: str, image_bytes: bytes, mime_type: str) -> str:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime_type};base64,{image_b64}"

    response = httpx.post(
        OPENROUTER_URL,
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        },
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        timeout=OPENROUTER_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"] or ""


def _parse_verdict(response_text: str) -> tuple[bool, str]:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response")

    payload = json.loads(cleaned[start : end + 1])
    return bool(payload["match"]), str(payload["reason"])


def verify_photo(
    item_name: str,
    category: str,
    description: str | None,
    image_bytes: bytes,
    mime_type: str,
) -> tuple[bool | None, str | None]:
    """Checks whether the photo shows the specific donated item (not just its
    category), via a free vision model on OpenRouter. Returns (match, reasoning).

    `match` is:
    - `True`/`False` when the model successfully judged the photo
    - `None` when verification couldn't run at all (missing API key, timeout,
      rate limit, unparseable response, etc.) — callers should treat `None`
      as "unknown" and let the action proceed, since blocking on an
      infrastructure failure (e.g. a rate limit) would lock out every receiver
      until it recovers. Only a confirmed `False` should block.
    """
    prompt = VERIFICATION_PROMPT.format(
        item_name=item_name, category=category, description=description or ""
    )
    try:
        response_text = _call_openrouter_vision(prompt, image_bytes, mime_type)
        return _parse_verdict(response_text)
    except Exception as exc:
        logger.warning("OpenRouter photo verification failed (treated as unknown): %s", exc)
        return None, None
