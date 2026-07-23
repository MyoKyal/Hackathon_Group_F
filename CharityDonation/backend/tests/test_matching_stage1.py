from datetime import datetime, time

from app.services.matching.stage1_rules import (
    category_match_score,
    compute_donor_receiver_score,
    compute_volunteer_score,
    distance_score,
    experience_score,
    is_within_availability,
    jaccard_similarity,
    keyword_score,
    passes_hard_filter,
    passes_volunteer_mandatory,
    preferred_category_score,
    quantity_score,
    reliability_score,
    tokenize,
    transportation_score,
    volunteer_distance_score,
    workload_score,
)

# Tuesday
NOW = datetime(2026, 7, 21, 10, 0)


def test_category_match_dominates():
    same_category = compute_donor_receiver_score(
        "food", "rice bag", "white rice", 10,
        "food", "unrelated", "xyz", 10,
        distance_meters=0,
    )
    diff_category = compute_donor_receiver_score(
        "food", "rice bag", "white rice", 10,
        "clothing", "rice bag", "white rice", 10,
        distance_meters=0,
    )
    assert same_category > diff_category


def test_quantity_score_full_partial_and_oversupply():
    assert quantity_score(10, 10) == 1.0
    assert quantity_score(5, 10) == 0.5
    assert quantity_score(20, 10) == 0.9


def test_distance_decay_monotonic():
    near = distance_score(100)
    far = distance_score(5000)
    assert near > far


def test_keyword_jaccard_symmetric():
    left = tokenize("rice bag donation")
    right = tokenize("bag of rice")
    assert jaccard_similarity(left, right) == jaccard_similarity(right, left)


def test_hard_filter_excludes_unrelated():
    cat = category_match_score("food", "clothing")
    kw = keyword_score("rice", None, "shoes", None)
    assert cat == 0.0
    assert kw < 0.2
    assert passes_hard_filter(cat, kw) is False


def test_hard_filter_allows_related_keywords():
    cat = category_match_score("food", "clothing")
    kw = keyword_score("rice bag", "for family", "rice", "need rice for family")
    assert passes_hard_filter(cat, kw) is True


def test_category_match_ignores_case_and_whitespace():
    assert category_match_score("Food", "food") == 1.0
    assert category_match_score(" Clothing ", "clothing") == 1.0
    assert category_match_score("Food", "Clothing") == 0.0


def test_hard_filter_excludes_stopword_only_overlap():
    # "torchlight"/"my electronic" vs "food"/"my food" — shared "my" must not
    # count as keyword similarity, or unrelated categories slip through.
    cat = category_match_score("electronic", "food")
    kw = keyword_score("torchlight", "my electronic", "food", "my food")
    assert kw == 0.0
    assert passes_hard_filter(cat, kw) is False


def test_volunteer_mandatory_rejects_unavailable():
    assert passes_volunteer_mandatory(False, 70, 20, 10, 5, None, None, None, NOW) is False


def test_volunteer_mandatory_rejects_over_capacity():
    assert passes_volunteer_mandatory(True, 70, 120, 10, 5, None, None, None, NOW) is False


def test_volunteer_mandatory_allows_unlimited_capacity():
    assert passes_volunteer_mandatory(True, None, 10000, 10, 5, None, None, None, NOW) is True


def test_volunteer_mandatory_rejects_over_travel_distance():
    assert passes_volunteer_mandatory(True, 70, 20, 10, 15, None, None, None, NOW) is False


def test_volunteer_mandatory_passes_all_rules():
    assert passes_volunteer_mandatory(True, 70, 20, 10, 5, None, None, None, NOW) is True


def test_volunteer_mandatory_rejects_outside_schedule():
    assert passes_volunteer_mandatory(
        True, 70, 20, 10, 5, ["saturday"], time(9, 0), time(17, 0), NOW
    ) is False


def test_volunteer_mandatory_allows_within_schedule():
    assert passes_volunteer_mandatory(
        True, 70, 20, 10, 5, ["tuesday"], time(9, 0), time(17, 0), NOW
    ) is True


def test_is_within_availability_no_schedule_set_does_not_block():
    assert is_within_availability(None, None, None, NOW) is True


def test_is_within_availability_wrong_day():
    assert is_within_availability(["monday"], time(0, 0), time(23, 59), NOW) is False


def test_is_within_availability_before_start_time():
    assert is_within_availability(["tuesday"], time(12, 0), time(17, 0), NOW) is False


def test_is_within_availability_after_end_time():
    assert is_within_availability(["tuesday"], time(6, 0), time(9, 0), NOW) is False


def test_is_within_availability_case_insensitive_day():
    assert is_within_availability(["Tuesday"], time(9, 0), time(17, 0), NOW) is True


def test_is_within_availability_exact_start_and_end_boundary_are_inclusive():
    assert is_within_availability(["tuesday"], time(10, 0), time(10, 0), NOW) is True


