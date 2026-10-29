import re
from typing import List, Dict, Tuple, Set, Optional
from app.ml.preprocessing import clean_text, tokenize, extract_ngrams


# Category Taxonomies mapping anchor trends to categories
FASHION_CATEGORY_MAP: Dict[str, str] = {
    # Canonical Concept Mappings
    "Wide-Leg & Baggy Denim": "Pants & Denim",
    "Cargo Pants & Utility Trousers": "Pants & Utility",
    "Relaxed Tailored Trousers": "Materials & Pants",
    "Relaxed Track Pants & Athleisure": "Pants & Utility",
    "Oversized Hoodies & Sweats": "Silhouettes & Tops",
    "Vintage Graphic Tees": "Silhouettes & Tops",
    "Sheer & Lace Tops": "Silhouettes & Tops",
    "Knit Polos & Vests": "Knitwear & Tops",
    "Cozy Knitwear & Sweaters": "Knitwear & Tops",
    "Tailored & Oversized Blazers": "Silhouettes & Tailoring",
    "Statement Leather & Outerwear": "Outerwear & Leather",
    "Puffer Jackets & Quilted Outerwear": "Outerwear & Utility",
    "Gorpcore & Outdoor Aesthetics": "Outerwear & Utility",
    "Chunky & Retro Sneakers": "Footwear",
    "Minimalist White Sneakers": "Footwear",
    "Chunky Lug-Sole Loafers": "Footwear",
    "Statement Boots": "Footwear",
    "Ballet Flats & Mary Janes": "Footwear",
    "Quiet Luxury & Old Money": "Aesthetics & Tailoring",
    "Vintage Streetwear & Y2K": "Aesthetics & Vintage",
    "Coquette & Balletcore": "Aesthetics & Subcultures",
    "Techwear & Functional Gear": "Aesthetics & Functional",
    "Maxi Dresses & Slip Silhouettes": "Skirts & Silhouettes",
    "Pleated & Maxi Skirts": "Skirts & Silhouettes",
    "Silver & Statement Jewelry": "Accessories",
    "Statement Accessories & Bags": "Accessories",
    "Minimalist Everyday Totes & Bags": "Accessories",
    "Sartorial Ties & Accents": "Accessories",

    # Exact Raw Term Backward Compatibility
    "oversized hoodie": "Silhouettes & Tops",
    "oversized hoodies": "Silhouettes & Tops",
    "wide-leg jeans": "Pants & Denim",
    "wide leg jeans": "Pants & Denim",
    "baggy jeans": "Pants & Denim",
    "loose-fit denim": "Pants & Denim",
    "cargo pants": "Pants & Utility",
    "vintage streetwear": "Aesthetics & Vintage",
    "minimalist sneakers": "Footwear",
    "quiet luxury": "Aesthetics & Tailoring",
    "old money style": "Aesthetics & Tailoring",
    "coquette fashion": "Aesthetics & Subcultures",
    "balletcore": "Aesthetics & Subcultures",
    "techwear": "Aesthetics & Functional",
    "gorpcore jacket": "Outerwear & Utility",
    "leather trench coat": "Outerwear & Leather",
    "chunky loafers": "Footwear",
    "cropped blazer": "Silhouettes & Tailoring",
    "knit polo": "Knitwear & Tops",
    "linen trousers": "Materials & Pants",
    "silver jewelry": "Accessories",
    "metallic accessories": "Accessories",
    "distressed denim": "Pants & Denim",
    "pleated skirt": "Skirts & Silhouettes",
    "bomber jacket": "Outerwear",
    "mary jane shoes": "Footwear"
}

