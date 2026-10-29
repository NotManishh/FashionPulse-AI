import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
from app.core.config import settings


class TrendScoringEngine:
    """
    Transparent, configurable scoring engine for fashion trends.
    Normalizes multi-platform social metrics and computes:
    - trend_score [0 - 100]
    - momentum_score [0 - 100]
    - growth_percentage (or None if baseline is zero / small)
    - growth_status ("emerging", "rising", "steady", "peaking", "insufficient_data")
    - confidence [0.0 - 1.0]
    """

    def __init__(
        self,
        weight_freq: float = settings.WEIGHT_FREQUENCY,
        weight_momentum: float = settings.WEIGHT_MOMENTUM,
        weight_engagement: float = settings.WEIGHT_ENGAGEMENT,
        weight_cross_plat: float = settings.WEIGHT_CROSS_PLATFORM,
        weight_recency: float = settings.WEIGHT_RECENCY,
        min_sample_threshold: int = settings.MIN_OBSERVATION_THRESHOLD
    ):
        self.w_freq = weight_freq
        self.w_momentum = weight_momentum
        self.w_eng = weight_engagement
        self.w_cross = weight_cross_plat
        self.w_recency = weight_recency
        self.min_sample_threshold = min_sample_threshold

    @staticmethod
    def normalize_engagement(platform: str, raw_metrics: Dict[str, Any]) -> float:
        """
        Logarithmically scales platform engagement metrics to prevent viral outliers
        from dominating scores, and aligns Reddit, Instagram, and YouTube.
        """
        if not raw_metrics:
            return 0.0

        if platform == "youtube":
            views = float(raw_metrics.get("views", 0))
            likes = float(raw_metrics.get("likes", 0))
            comments = float(raw_metrics.get("comments", 0))
            # Log scale: views have higher volume than likes/comments
            score = (math.log1p(views) * 1.5) + (math.log1p(likes) * 3.0) + (math.log1p(comments) * 4.0)
            return round(score, 3)

        elif platform == "reddit":
            upvotes = float(raw_metrics.get("score", raw_metrics.get("upvotes", 0)))
            comments = float(raw_metrics.get("num_comments", 0))
            score = (math.log1p(max(0.0, upvotes)) * 3.5) + (math.log1p(max(0.0, comments)) * 4.5)
            return round(score, 3)

        elif platform == "instagram":
            likes = float(raw_metrics.get("like_count", raw_metrics.get("likes", 0)))
            comments = float(raw_metrics.get("comments_count", raw_metrics.get("comments", 0)))
            score = (math.log1p(likes) * 3.0) + (math.log1p(comments) * 5.0)
            return round(score, 3)

        return 0.0

    def calculate_growth(
        self,
        current_mentions: int,
        baseline_mentions: int,
        current_sample_size: Optional[int] = None,
        baseline_sample_size: Optional[int] = None,
        is_baseline_comparable: bool = False
    ) -> Tuple[Optional[float], str]:
        """
        Calculates mathematical growth rate.
        Prevents misleading growth rates when baseline is zero, sample size is below threshold,
        or collection effort between windows is non-comparable (e.g. retrospective snapshot).
        """
        if current_mentions < self.min_sample_threshold:
            return None, "insufficient_data"

        if baseline_mentions == 0:
            # Baseline is zero: cannot divide by zero; label as emerging new arrival
            return None, "emerging"

        # Check for non-comparable baseline (e.g. baseline sample too small or query configuration changed)
        if baseline_sample_size is not None and not is_baseline_comparable and baseline_sample_size < 30:
            # Baseline is non-comparable due to retrospective query snapshot / collection effort disparity
            growth = ((current_mentions - baseline_mentions) / float(baseline_mentions)) * 100.0
            return round(growth, 1), "provisional"

        # If sample sizes are provided and baseline is comparable, compute collection-effort normalized growth (share of voice)
        if current_sample_size and baseline_sample_size and current_sample_size > 0 and baseline_sample_size > 0:
            f_curr = current_mentions / float(current_sample_size)
            f_base = baseline_mentions / float(baseline_sample_size)
            growth = ((f_curr - f_base) / f_base) * 100.0
        else:
            growth = ((current_mentions - baseline_mentions) / float(baseline_mentions)) * 100.0

        growth_rounded = round(growth, 1)

        if growth_rounded > 40.0:
            status = "rising"
        elif growth_rounded > 0.0:
            status = "steady"
        elif growth_rounded < -20.0:
            status = "peaking"
        else:
            status = "steady"

        return growth_rounded, status

    def calculate_recency_score(self, last_seen: datetime) -> float:
        """Computes exponential recency decay over 7 days."""
        now = datetime.now(timezone.utc)
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        delta_hours = max(0.0, (now - last_seen).total_seconds() / 3600.0)
        # Half-life of 48 hours
        decay = math.exp(-0.015 * delta_hours)
        return min(1.0, max(0.0, decay))

    def calculate_cross_platform_score(self, platform_breakdown: Dict[str, int]) -> float:
        """
        Evaluates cross-platform presence.
        Presence across 3 platforms receives maximum bonus (1.0),
        2 platforms receives 0.65, 1 platform receives 0.35.
        """
        active_platforms = [p for p, count in platform_breakdown.items() if count > 0]
        num_active = len(active_platforms)
        
        if num_active >= 3:
            return 1.0
        elif num_active == 2:
            return 0.65
        elif num_active == 1:
            return 0.35
        return 0.0

    def calculate_confidence(
        self,
        mention_count: int,
        platform_breakdown: Dict[str, int],
        avg_classifier_confidence: float = 0.85
    ) -> float:
        """
        Calculates confidence score based on sample size, source diversity,
        and ML classification reliability.
        """
        # Sample size factor saturates around 30 mentions
        sample_factor = min(1.0, mention_count / 30.0)
        # Platform diversity factor
        plat_factor = self.calculate_cross_platform_score(platform_breakdown)
        
        confidence = (sample_factor * 0.45) + (plat_factor * 0.30) + (avg_classifier_confidence * 0.25)
        return round(min(0.99, max(0.10, confidence)), 2)

    def calculate_trend_score(
        self,
        current_mentions: int,
        baseline_mentions: int,
        total_engagement: float,
        platform_breakdown: Dict[str, int],
        last_seen: datetime,
        total_sample_size: int = 100,
        baseline_sample_size: Optional[int] = None,
        is_baseline_comparable: bool = False,
        avg_classifier_confidence: float = 0.85
    ) -> Dict[str, Any]:
        """
        Calculates holistic trend metrics:
        trend_score, momentum_score, growth_rate, growth_status, confidence.
        """
        # 1. Frequency Score (normalized by log-scale relative to sample)
        freq_ratio = current_mentions / max(1, total_sample_size)
        freq_score = min(100.0, (math.log1p(current_mentions) / math.log1p(max(10, total_sample_size))) * 100.0)

        # 2. Growth & Momentum
        growth_rate, growth_status = self.calculate_growth(
            current_mentions,
            baseline_mentions,
            current_sample_size=total_sample_size,
            baseline_sample_size=baseline_sample_size,
            is_baseline_comparable=is_baseline_comparable
        )
        if growth_rate is not None:
            # Smooth velocity response with wide scaling denominator (S=1200.0)
            # prevents premature saturation/rounding to 100.0 and maintains visible differences
            if growth_rate >= 0:
                momentum_score = min(99.0, 50.0 + 50.0 * math.tanh(growth_rate / 1200.0))
            else:
                momentum_score = max(5.0, 50.0 - 50.0 * math.tanh(abs(growth_rate) / 400.0))
        elif growth_status == "emerging":
            momentum_score = 75.0  # High initial momentum for verified new emergence
        else:
            momentum_score = 30.0  # Low momentum if insufficient data

        # 3. Engagement Score (log-scaled)
        eng_score = min(100.0, math.log1p(total_engagement) * 12.0)

        # 4. Cross-Platform Score (0 - 100)
        cross_plat_score = self.calculate_cross_platform_score(platform_breakdown) * 100.0

        # 5. Recency Score (0 - 100)
        recency_score = self.calculate_recency_score(last_seen) * 100.0

        # Weighted composite trend score
        raw_trend_score = (
            (freq_score * self.w_freq) +
            (momentum_score * self.w_momentum) +
            (eng_score * self.w_eng) +
            (cross_plat_score * self.w_cross) +
            (recency_score * self.w_recency)
        )

        confidence = self.calculate_confidence(
            current_mentions, platform_breakdown, avg_classifier_confidence
        )

        # Confidence acts as a calibration factor: low confidence slightly reins in extreme scores
        calibrated_trend_score = round(raw_trend_score * (0.6 + 0.4 * confidence), 1)
        final_score = min(99.5, max(5.0, calibrated_trend_score))

        return {
            "trend_score": final_score,
            "momentum_score": round(momentum_score, 1),
            "growth_rate": growth_rate,
            "growth_status": growth_status,
            "confidence": confidence,
            "metrics": {
                "freq_score": round(freq_score, 1),
                "eng_score": round(eng_score, 1),
                "cross_plat_score": round(cross_plat_score, 1),
                "recency_score": round(recency_score, 1)
            }
        }


scoring_engine = TrendScoringEngine()
