from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TrendClusterer:
    """
    Groups semantically similar candidate fashion expressions into cohesive trend clusters
    using exact canonical normalization and TF-IDF n-gram vectors with cosine similarity.
    """
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold

    def cluster_expressions(self, candidate_terms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes candidate terms with count/frequency information and clusters similar ones.
        Returns aggregated clusters with primary representative name, supporting terms, and count.
        """
        if not candidate_terms:
            return []

        # 1. First consolidate exact identical normalized_name entries
        consolidated: Dict[str, Dict[str, Any]] = {}
        for item in candidate_terms:
            norm_name = item["normalized_name"]
            if norm_name not in consolidated:
                consolidated[norm_name] = {
                    "normalized_name": norm_name,
                    "category": item.get("category", "Contemporary Fashion"),
                    "supporting_terms": set(),
                    "occurrences": [],
                    "total_mentions": 0,
                    "platforms": {},
                    "engagement_total": 0.0,
                    "references": [],
                    "latest_timestamp": None
                }
            entry = consolidated[norm_name]
            raw_t = item.get("raw_term") or norm_name
            entry["supporting_terms"].add(raw_t)
            entry["occurrences"].append(item)
            entry["total_mentions"] += item.get("count", 1)
            for plat, cnt in item.get("platforms", {}).items():
                entry["platforms"][plat] = entry["platforms"].get(plat, 0) + cnt
            entry["engagement_total"] += item.get("engagement_total", 0.0)
            entry["references"].extend(item.get("references", []))
            ts = item.get("latest_timestamp")
            if ts and (entry["latest_timestamp"] is None or ts > entry["latest_timestamp"]):
                entry["latest_timestamp"] = ts

        canonical_items = list(consolidated.values())
        if len(canonical_items) <= 1:
            if not canonical_items:
                return []
            it = canonical_items[0]
            return [{
                "primary_name": it["normalized_name"],
                "category": it["category"],
                "supporting_terms": list(it["supporting_terms"]),
                "occurrences": it["occurrences"],
                "total_mentions": it["total_mentions"],
                "platforms": it["platforms"],
                "engagement_total": it["engagement_total"],
                "references": it["references"][:5],
                "latest_timestamp": it["latest_timestamp"]
            }]

        term_strings = [it["normalized_name"] for it in canonical_items]
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        try:
            tfidf_matrix = vectorizer.fit_transform(term_strings)
            sim_matrix = cosine_similarity(tfidf_matrix)
        except Exception:
            sim_matrix = np.eye(len(term_strings))

        n_terms = len(term_strings)
        visited = set()
        clusters: List[Dict[str, Any]] = []

        for i in range(n_terms):
            if i in visited:
                continue

            cluster_indices = [i]
            visited.add(i)

            for j in range(i + 1, n_terms):
                if j not in visited and sim_matrix[i, j] >= self.similarity_threshold:
                    cluster_indices.append(j)
                    visited.add(j)

            cluster_group = [canonical_items[idx] for idx in cluster_indices]
            primary_item = max(cluster_group, key=lambda x: x["total_mentions"])
            primary_name = primary_item["normalized_name"]
            category = primary_item["category"]

            combined_supporting = set()
            combined_occurrences = []
            combined_mentions = 0
            combined_platforms: Dict[str, int] = {}
            combined_engagement = 0.0
            combined_refs = []
            latest_time = None

            for it in cluster_group:
                combined_supporting.update(it["supporting_terms"])
                combined_occurrences.extend(it["occurrences"])
                combined_mentions += it["total_mentions"]
                for p, c in it["platforms"].items():
                    combined_platforms[p] = combined_platforms.get(p, 0) + c
                combined_engagement += it["engagement_total"]
                combined_refs.extend(it["references"])
                if it["latest_timestamp"] and (latest_time is None or it["latest_timestamp"] > latest_time):
                    latest_time = it["latest_timestamp"]

            clusters.append({
                "primary_name": primary_name,
                "category": category,
                "supporting_terms": list(combined_supporting),
                "occurrences": combined_occurrences,
                "total_mentions": combined_mentions,
                "platforms": combined_platforms,
                "engagement_total": combined_engagement,
                "references": combined_refs[:5],
                "latest_timestamp": latest_time
            })

        # Sort clusters by total mentions
        clusters.sort(key=lambda c: c["total_mentions"], reverse=True)
        return clusters


trend_clusterer = TrendClusterer()
