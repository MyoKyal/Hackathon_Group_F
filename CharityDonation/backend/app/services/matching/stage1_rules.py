import re
from dataclasses import dataclass
from datetime import datetime, time
from uuid import UUID

# ponytail: small hand-picked stopword list, not a full NLP stopword corpus —
# swap for nltk/spacy stopwords if keyword matching needs to handle more languages/edge cases
STOPWORDS = {
    "a", "an", "the", "my", "our", "your", "his", "her", "its", "their",
    "of", "for", "to", "in", "on", "at", "and", "or", "with", "is", "are",
}


def tokenize(text: str | None) -> set[str]:
    if not text:
        return set()
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if t not in STOPWORDS}


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    intersection = left & right
    union = left | right
    return len(intersection) / len(union)


def category_match_score(donation_category: str, request_category: str) -> float:
    return 1.0 if donation_category.strip().lower() == request_category.strip().lower() else 0.0


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


def quantity_score(donation_quantity: int, quantity_needed: int) -> float:
    if donation_quantity >= quantity_needed:
        # ponytail: flat 0.9 for any oversupply rather than a decaying penalty —
        # revisit if huge surplus donations need to rank below closer full matches
        return 1.0 if donation_quantity == quantity_needed else 0.9
    return donation_quantity / quantity_needed


def compute_donor_receiver_score(
    donation_category: str,
    donation_name: str,
    donation_description: str | None,
    donation_quantity: int,
    request_category: str,
    request_name: str,
    request_description: str | None,
    quantity_needed: int,
    distance_meters: float,
) -> float:
    cat = category_match_score(donation_category, request_category)
    kw = keyword_score(donation_name, donation_description, request_name, request_description)
    qty = quantity_score(donation_quantity, quantity_needed)
    dist = distance_score(distance_meters)
    return 0.45 * cat + 0.25 * kw + 0.15 * qty + 0.15 * dist


def passes_hard_filter(category_match: float, keyword: float) -> bool:
    return not (category_match == 0.0 and keyword < 0.2)


@dataclass
class ScoredRequest:
    request_id: UUID
    requester_name: str
    item_name: str
    quantity_needed: int
    distance_meters: float
    score: float


@dataclass
class ScoredVolunteer:
    volunteer_id: UUID
    full_name: str
    distance_meters: float
    score: float
    is_available: bool
    transportation_type: str | None = None


TRANSPORT_CAPACITY_KG: dict[str, float | None] = {
    "walking": 10.0,
    "bicycle": 25.0,
    "motorbike": 70.0,
    "car": 300.0,
    "truck": None,  # unlimited
}

TRANSPORT_SCORE: dict[str, float] = {
    "walking": 5.0,
    "bicycle": 10.0,
    "motorbike": 15.0,
    "car": 18.0,
    "truck": 20.0,
}


def is_within_availability(
    available_days: list[str] | None,
    available_start_time: time | None,
    available_end_time: time | None,
    now: datetime,
) -> bool:
    if available_days is None or available_start_time is None or available_end_time is None:
        return True
    if now.strftime("%A").lower() not in {d.lower() for d in available_days}:
        return False
    return available_start_time <= now.time() <= available_end_time


def passes_volunteer_mandatory(
    is_available: bool,
    max_capacity_kg: float | None,
    donation_weight_kg: float,
    max_travel_km: float,
    total_travel_km: float,
    available_days: list[str] | None,
    available_start_time: time | None,
    available_end_time: time | None,
    now: datetime,
) -> bool:
    if not is_available:
        return False
    if max_capacity_kg is not None and donation_weight_kg > max_capacity_kg:
        return False
    if total_travel_km > max_travel_km:
        return False
    if not is_within_availability(available_days, available_start_time, available_end_time, now):
        return False
    return True


def volunteer_distance_score(distance_km: float) -> float:
    if distance_km <= 2:
        return 30.0
    if distance_km <= 5:
        return 25.0
    if distance_km <= 10:
        return 15.0
    return 5.0


def transportation_score(transport_type: str) -> float:
    return TRANSPORT_SCORE[transport_type]


def workload_score(active_deliveries: int) -> float:
    if active_deliveries == 0:
        return 15.0
    if active_deliveries == 1:
        return 10.0
    if active_deliveries == 2:
        return 5.0
    return 0.0


def reliability_score(rating: float) -> float:
    if rating >= 4.8:
        return 10.0
    if rating >= 4.5:
        return 8.0
    if rating >= 4.0:
        return 5.0
    return 2.0


def preferred_category_score(preferred_categories: list[str] | None, donation_category: str) -> float:
    if not preferred_categories:
        return 0.0
    normalized = {c.strip().lower() for c in preferred_categories}
    return 5.0 if donation_category.strip().lower() in normalized else 0.0


def experience_score(completed_deliveries: int) -> float:
    if completed_deliveries > 100:
        return 10.0
    if completed_deliveries > 50:
        return 8.0
    if completed_deliveries > 20:
        return 5.0
    return 2.0


def compute_volunteer_score(
    transport_type: str,
    distance_km: float,
    active_deliveries: int,
    reliability_rating: float,
    preferred_categories: list[str] | None,
    donation_category: str,
    completed_deliveries: int,
) -> float:
    return (
        transportation_score(transport_type)
        + volunteer_distance_score(distance_km)
        + workload_score(active_deliveries)
        + reliability_score(reliability_rating)
        + preferred_category_score(preferred_categories, donation_category)
        + experience_score(completed_deliveries)
    )
