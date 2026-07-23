from unittest.mock import patch

import pytest

from app.services.matching import stage2_gemini
from app.services.matching.stage1_rules import ScoredRequest, ScoredVolunteer

REQUEST_CANDIDATES = [
    ScoredRequest(
        request_id="00000000-0000-0000-0000-000000000001",
        requester_name="Alice",
        item_name="Rice",
        quantity_needed=10,
        distance_meters=500,
        score=0.9,
    ),
    ScoredRequest(
        request_id="00000000-0000-0000-0000-000000000002",
        requester_name="Bob",
        item_name="Rice bag",
        quantity_needed=5,
        distance_meters=2000,
        score=0.7,
    ),
]

VOLUNTEER_CANDIDATES = [
    ScoredVolunteer(
        volunteer_id="00000000-0000-0000-0000-000000000010",
        full_name="Carol",
        distance_meters=800,
        score=55.0,
        is_available=True,
        transportation_type="car",
    ),
    ScoredVolunteer(
        volunteer_id="00000000-0000-0000-0000-000000000011",
        full_name="Dave",
        distance_meters=3000,
        score=40.0,
        is_available=True,
        transportation_type="bicycle",
    ),
]


def test_single_candidate_skips_gemini_entirely():
    with patch.object(stage2_gemini, "_call_gemini") as mock_call:
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, [REQUEST_CANDIDATES[0]]
        )
    mock_call.assert_not_called()
    assert selected is REQUEST_CANDIDATES[0]
    assert reason == "Selected top Stage 1 candidate (single option)."


@pytest.mark.parametrize(
    "bad_response",
    [
        "not json at all",
        "",
        '{"selected_index": 1}',  # missing reason
        '{"reason": "because"}',  # missing selected_index
        '{"selected_index": 99, "reason": "out of range"}',
        '{"selected_index": 0, "reason": "zero is out of range"}',
        '{"selected_index": "abc", "reason": "not an int"}',
        "```\n{not valid json}\n```",
        "here is my answer: {broken",
    ],
)
def test_malformed_gemini_response_falls_back_to_stage1_top(bad_response):
    with patch.object(stage2_gemini, "_call_gemini", return_value=bad_response):
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, REQUEST_CANDIDATES
        )
    assert selected is REQUEST_CANDIDATES[0]
    assert reason is None


def test_valid_gemini_response_selects_named_index():
    response = '{"selected_index": 2, "reason": "closer fit"}'
    with patch.object(stage2_gemini, "_call_gemini", return_value=response):
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, REQUEST_CANDIDATES
        )
    assert selected is REQUEST_CANDIDATES[1]
    assert reason == "closer fit"


def test_valid_response_with_stray_braces_in_surrounding_prose():
    # Regression: naive find("{")/rfind("}") would slice from the stray "{2}"
    # through the real JSON, producing an invalid combined string.
    response = (
        'Sure! Looking at candidate {2}, they seem best.\n'
        '{"selected_index": 2, "reason": "closest volunteer"}'
    )
    with patch.object(stage2_gemini, "_call_gemini", return_value=response):
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, REQUEST_CANDIDATES
        )
    assert selected is REQUEST_CANDIDATES[1]
    assert reason == "closest volunteer"


def test_valid_response_wrapped_in_markdown_fence():
    response = '```json\n{"selected_index": 1, "reason": "best match"}\n```'
    with patch.object(stage2_gemini, "_call_gemini", return_value=response):
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, REQUEST_CANDIDATES
        )
    assert selected is REQUEST_CANDIDATES[0]
    assert reason == "best match"


def test_gemini_timeout_falls_back_to_stage1_top():
    with patch.object(stage2_gemini, "_call_gemini", side_effect=TimeoutError("timed out")):
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, REQUEST_CANDIDATES
        )
    assert selected is REQUEST_CANDIDATES[0]
    assert reason is None


def test_missing_api_key_falls_back_to_stage1_top():
    with patch.object(
        stage2_gemini, "_call_gemini", side_effect=RuntimeError("GEMINI_API_KEY is not configured")
    ):
        selected, reason = stage2_gemini.select_receiver_request(
            "Rice", "food", None, 10, REQUEST_CANDIDATES
        )
    assert selected is REQUEST_CANDIDATES[0]
    assert reason is None


def test_no_candidates_raises():
    with pytest.raises(ValueError):
        stage2_gemini.select_receiver_request("Rice", "food", None, 10, [])


def test_volunteer_single_candidate_skips_gemini():
    with patch.object(stage2_gemini, "_call_gemini") as mock_call:
        selected, reason = stage2_gemini.select_volunteer(
            "Rice", "food", None, [VOLUNTEER_CANDIDATES[0]]
        )
    mock_call.assert_not_called()
    assert selected is VOLUNTEER_CANDIDATES[0]


def test_volunteer_malformed_response_falls_back_to_stage1_top():
    with patch.object(stage2_gemini, "_call_gemini", return_value="garbage"):
        selected, reason = stage2_gemini.select_volunteer(
            "Rice", "food", None, VOLUNTEER_CANDIDATES
        )
    assert selected is VOLUNTEER_CANDIDATES[0]
    assert reason is None


def test_volunteer_valid_response_selects_named_index():
    response = '{"selected_index": 2, "reason": "better fit"}'
    with patch.object(stage2_gemini, "_call_gemini", return_value=response):
        selected, reason = stage2_gemini.select_volunteer(
            "Rice", "food", None, VOLUNTEER_CANDIDATES
        )
    assert selected is VOLUNTEER_CANDIDATES[1]
    assert reason == "better fit"


def test_volunteer_no_candidates_raises():
    with pytest.raises(ValueError):
        stage2_gemini.select_volunteer("Rice", "food", None, [])
