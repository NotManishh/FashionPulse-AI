from app.ml.fashion_classifier import fashion_classifier


def test_fashion_classifier_positive():
    fashion_post = "Heavyweight oversized hoodie paired with baggy wide-leg denim and minimalist sneakers for autumn styling."
    is_fashion, confidence = fashion_classifier.classify(fashion_post)
    assert is_fashion is True
    assert confidence > 0.4


def test_fashion_classifier_quiet_luxury():
    luxury_post = "Exploring quiet luxury aesthetic: cashmere knitwear, relaxed linen trousers, and subtle loafers."
    is_fashion, confidence = fashion_classifier.classify(luxury_post)
    assert is_fashion is True
    assert confidence > 0.4


def test_fashion_classifier_negative_crypto_gaming():
    crypto_post = "Nvidia RTX 5090 GPU benchmarks running Cyberpunk 2077 with bitcoin mining performance in background."
    is_fashion, confidence = fashion_classifier.classify(crypto_post)
    assert is_fashion is False
    assert confidence < 0.35


def test_fashion_classifier_empty():
    is_fashion, confidence = fashion_classifier.classify("")
    assert is_fashion is False
    assert confidence == 0.0
