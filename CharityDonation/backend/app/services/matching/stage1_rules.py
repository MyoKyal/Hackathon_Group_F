import re
from dataclasses import dataclass
from uuid import UUID


def tokenize(text: str | None) -> set[str]:
    if not text:
        return set()
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return set(tokens)


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    intersection = left & right
    union = left | right
    return len(intersection) / len(union)


def category_match_score(donation_category: str, request_category: str) -> float:
    return 1.0 if donation_category == request_category else 0.0


def keyword_score(
    donation_name: str,
    donation_description: str | None,
    request_name: str,
    request_description: str | None,
) -> float:
    donation_tokens = tokenize(f"{donation_name} {donation_description or ''}")
    request_tokens = tokenize(f"{request_name} {request_description or ''}")
    return jaccard_similarity(donation_tokens, request_tokens)


def distance_score(distance_meters: float) -> float:
    return 1.0 / (1.0 + distance_meters / 1000.0)


def compute_donor_receiver_score(
    donation_category: str,
    donation_name: str,
    donation_description: str | None,
    request_category: str,
    request_name: str,
    request_description: str | None,
    distance_meters: float,
) -> float:
    cat = category_match_score(donation_category, request_category)
    kw = keyword_score(donation_name, donation_description, request_name, request_description)
    dist = distance_score(distance_meters)
    return 0.5 * cat + 0.3 * kw + 0.2 * dist


def passes_hard_filter(category_match: float, keyword: float) -> bool:
    return not (category_match == 0.0 and keyword < 0.2)


@dataclass
class ScoredRequest:
    request_id: UUID
    requester_name: str
    item_name: str
    distance_meters: float
    score: float


@dataclass
class ScoredVolunteer:
    volunteer_id: UUID
    full_name: str
    distance_meters: float
    score: float
    is_available: bool