# --- Boundary-value edge cases ---


def test_volunteer_distance_score_exact_boundaries():
    assert volunteer_distance_score(2) == 30.0
    assert volunteer_distance_score(2.01) == 25.0
    assert volunteer_distance_score(5) == 25.0
    assert volunteer_distance_score(5.01) == 15.0
    assert volunteer_distance_score(10) == 15.0
    assert volunteer_distance_score(10.01) == 5.0
    assert volunteer_distance_score(0) == 30.0


def test_workload_score_exact_boundary_three_plus():
    assert workload_score(3) == 0.0
    assert workload_score(100) == 0.0


def test_reliability_score_exact_boundaries():
    assert reliability_score(4.8) == 10.0
    assert reliability_score(4.79) == 8.0
    assert reliability_score(4.5) == 8.0
    assert reliability_score(4.49) == 5.0
    assert reliability_score(4.0) == 5.0
    assert reliability_score(3.99) == 2.0
    assert reliability_score(0.0) == 2.0


def test_experience_score_exact_boundaries():
    assert experience_score(100) == 8.0  # not > 100
    assert experience_score(101) == 10.0
    assert experience_score(50) == 5.0  # not > 50
    assert experience_score(51) == 8.0
    assert experience_score(20) == 2.0  # not > 20
    assert experience_score(21) == 5.0
    assert experience_score(0) == 2.0


def test_quantity_score_exact_equal_boundary():
    assert quantity_score(10, 10) == 1.0
    assert quantity_score(11, 10) == 0.9


def test_quantity_score_zero_needed_would_divide_by_zero_if_under():
    # documents current behavior: equal (0, 0) short-circuits to the ==-branch
    # before division, so it never hits ZeroDivisionError.
    assert quantity_score(0, 0) == 1.0


def test_distance_score_zero_distance_is_max():
    assert distance_score(0) == 1.0


def test_passes_hard_filter_keyword_exact_boundary():
    # boundary is keyword < 0.2 -> exactly 0.2 with no category match must PASS
    assert passes_hard_filter(0.0, 0.2) is True
    assert passes_hard_filter(0.0, 0.19999) is False


def test_passes_hard_filter_category_match_always_passes_regardless_of_keyword():
    assert passes_hard_filter(1.0, 0.0) is True


# --- Tie-breaking / stability ---


def test_equal_scores_preserve_original_relative_order_when_sorted():
    # list.sort() is stable: candidates with identical scores must keep their
    # original relative order rather than reshuffling on every match run.
    items = [("first", 1.0), ("second", 1.0), ("third", 1.0)]
    items_sorted = sorted(items, key=lambda item: item[1], reverse=True)
    assert [name for name, _ in items_sorted] == ["first", "second", "third"]


def test_compute_volunteer_score_identical_inputs_produce_identical_scores():
    a = compute_volunteer_score("car", 1, 0, 4.9, ["Food"], "food", 150)
    b = compute_volunteer_score("car", 1, 0, 4.9, ["Food"], "food", 150)
    assert a == b


def test_volunteer_distance_score_buckets():
    assert volunteer_distance_score(1) == 30.0
    assert volunteer_distance_score(4) == 25.0
    assert volunteer_distance_score(9) == 15.0
    assert volunteer_distance_score(20) == 5.0


def test_transportation_score_larger_vehicles_score_higher():
    assert transportation_score("truck") > transportation_score("car")
    assert transportation_score("car") > transportation_score("motorbike")
    assert transportation_score("motorbike") > transportation_score("bicycle")
    assert transportation_score("bicycle") > transportation_score("walking")


def test_workload_score_prefers_fewer_active_deliveries():
    assert workload_score(0) == 15.0
    assert workload_score(1) == 10.0
    assert workload_score(2) == 5.0
    assert workload_score(3) == 0.0


def test_reliability_score_buckets():
    assert reliability_score(4.9) == 10.0
    assert reliability_score(4.6) == 8.0
    assert reliability_score(4.2) == 5.0
    assert reliability_score(3.0) == 2.0


def test_preferred_category_score_matches_case_insensitively():
    assert preferred_category_score(["Food", "Medicine"], "food") == 5.0
    assert preferred_category_score(["Food"], "clothing") == 0.0
    assert preferred_category_score(None, "food") == 0.0
    assert preferred_category_score([], "food") == 0.0


def test_experience_score_buckets():
    assert experience_score(150) == 10.0
    assert experience_score(75) == 8.0
    assert experience_score(30) == 5.0
    assert experience_score(5) == 2.0


def test_compute_volunteer_score_prefers_closer_more_experienced_volunteer():
    near_experienced = compute_volunteer_score("car", 1, 0, 4.9, ["Food"], "food", 150)
    far_novice = compute_volunteer_score("walking", 15, 3, 2.0, None, "food", 0)
    assert near_experienced > far_novice