# Synonym mapping dictionary for controlled normalization
SYNONYM_NORMALIZATION_MAP: Dict[str, str] = {
    # Denim & Jeans
    "baggy jeans": "Wide-Leg & Baggy Denim",
    "baggy denim": "Wide-Leg & Baggy Denim",
    "wide leg jeans": "Wide-Leg & Baggy Denim",
    "wide-leg jeans": "Wide-Leg & Baggy Denim",
    "wide leg denim": "Wide-Leg & Baggy Denim",
    "wide-leg denim": "Wide-Leg & Baggy Denim",
    "loose fit denim": "Wide-Leg & Baggy Denim",
    "loose denim": "Wide-Leg & Baggy Denim",
    "straight leg jeans": "Wide-Leg & Baggy Denim",
    "relaxed jeans": "Wide-Leg & Baggy Denim",
    "relaxed denim": "Wide-Leg & Baggy Denim",
    "baggy pants": "Wide-Leg & Baggy Denim",
    "distressed denim": "Wide-Leg & Baggy Denim",
    "distressed jeans": "Wide-Leg & Baggy Denim",
    "flared jeans": "Wide-Leg & Baggy Denim",
    "denim jeans": "Wide-Leg & Baggy Denim",

    # Trousers & Pants
    "cargo pants": "Cargo Pants & Utility Trousers",
    "cargo trousers": "Cargo Pants & Utility Trousers",
    "utility pants": "Cargo Pants & Utility Trousers",
    "utility trousers": "Cargo Pants & Utility Trousers",
    "parachute pants": "Cargo Pants & Utility Trousers",
    "combat pants": "Cargo Pants & Utility Trousers",
    "linen trousers": "Relaxed Tailored Trousers",
    "linen pants": "Relaxed Tailored Trousers",
    "tailored trousers": "Relaxed Tailored Trousers",
    "pleated trousers": "Relaxed Tailored Trousers",
    "dress trousers": "Relaxed Tailored Trousers",
    "track pants": "Relaxed Track Pants & Athleisure",
    "track trousers": "Relaxed Track Pants & Athleisure",
    "baggy track pants": "Relaxed Track Pants & Athleisure",
    "sweatpants": "Relaxed Track Pants & Athleisure",
    "joggers": "Relaxed Track Pants & Athleisure",

    # Hoodies & Tops
    "oversized hoodie": "Oversized Hoodies & Sweats",
    "oversized hoodies": "Oversized Hoodies & Sweats",
    "baggy hoodie": "Oversized Hoodies & Sweats",
    "boxy hoodie": "Oversized Hoodies & Sweats",
    "fleece hoodie": "Oversized Hoodies & Sweats",
    "hooded sweatshirt": "Oversized Hoodies & Sweats",
    "oversized sweatshirt": "Oversized Hoodies & Sweats",
    "hoodie": "Oversized Hoodies & Sweats",
    "hoodies": "Oversized Hoodies & Sweats",
    "graphic tee": "Vintage Graphic Tees",
    "graphic t-shirt": "Vintage Graphic Tees",
    "graphic t-shirts": "Vintage Graphic Tees",
    "vintage tee": "Vintage Graphic Tees",
    "oversized tee": "Vintage Graphic Tees",
    "sheer blouse": "Sheer & Lace Tops",
    "sheer top": "Sheer & Lace Tops",
    "mesh top": "Sheer & Lace Tops",
    "lace blouse": "Sheer & Lace Tops",
    "lace top": "Sheer & Lace Tops",
    "knit polo": "Knit Polos & Vests",
    "knit vest": "Knit Polos & Vests",
    "crochet top": "Knit Polos & Vests",

    # Knitwear
    "knit sweater": "Cozy Knitwear & Sweaters",
    "knitwear": "Cozy Knitwear & Sweaters",
    "cable knit": "Cozy Knitwear & Sweaters",
    "cozy knitwear": "Cozy Knitwear & Sweaters",
    "pullover sweater": "Cozy Knitwear & Sweaters",
    "knit pullover": "Cozy Knitwear & Sweaters",
    "wool sweater": "Cozy Knitwear & Sweaters",
    "cardigan sweater": "Cozy Knitwear & Sweaters",
    "chunky knit": "Cozy Knitwear & Sweaters",
    "cardigan": "Cozy Knitwear & Sweaters",
    "sweater": "Cozy Knitwear & Sweaters",

    # Outerwear & Blazers
    "oversized blazer": "Tailored & Oversized Blazers",
    "tailored blazer": "Tailored & Oversized Blazers",
    "cropped blazer": "Tailored & Oversized Blazers",
    "boxy blazer": "Tailored & Oversized Blazers",
    "blazer": "Tailored & Oversized Blazers",
    "blazers": "Tailored & Oversized Blazers",
    "leather trench": "Statement Leather & Outerwear",
    "leather coat": "Statement Leather & Outerwear",
    "leather jacket": "Statement Leather & Outerwear",
    "leather trench coat": "Statement Leather & Outerwear",
    "biker jacket": "Statement Leather & Outerwear",
    "bomber jacket": "Statement Leather & Outerwear",
    "shearling coat": "Statement Leather & Outerwear",
    "outerwear": "Statement Leather & Outerwear",
    "puffer jacket": "Puffer Jackets & Quilted Outerwear",
    "quilted jacket": "Puffer Jackets & Quilted Outerwear",
    "down jacket": "Puffer Jackets & Quilted Outerwear",
    "gorpcore": "Gorpcore & Outdoor Aesthetics",
    "gorpcore jacket": "Gorpcore & Outdoor Aesthetics",
    "hiking aesthetic": "Gorpcore & Outdoor Aesthetics",

    # Footwear
    "chunky sneakers": "Chunky & Retro Sneakers",
    "dad shoes": "Chunky & Retro Sneakers",
    "retro sneakers": "Chunky & Retro Sneakers",
    "designer sneakers": "Chunky & Retro Sneakers",
    "platform sneakers": "Chunky & Retro Sneakers",
    "sneakers": "Chunky & Retro Sneakers",
    "sneaker": "Chunky & Retro Sneakers",
    "minimalist sneakers": "Minimalist White Sneakers",
    "clean white sneakers": "Minimalist White Sneakers",
    "court sneakers": "Minimalist White Sneakers",
    "chunky loafers": "Chunky Lug-Sole Loafers",
    "lug sole loafers": "Chunky Lug-Sole Loafers",
    "platform loafers": "Chunky Lug-Sole Loafers",
    "loafers": "Chunky Lug-Sole Loafers",
    "boots": "Statement Boots",
    "chunky boots": "Statement Boots",
    "chelsea boots": "Statement Boots",
    "cowboy boots": "Statement Boots",
    "mary jane shoes": "Ballet Flats & Mary Janes",
    "mary janes": "Ballet Flats & Mary Janes",
    "ballet flats": "Ballet Flats & Mary Janes",

    # Aesthetics
    "quiet luxury": "Quiet Luxury & Old Money",
    "old money": "Quiet Luxury & Old Money",
    "old money aesthetic": "Quiet Luxury & Old Money",
    "old money style": "Quiet Luxury & Old Money",
    "stealth wealth": "Quiet Luxury & Old Money",
    "vintage streetwear": "Vintage Streetwear & Y2K",
    "retro streetwear": "Vintage Streetwear & Y2K",
    "y2k fashion": "Vintage Streetwear & Y2K",
    "y2k streetwear": "Vintage Streetwear & Y2K",
    "streetwear": "Vintage Streetwear & Y2K",
    "coquette aesthetic": "Coquette & Balletcore",
    "coquette fashion": "Coquette & Balletcore",
    "balletcore": "Coquette & Balletcore",
    "ballet core": "Coquette & Balletcore",
    "bow aesthetic": "Coquette & Balletcore",
    "techwear": "Techwear & Functional Gear",
    "cyberpunk techwear": "Techwear & Functional Gear",

    # Dresses & Skirts
    "slip dress": "Maxi Dresses & Slip Silhouettes",
    "maxi dress": "Maxi Dresses & Slip Silhouettes",
    "dress designs": "Maxi Dresses & Slip Silhouettes",
    "dress": "Maxi Dresses & Slip Silhouettes",
    "dresses": "Maxi Dresses & Slip Silhouettes",
    "pleated skirt": "Pleated & Maxi Skirts",
    "maxi skirt": "Pleated & Maxi Skirts",
    "cargo skirt": "Pleated & Maxi Skirts",
    "skirt": "Pleated & Maxi Skirts",

    # Accessories
    "silver jewelry": "Silver & Statement Jewelry",
    "chunky jewelry": "Silver & Statement Jewelry",
    "jewelry": "Silver & Statement Jewelry",
    "tote bag": "Minimalist Everyday Totes & Bags",
    "shoulder bag": "Minimalist Everyday Totes & Bags",
    "crossbody bag": "Minimalist Everyday Totes & Bags",
    "accessories": "Statement Accessories & Bags",
    "metallic accessories": "Statement Accessories & Bags",
    "neck tie": "Sartorial Ties & Accents",
    "tie trend": "Sartorial Ties & Accents"
}


