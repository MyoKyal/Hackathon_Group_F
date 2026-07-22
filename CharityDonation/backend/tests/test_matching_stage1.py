from app.services.matching.stage1_rules import (
    category_match_score,
    compute_donor_receiver_score,
    compute_volunteer_score,
    distance_score,
    experience_score,
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
    assert passes_volunteer_mandatory(False, 70, 20, 10, 5) is False


def test_volunteer_mandatory_rejects_over_capacity():
    assert passes_volunteer_mandatory(True, 70, 120, 10, 5) is False


def test_volunteer_mandatory_allows_unlimited_capacity():
    assert passes_volunteer_mandatory(True, None, 10000, 10, 5) is True


def test_volunteer_mandatory_rejects_over_travel_distance():
    assert passes_volunteer_mandatory(True, 70, 20, 10, 15) is False


def test_volunteer_mandatory_passes_all_rules():
    assert passes_volunteer_mandatory(True, 70, 20, 10, 5) is True


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
