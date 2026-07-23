import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import google.generativeai as genai

from app.config import settings
from app.services.matching.stage1_rules import ScoredRequest, ScoredVolunteer

logger = logging.getLogger(__name__)

GEMINI_TIMEOUT_SECONDS = 5

DONOR_RECEIVER_PROMPT = """You are helping match a donation to the best receiver request.

DONATION:
- Item: {item_name}
- Category: {category}
- Description: {description}
- Quantity available: {quantity}

CANDIDATE REQUESTS (pre-filtered, top {n}):
{numbered_list_of_candidates_with_scores}

Prefer candidates whose quantity needed is fully covered by the donation quantity,
but a partial match is still acceptable if it's otherwise the best fit.
Select the single best match by number and give a one-sentence reason.
Respond in strict JSON: {{"selected_index": <int>, "reason": "<string>"}}"""

VOLUNTEER_PROMPT = """You are helping assign the best volunteer to deliver a donation.

DONATION PICKUP:
- Item: {item_name}
- Category: {category}
- Description: {description}

CANDIDATE VOLUNTEERS (pre-filtered, top {n}):
{numbered_list_of_candidates_with_scores}

Select the single best volunteer by number and give a one-sentence reason.
Respond in strict JSON: {{"selected_index": <int>, "reason": "<string>"}}"""


def _format_request_candidates(candidates: list[ScoredRequest]) -> str:
    lines = []
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            f"{index}. Requester: {candidate.requester_name}, Item: {candidate.item_name}, "
            f"Quantity needed: {candidate.quantity_needed}, "
            f"Score: {candidate.score:.3f}, Distance: {candidate.distance_meters / 1000:.2f} km"
        )
    return "\n".join(lines)


def _format_volunteer_candidates(candidates: list[ScoredVolunteer]) -> str:
    lines = []
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            f"{index}. Name: {candidate.full_name}, Score: {candidate.score:.3f}, "
            f"Distance: {candidate.distance_meters / 1000:.2f} km, "
            f"Transport: {candidate.transportation_type}, Available: {candidate.is_available}"
        )
    return "\n".join(lines)


def _call_gemini(prompt: str) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-flash-latest")

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(model.generate_content, prompt)
        try:
            response = future.result(timeout=GEMINI_TIMEOUT_SECONDS)
        except FuturesTimeoutError as exc:
            raise TimeoutError("Gemini request timed out") from exc

    return response.text or ""


def _extract_json_object(text: str) -> dict:
    """Find the first balanced {...} object in text, ignoring any stray
    braces elsewhere in the surrounding prose."""
    decoder = json.JSONDecoder()
    search_from = 0
    while True:
        brace_index = text.find("{", search_from)
        if brace_index == -1:
            raise ValueError("No JSON object found in Gemini response")
        try:
            payload, _ = decoder.raw_decode(text, brace_index)
            return payload
        except json.JSONDecodeError:
            search_from = brace_index + 1


def _parse_selection(response_text: str, candidate_count: int) -> tuple[int, str]:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    payload = _extract_json_object(cleaned)
    selected_index = int(payload["selected_index"])
    reason = str(payload["reason"])
    if selected_index < 1 or selected_index > candidate_count:
        raise ValueError("selected_index out of range")
    return selected_index, reason


def select_receiver_request(
    item_name: str,
    category: str,
    description: str | None,
    quantity: int,
    candidates: list[ScoredRequest],
) -> tuple[ScoredRequest, str | None]:
    if not candidates:
        raise ValueError("No candidates provided")

    top = candidates[0]
    if len(candidates) == 1:
        return top, "Selected top Stage 1 candidate (single option)."

    prompt = DONOR_RECEIVER_PROMPT.format(
        item_name=item_name,
        category=category,
        description=description or "",
        quantity=quantity,
        n=len(candidates),
        numbered_list_of_candidates_with_scores=_format_request_candidates(candidates),
    )

    try:
        response_text = _call_gemini(prompt)
        selected_index, reason = _parse_selection(response_text, len(candidates))
        return candidates[selected_index - 1], reason
    except Exception as exc:
        logger.warning("Gemini receiver matching failed, falling back to Stage 1: %s", exc)
        return top, None


def select_volunteer(
    item_name: str,
    category: str,
    description: str | None,
    candidates: list[ScoredVolunteer],
) -> tuple[ScoredVolunteer, str | None]:
    if not candidates:
        raise ValueError("No candidates provided")

    top = candidates[0]
    if len(candidates) == 1:
        return top, "Selected top Stage 1 candidate (single option)."

    prompt = VOLUNTEER_PROMPT.format(
        item_name=item_name,
        category=category,
        description=description or "",
        n=len(candidates),
        numbered_list_of_candidates_with_scores=_format_volunteer_candidates(candidates),
    )

    try:
        response_text = _call_gemini(prompt)
        selected_index, reason = _parse_selection(response_text, len(candidates))
        return candidates[selected_index - 1], reason
    except Exception as exc:
        logger.warning("Gemini volunteer matching failed, falling back to Stage 1: %s", exc)
        return top, None
