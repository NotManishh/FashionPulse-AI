from app.ml.preprocessing import clean_text, tokenize, extract_ngrams


def test_clean_text():
    raw_text = "Check out this #vintage hoodie at https://example.com/item?id=42 &amp; wide-leg jeans!!"
    cleaned = clean_text(raw_text)
    assert "https" not in cleaned
    assert "vintage" in cleaned
    assert "hoodie" in cleaned
    assert "wide-leg" in cleaned
    assert "&amp;" not in cleaned


def test_tokenize():
    text = "The oversized blazer and baggy jeans are trending on TikTok"
    tokens = tokenize(text, remove_stopwords=True)
    assert "oversized" in tokens
    assert "blazer" in tokens
    assert "baggy" in tokens
    assert "jeans" in tokens
    assert "the" not in tokens
    assert "and" not in tokens


def test_extract_ngrams():
    tokens = ["oversized", "hoodie", "streetwear"]
    ngrams = extract_ngrams(tokens, min_n=1, max_n=2)
    assert "oversized" in ngrams
    assert "oversized hoodie" in ngrams
    assert "hoodie streetwear" in ngrams