class TrendExtractor:
    """Extracts candidate fashion trends, applies synonym normalization and categorizes terms."""
    
    def __init__(self):
        self.synonym_map = SYNONYM_NORMALIZATION_MAP
        self.category_map = FASHION_CATEGORY_MAP

    def extract_candidate_terms(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts matched fashion terms from text, maps them to normalized trend concepts
        and categories.
        """
        cleaned = clean_text(text)
        tokens = tokenize(cleaned, remove_stopwords=False)
        ngrams = extract_ngrams(tokens, min_n=1, max_n=3)
        
        extracted_results: List[Dict[str, str]] = []
        seen_normalized: Set[str] = set()

        # Check multi-word ngrams first for maximum specificity
        for ngram in sorted(ngrams, key=lambda x: len(x), reverse=True):
            # Check direct synonym map
            if ngram in self.synonym_map:
                normalized_name = self.synonym_map[ngram]
                if normalized_name not in seen_normalized:
                    category = self.find_category(ngram, normalized_name)
                    extracted_results.append({
                        "raw_term": ngram,
                        "normalized_name": normalized_name,
                        "category": category
                    })
                    seen_normalized.add(normalized_name)
            
            # Check pattern matches (e.g. [adjective] + [clothing])
            pattern_match = self._match_syntactic_pattern(ngram)
            if pattern_match and pattern_match not in seen_normalized:
                cat = self.find_category(ngram, pattern_match)
                extracted_results.append({
                    "raw_term": ngram,
                    "normalized_name": pattern_match,
                    "category": cat
                })
                seen_normalized.add(pattern_match)

        return extracted_results

    def _match_syntactic_pattern(self, phrase: str) -> Optional[str]:
        """Heuristic syntactic pattern matching for compound fashion terms."""
        modifiers = r"(oversized|baggy|wide-leg|wide leg|cropped|chunky|relaxed|vintage|minimalist|quilted|pleated|distressed|sheer|knit|leather|cargo|graphic|boxy|lug-sole|lug sole|retro|cozy|metallic|corduroy|linen|puffer|slip|maxi|flared|tailored|denim|streetwear)"
        items = r"(hoodie|hoodies|jeans|pants|trousers|jacket|jackets|blazer|blazers|sweater|sweaters|pullover|pullovers|cardigan|cardigans|sneakers|shoes|boots|loafers|tote|totes|vest|vests|coat|coats|tee|tees|t-shirt|t-shirts|skirt|skirts|dress|dresses|accessories|jewelry)"
        match = re.search(rf"\b{modifiers}\s+{items}\b", phrase, re.IGNORECASE)
        if match:
            matched_phrase = match.group(0).lower()
            # If the syntactic match corresponds to a known normalized concept, prioritize canonical name
            if matched_phrase in self.synonym_map:
                return self.synonym_map[matched_phrase]
            # Capitalize words
            return " ".join([word.capitalize() for word in matched_phrase.split()])
        return None

    def find_category(self, raw_term: str, normalized_name: str) -> str:
        """Assigns category based on taxonomy lookup or keyword inference."""
        if raw_term in self.category_map:
            return self.category_map[raw_term]
        if normalized_name in self.category_map:
            return self.category_map[normalized_name]
            
        norm_lower = normalized_name.lower()
        if any(w in norm_lower for w in ["denim", "jean", "pant", "trouser"]):
            return "Pants & Denim"
        if any(w in norm_lower for w in ["hoodie", "sweat", "shirt", "tee", "top"]):
            return "Silhouettes & Tops"
        if any(w in norm_lower for w in ["jacket", "coat", "blazer", "outerwear", "trench"]):
            return "Outerwear"
        if any(w in norm_lower for w in ["sneaker", "boot", "loafer", "shoe"]):
            return "Footwear"
        if any(w in norm_lower for w in ["luxury", "money", "coquette", "streetwear", "techwear", "gorpcore", "vintage", "y2k"]):
            return "Aesthetics & Subcultures"
        if any(w in norm_lower for w in ["linen", "leather", "knit", "silk", "wool"]):
            return "Materials & Textures"
        if any(w in norm_lower for w in ["jewelry", "bag", "tote", "belt", "accessory", "tie"]):
            return "Accessories"
            
        return "Contemporary Streetwear"


trend_extractor = TrendExtractor()
