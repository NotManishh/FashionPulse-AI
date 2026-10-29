import re
import html
import unicodedata
from typing import List, Set


# Standard English stopwords minus fashion-informative qualifiers (e.g. over, under, wide)
BASIC_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "own", "s", "same", "she", "should", 
    "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "until", "up", 
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", 
    "will", "with", "you", "your", "yours", "yourself", "yourselves", "http", "https", "com", 
    "www", "subscribe", "video", "channel", "link", "bio", "check", "click", "comment", "like", 
    "post", "share", "follow", "reddit", "instagram", "youtube", "hey", "guys", "today"
}


def clean_text(text: str) -> str:
    """Cleans and standardizes raw social media text."""
    if not text:
        return ""
    
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    
    # Replace hashtags by separating words if needed, but preserve hashtag keyword
    text = re.sub(r"#([a-zA-Z0-9_]+)", r" \1 ", text)
    
    # Replace newlines, tabs and special chars with space
    text = re.sub(r"[^a-zA-Z0-9\s\-]", " ", text)
    
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip().lower()
    
    return text


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    """Tokenizes cleaned text into lowercase word tokens."""
    cleaned = clean_text(text)
    tokens = [t.strip("-") for t in cleaned.split() if len(t.strip("-")) > 1]
    
    if remove_stopwords:
        tokens = [t for t in tokens if t not in BASIC_STOPWORDS]
        
    return tokens


def extract_ngrams(tokens: List[str], min_n: int = 1, max_n: int = 3) -> List[str]:
    """Extracts contiguous n-grams from tokens."""
    ngrams = []
    n_tokens = len(tokens)
    for n in range(min_n, max_n + 1):
        for i in range(n_tokens - n + 1):
            ngram = " ".join(tokens[i:i + n])
            ngrams.append(ngram)
    return ngrams
