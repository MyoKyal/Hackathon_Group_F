from app.services.matching.stage1_rules import (
    category_match_score,
    compute_donor_receiver_score,
    distance_score,
    jaccard_similarity,
    keyword_score,
    passes_hard_filter,
    tokenize,
)


def test_category_match_dominates():
    same_category = compute_donor_receiver_score(
        "food", "rice bag", "white rice",
        "food", "unrelated", "xyz",
        distance_meters=0,
    )
    diff_category = compute_donor_receiver_score(
        "food", "rice bag", "white rice",
        "clothing", "rice bag", "white rice",
        distance_meters=0,
    )
    assert same_category > diff_category


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
