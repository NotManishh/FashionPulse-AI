from datetime import datetime, timezone, timedelta
from app.ml.scoring import scoring_engine


def test_zero_baseline_handling():
    # If baseline is 0 and current mentions is at or above threshold
    growth_rate, status = scoring_engine.calculate_growth(current_mentions=15, baseline_mentions=0)
    assert growth_rate is None
    assert status == "emerging"


def test_small_sample_size_handling():
    # Below min sample threshold of 3
    growth_rate, status = scoring_engine.calculate_growth(current_mentions=2, baseline_mentions=1)
    assert growth_rate is None
    assert status == "insufficient_data"


def test_valid_growth_calculation():
    # Baseline 10, Current 20 -> 100% growth
    growth_rate, status = scoring_engine.calculate_growth(current_mentions=20, baseline_mentions=10)
    assert growth_rate == 100.0
    assert status == "rising"


def test_logarithmic_engagement_normalization():
    yt_metrics = {"views": 100000, "likes": 5000, "comments": 300}
    reddit_metrics = {"score": 1200, "num_comments": 150}
    insta_metrics = {"like_count": 8000, "comments_count": 250}

    yt_score = scoring_engine.normalize_engagement("youtube", yt_metrics)
    reddit_score = scoring_engine.normalize_engagement("reddit", reddit_metrics)
    insta_score = scoring_engine.normalize_engagement("instagram", insta_metrics)

    # Log scaling keeps all 3 within reasonable, comparable bands (e.g. 30 to 75)
    assert 20.0 < yt_score < 100.0
    assert 20.0 < reddit_score < 100.0
    assert 20.0 < insta_score < 100.0


def test_cross_platform_scoring():
    all_three = {"reddit": 10, "instagram": 5, "youtube": 8}
    two_platforms = {"reddit": 10, "instagram": 5, "youtube": 0}
    one_platform = {"reddit": 10, "instagram": 0, "youtube": 0}

    assert scoring_engine.calculate_cross_platform_score(all_three) == 1.0
    assert scoring_engine.calculate_cross_platform_score(two_platforms) == 0.65
    assert scoring_engine.calculate_cross_platform_score(one_platform) == 0.35


def test_calculate_trend_score_holistic():
    now = datetime.now(timezone.utc)
    res = scoring_engine.calculate_trend_score(
        current_mentions=25,
        baseline_mentions=10,
        total_engagement=120.0,
        platform_breakdown={"reddit": 10, "instagram": 10, "youtube": 5},
        last_seen=now - timedelta(hours=2),
        total_sample_size=100
    )
    
    assert 10.0 <= res["trend_score"] <= 100.0
    assert 0.0 <= res["confidence"] <= 1.0
    assert res["growth_rate"] == 150.0
    assert res["growth_status"] == "rising"


def test_provisional_baseline_handling():
    # When baseline sample size is small (< 30) and not comparable, status is provisional
    growth_rate, status = scoring_engine.calculate_growth(
        current_mentions=25,
        baseline_mentions=2,
        current_sample_size=150,
        baseline_sample_size=12,
        is_baseline_comparable=False
    )
    assert growth_rate == 1150.0
    assert status == "provisional"


def test_smooth_tanh_momentum_scaling_distinct_and_unclipped():
    now = datetime.now(timezone.utc)
    # Test across multiple high-growth tiers: 250%, 800%, 1500%, 2300%
    growths = [
        (14, 4),   # 250%
        (18, 2),   # 800%
        (16, 1),   # 1500%
        (24, 1),   # 2300%
    ]
    scores = []
    for curr, base in growths:
        res = scoring_engine.calculate_trend_score(
            current_mentions=curr,
            baseline_mentions=base,
            total_engagement=100.0,
            platform_breakdown={"youtube": curr},
            last_seen=now,
            total_sample_size=150
        )
        scores.append(res["momentum_score"])

    # Every score must be strictly less than 100.0 (no rounding saturation ceiling)
    assert all(s < 100.0 for s in scores)
    # Every score must be strictly monotonically increasing with growth
    assert scores[0] < scores[1] < scores[2] < scores[3]
    # No duplicate momentum scores
    assert len(set(scores)) == len(scores)
