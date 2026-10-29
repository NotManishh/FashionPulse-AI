import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from app.models.entities import CollectedContent, Trend, TrendObservation
from app.ml.clustering import trend_clusterer
from app.ml.scoring import scoring_engine
from app.ml.trend_extractor import trend_extractor
from app.schemas.nemotron import NemotronPayload, NemotronTrendItem
from app.core.logging import logger


def ensure_utc(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class TrendService:
    """Discovers trends from collected content, computes rankings and generates Nemotron payloads."""

    async def detect_and_update_trends(
        self, db: AsyncSession, days_window: int = 7
    ) -> List[Trend]:
        """
        Processes content from the current window, compares against baseline window,
        clusters expressions, computes scores, and updates the top 10 trends.
        """
        now = datetime.now(timezone.utc)
        current_window_start = now - timedelta(days=days_window)
        baseline_window_start = current_window_start - timedelta(days=days_window)

        # Check if live social content exists in the database
        live_count_res = await db.execute(
            select(func.count(CollectedContent.id)).where(CollectedContent.is_demo == False)
        )
        has_live_records = (live_count_res.scalar() or 0) > 0

        # If live records exist, analyze genuine live social content only
        # If no live records exist yet, fall back to analyzing demo content
        demo_filter = (CollectedContent.is_demo == False) if has_live_records else (CollectedContent.is_demo == True)

        # 1. Fetch current window fashion-related content
        curr_stmt = select(CollectedContent).where(
            and_(
                CollectedContent.published_at >= current_window_start,
                CollectedContent.is_fashion_related == True,
                demo_filter
            )
        )
        curr_result = await db.execute(curr_stmt)
        curr_items = curr_result.scalars().all()

        if not curr_items:
            logger.info("No fashion content found in current window to extract trends.")
            # Return current active trends if available
            existing_trends = await db.execute(
                select(Trend).where(Trend.is_active == True).order_by(Trend.current_rank.asc().nullslast())
            )
            return list(existing_trends.scalars().all())

        # 2. Fetch baseline window items to calculate growth rates
        base_stmt = select(CollectedContent).where(
            and_(
                CollectedContent.published_at >= baseline_window_start,
                CollectedContent.published_at < current_window_start,
                CollectedContent.is_fashion_related == True,
                demo_filter
            )
        )
        base_result = await db.execute(base_stmt)
        base_items = base_result.scalars().all()

        # Build baseline term mention dictionary
        baseline_counts: Dict[str, int] = {}
        for b_item in base_items:
            b_extracted = trend_extractor.extract_candidate_terms(b_item.content_text)
            b_terms = [c["normalized_name"] for c in b_extracted] if b_extracted else (b_item.extracted_terms or [])
            for term in b_terms:
                baseline_counts[term] = baseline_counts.get(term, 0) + 1

        # 3. Aggregate candidate terms in current window
        candidate_term_map: Dict[str, Dict[str, Any]] = {}
        for c_item in curr_items:
            c_pub_date = ensure_utc(c_item.published_at)
            # Dynamically extract fashion terms from content_text to reflect current taxonomy
            extracted = trend_extractor.extract_candidate_terms(c_item.content_text)
            terms = [c["normalized_name"] for c in extracted]
            if terms:
                c_item.extracted_terms = terms
            else:
                terms = c_item.extracted_terms or []

            for term in terms:
                if term not in candidate_term_map:
                    candidate_term_map[term] = {
                        "normalized_name": term,
                        "raw_term": term,
                        "category": trend_extractor.find_category(term, term),
                        "count": 0,
                        "platforms": {},
                        "engagement_total": 0.0,
                        "references": [],
                        "latest_timestamp": c_pub_date
                    }
                
                entry = candidate_term_map[term]
                entry["count"] += 1
                entry["platforms"][c_item.platform] = entry["platforms"].get(c_item.platform, 0) + 1
                entry["engagement_total"] += c_item.normalized_engagement
                if c_item.permalink and len(entry["references"]) < 3:
                    entry["references"].append(c_item.permalink)
                if c_pub_date > entry["latest_timestamp"]:
                    entry["latest_timestamp"] = c_pub_date

        # 4. Cluster related candidate terms
        candidate_list = list(candidate_term_map.values())
        clusters = trend_clusterer.cluster_expressions(candidate_list)

        # 5. Score each cluster
        scored_trends_data = []
        total_sample = len(curr_items)

        for cluster in clusters:
            primary_name = cluster["primary_name"]
            total_mentions = cluster["total_mentions"]
            
            # Combine platform breakdowns and references across cluster items
            combined_platforms = dict(cluster.get("platforms") or {})
            combined_engagement = cluster.get("engagement_total", 0.0)
            combined_refs = list(cluster.get("references") or [])
            latest_time = cluster.get("latest_timestamp") or current_window_start

            if not combined_platforms:
                for occ in cluster["occurrences"]:
                    for plat, cnt in occ.get("platforms", {}).items():
                        combined_platforms[plat] = combined_platforms.get(plat, 0) + cnt
                    combined_engagement += occ.get("engagement_total", 0.0)
                    combined_refs.extend(occ.get("references", []))
                    occ_ts = ensure_utc(occ.get("latest_timestamp"))
                    if occ_ts and occ_ts > latest_time:
                        latest_time = occ_ts

            baseline_mentions = baseline_counts.get(primary_name, 0)

            score_data = scoring_engine.calculate_trend_score(
                current_mentions=total_mentions,
                baseline_mentions=baseline_mentions,
                total_engagement=combined_engagement,
                platform_breakdown=combined_platforms,
                last_seen=latest_time,
                total_sample_size=total_sample,
                baseline_sample_size=len(base_items),
                is_baseline_comparable=False
            )

            scored_trends_data.append({
                "name": primary_name,
                "category": cluster["category"],
                "total_mentions": total_mentions,
                "total_engagement": combined_engagement,
                "platform_breakdown": combined_platforms,
                "supporting_keywords": cluster["supporting_terms"][:8],
                "representative_references": combined_refs[:3],
                "last_seen": latest_time,
                "score_info": score_data
            })

        # Sort globally descending by computed trend_score, with momentum and confidence as documented tie-breakers
        scored_trends_data.sort(
            key=lambda x: (
                -x["score_info"]["trend_score"],
                -x["score_info"]["momentum_score"],
                -x["score_info"]["confidence"],
                x["name"]
            )
        )

        # 6. Upsert Trends and record historical observations
        persisted_trends: List[Trend] = []

        # Reset all existing ranks first so no stale ranks or duplicate ranks remain
        await db.execute(update(Trend).values(current_rank=None))
        await db.flush()

        for rank_idx, item_data in enumerate(scored_trends_data, start=1):
            name = item_data["name"]
            score_info = item_data["score_info"]
            is_top_10 = rank_idx <= 10

            result = await db.execute(select(Trend).where(Trend.name == name))
            trend_obj = result.scalar_one_or_none()

            if not trend_obj:
                trend_obj = Trend(
                    id=str(uuid.uuid4()),
                    name=name,
                    category=item_data["category"],
                    description=f"Trending aesthetic/silhouette characterized by {', '.join(item_data['supporting_keywords'][:3])}.",
                    first_seen=now - timedelta(days=days_window),
                    is_demo=not has_live_records
                )
                db.add(trend_obj)

            # Update trend metrics
            trend_obj.is_demo = not has_live_records
            trend_obj.category = item_data["category"]
            trend_obj.current_rank = rank_idx if is_top_10 else None
            trend_obj.current_score = score_info["trend_score"]
            trend_obj.confidence = score_info["confidence"]
            trend_obj.momentum_score = score_info["momentum_score"]
            trend_obj.growth_rate = score_info["growth_rate"]
            trend_obj.growth_status = score_info["growth_status"]
            trend_obj.mention_count = item_data["total_mentions"]
            trend_obj.total_engagement = item_data["total_engagement"]
            trend_obj.platform_breakdown = item_data["platform_breakdown"]
            trend_obj.last_seen = item_data["last_seen"]
            trend_obj.time_window = f"{days_window}d"
            trend_obj.supporting_keywords = item_data["supporting_keywords"]
            trend_obj.representative_references = item_data["representative_references"]
            trend_obj.is_active = True
            trend_obj.updated_at = now

            await db.flush()

            # Record historical observation snapshot
            observation = TrendObservation(
                id=str(uuid.uuid4()),
                trend_id=trend_obj.id,
                observation_window_start=current_window_start,
                observation_window_end=now,
                mention_count=item_data["total_mentions"],
                engagement_score=item_data["total_engagement"],
                trend_score=score_info["trend_score"],
                platform="aggregated",
                recorded_at=now
            )
            db.add(observation)

            persisted_trends.append(trend_obj)

        await db.commit()
        return [t for t in persisted_trends if t.current_rank is not None]

    async def get_top_10_trends(self, db: AsyncSession) -> List[Trend]:
        """Returns the current ranked top 10 trends strictly ordered by score descending."""
        live_count_res = await db.execute(
            select(func.count(CollectedContent.id)).where(CollectedContent.is_demo == False)
        )
        has_live_records = (live_count_res.scalar() or 0) > 0
        demo_filter = (Trend.is_demo == False) if has_live_records else (Trend.is_demo == True)

        stmt = select(Trend).where(
            and_(
                Trend.current_rank.isnot(None),
                Trend.is_active == True,
                demo_filter
            )
        ).order_by(
            Trend.current_rank.asc(),
            Trend.current_score.desc(),
            Trend.momentum_score.desc(),
            Trend.confidence.desc()
        ).limit(10)
        
        result = await db.execute(stmt)
        trends = list(result.scalars().all())

        # Verify integrity: ensure no duplicate ranks, sequential ranks, and accurate live/demo partition
        ranks = [t.current_rank for t in trends]
        has_duplicates = len(ranks) != len(set(ranks))
        has_mismatch = any(t.is_demo != (not has_live_records) for t in trends)

        if not trends or has_duplicates or has_mismatch:
            trends = await self.detect_and_update_trends(db)

        # Guarantee unique sequential order by rank ascending
        sorted_top = sorted(
            [t for t in trends if t.current_rank is not None],
            key=lambda x: (
                x.current_rank if x.current_rank is not None else 999,
                -x.current_score,
                -x.momentum_score,
                -x.confidence
            )
        )[:10]

        return sorted_top

    async def get_trend_history(self, db: AsyncSession, trend_id: str) -> List[TrendObservation]:
        """Returns historical observation snapshots for a trend."""
        stmt = select(TrendObservation).where(
            TrendObservation.trend_id == trend_id
        ).order_by(TrendObservation.recorded_at.asc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def build_nemotron_payload(self, db: AsyncSession) -> NemotronPayload:
        """Constructs downstream JSON payload for NVIDIA Nemotron model."""
        top_trends = await self.get_top_10_trends(db)
        
        # Check observations counts by live and demo
        live_obs_res = await db.execute(
            select(func.count(CollectedContent.id)).where(
                CollectedContent.is_fashion_related == True,
                CollectedContent.is_demo == False
            )
        )
        live_obs = live_obs_res.scalar() or 0

        demo_obs_res = await db.execute(
            select(func.count(CollectedContent.id)).where(
                CollectedContent.is_fashion_related == True,
                CollectedContent.is_demo == True
            )
        )
        demo_obs = demo_obs_res.scalar() or 0

        has_live = live_obs > 0
        data_mode = "live_youtube" if has_live else "demo"

        # Determine actual source platforms exclusively from active trend observations
        active_platforms = set()
        for t in top_trends:
            for plat, cnt in (t.platform_breakdown or {}).items():
                if cnt > 0:
                    active_platforms.add(plat)
        if not active_platforms:
            active_platforms = {"youtube"} if has_live else {"reddit", "instagram", "youtube"}

        trend_items: List[NemotronTrendItem] = []
        for t in top_trends:
            trend_items.append(
                NemotronTrendItem(
                    rank=t.current_rank or 1,
                    trend_name=t.name,
                    trend_score=t.current_score,
                    confidence=t.confidence,
                    momentum_score=t.momentum_score,
                    mention_count=t.mention_count,
                    platform_breakdown=t.platform_breakdown or {},
                    growth_rate=t.growth_rate,
                    category=t.category,
                    supporting_keywords=t.supporting_keywords or [],
                    is_demo=bool(t.is_demo)
                )
            )

        return NemotronPayload(
            generated_at=datetime.now(timezone.utc).isoformat(),
            time_window="7d",
            source_platforms=sorted(list(active_platforms)),
            total_observations_analyzed=live_obs if has_live else demo_obs,
            data_mode=data_mode,
            live_observations_count=live_obs,
            demo_observations_count=demo_obs,
            trends=trend_items,
            metadata={
                "scoring_engine": "FashionPulse-Composite-v1.0",
                "normalization": "logarithmic_cross_platform",
                "data_mode": data_mode,
                "is_demo_mode": not has_live,
                "active_platforms": sorted(list(active_platforms))
            }
        )


trend_service = TrendService()
