from typing import Tuple, Set
from app.ml.preprocessing import tokenize, clean_text


# High-signal fashion seed lexicon
FASHION_KEYWORDS: Set[str] = {
    # Garments & Silhouettes
    "hoodie", "hoodies", "jeans", "denim", "pants", "trousers", "jacket", "coat", "blazer",
    "skirt", "dress", "corset", "trench", "oversized", "baggy", "cargo", "wide-leg", "slim-fit",
    "cropped", "cardigan", "sweater", "knitwear", "bomber", "puffer", "vest", "tee", "shirt",
    # Aesthetics & Subcultures
    "streetwear", "coquette", "quiet luxury", "old money", "techwear", "balletcore", "gorpcore",
    "vintage", "y2k", "minimalist", "grunge", "boho", "cottagecore", "cyberpunk", "academia",
    "grunge", "preppy", "athleisure", "monochrome", "retro", "avant-garde",
    # Materials & Patterns
    "leather", "linen", "silk", "suede", "velvet", "tweed", "cashmere", "corduroy", "shearling",
    "houndstooth", "plaid", "stripes", "floral", "distressed", "pleated", "chunky",
    # Footwear & Accessories
    "sneakers", "boots", "loafers", "mules", "sandals", "tote", "handbag", "beret", "beanie",
    "shades", "sunglasses", "jewelry", "belt", "scarf", "chunky sneakers", "mary janes",
    # Styling verbs & descriptors
    "outfit", "ootd", "fit", "styling", "silhouette", "wardrobe", "aesthetic", "layering",
    "haul", "thrifted", "drape", "tailored", "runway", "couture", "apparel"
}

# Non-fashion noise triggers
NON_FASHION_INDICATORS: Set[str] = {
    "cryptocurrency", "bitcoin", "gpu", "nvidia", "rtx", "cpu", "gaming", "steam",
    "politics", "election", "senate", "football", "nba", "recipe", "cooking", "crypto",
    "stock market", "shares", "dividend", "car engine", "exhaust"
}


class FashionClassifier:
    """Classifies social media text as fashion-related or non-fashion with confidence score."""
    
    def __init__(self, confidence_threshold: float = 0.35):
        self.confidence_threshold = confidence_threshold
        self.fashion_lexicon = FASHION_KEYWORDS
        self.negative_lexicon = NON_FASHION_INDICATORS

    def classify(self, text: str) -> Tuple[bool, float]:
        """
        Evaluates text and returns (is_fashion_related, confidence_score).
        Confidence is bounded [0.0, 1.0].
        """
        if not text or len(text.strip()) < 5:
            return False, 0.0
            
        cleaned = clean_text(text)
        tokens = tokenize(cleaned, remove_stopwords=True)
        if not tokens:
            return False, 0.0
            
        token_set = set(tokens)
        
        # Count positive matches
        direct_matches = len(token_set.intersection(self.fashion_lexicon))
        
        # Check phrase matches (e.g. "quiet luxury", "wide-leg", "old money")
        phrase_matches = 0
        for multi_word in ["quiet luxury", "old money", "wide-leg", "wide leg", "chunky knit", "ballet core", "mary jane"]:
            if multi_word in cleaned:
                phrase_matches += 2
                
        # Count negative matches
        negative_matches = len(token_set.intersection(self.negative_lexicon))
        
        total_signals = direct_matches + phrase_matches
        
        if total_signals == 0:
            return False, 0.05
            
        # Compute confidence based on signal density and negative penalty
        raw_score = (total_signals * 0.28) / (1.0 + (negative_matches * 0.5))
        confidence = min(0.99, max(0.0, raw_score))
        
        # Require higher signal if negative noise is detected
        if negative_matches > direct_matches:
            confidence *= 0.4
            
        is_fashion = confidence >= self.confidence_threshold
        return is_fashion, round(confidence, 3)


fashion_classifier = FashionClassifier()
