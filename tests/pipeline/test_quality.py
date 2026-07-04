from src.pipeline.quality import score_quality

def test_perfect_listing_scores_100():
    data = {"make": "Toyota", "model": "Camry", "year": 2020,
            "mileage_km": 50000, "spec": "GCC", "trim": "GLE",
            "body_type": "sedan", "transmission": "automatic",
            "fuel_type": "petrol", "color": "white", "seller_type": "private",
            "normalized_price_aed": 75000}
    score, flags = score_quality(data)
    assert score == 100

def test_missing_fields_penalize():
    data = {"make": "Toyota", "model": "Camry", "year": 2020,
            "normalized_price_aed": 75000}
    score, flags = score_quality(data)
    assert score < 100
    assert any("missing_" in f for f in flags)

def test_price_too_low_penalizes():
    data = {"make": "Toyota", "model": "Camry", "year": 2020,
            "normalized_price_aed": 500}
    score, flags = score_quality(data)
    assert "price_too_low" in flags
    assert score <= 70

def test_score_never_negative():
    data = {"normalized_price_aed": 500}
    score, flags = score_quality(data)
    assert score >= 0
