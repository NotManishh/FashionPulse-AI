from app.ml.trend_extractor import trend_extractor


def test_trend_extractor_synonym_normalization():
    text = "Loving these baggy jeans and oversized hoodie fits for the weekend."
    results = trend_extractor.extract_candidate_terms(text)
    normalized_names = [r["normalized_name"] for r in results]
    
    assert "Wide-Leg & Baggy Denim" in normalized_names
    assert "Oversized Hoodies & Sweats" in normalized_names


def test_trend_extractor_category_assignment():
    text = "Quiet luxury with clean white minimalist sneakers and relaxed linen trousers."
    results = trend_extractor.extract_candidate_terms(text)
    categories = {r["normalized_name"]: r["category"] for r in results}
    
    assert categories.get("Quiet Luxury & Old Money") == "Aesthetics & Tailoring"
    assert "Footwear" in categories.values() or "Materials & Pants" in categories.values()


def test_trend_extractor_syntactic_patterns():
    text = "Check out this vintage jacket and pleated skirt."
    results = trend_extractor.extract_candidate_terms(text)
    names = [r["normalized_name"] for r in results]
    assert any("Vintage Jacket" in n or "Pleated Skirt" in n for n in names)
