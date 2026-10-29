from app.ml.clustering import trend_clusterer


def test_cluster_expressions_similar_terms():
    candidates = [
        {"normalized_name": "Wide-Leg & Baggy Denim", "raw_term": "wide-leg jeans", "count": 15, "category": "Pants & Denim"},
        {"normalized_name": "Wide-Leg & Baggy Denim", "raw_term": "loose fit denim", "count": 10, "category": "Pants & Denim"},
        {"normalized_name": "Cargo Pants & Utility Trousers", "raw_term": "cargo pants", "count": 8, "category": "Pants & Utility"}
    ]
    clusters = trend_clusterer.cluster_expressions(candidates)
    
    # Should cluster the denim terms together and separate cargo pants
    cluster_names = [c["primary_name"] for c in clusters]
    assert "Wide-Leg & Baggy Denim" in cluster_names
    assert "Cargo Pants & Utility Trousers" in cluster_names
    
    # Check total mentions
    denim_cluster = next(c for c in clusters if c["primary_name"] == "Wide-Leg & Baggy Denim")
    assert denim_cluster["total_mentions"] == 25


def test_cluster_expressions_empty():
    clusters = trend_clusterer.cluster_expressions([])
    assert clusters == []
