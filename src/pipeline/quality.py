def score_quality(data: dict) -> tuple[int, list[str]]:
    score = 100
    flags = []

    optional_fields = ["mileage_km", "spec", "trim", "body_type",
                       "transmission", "fuel_type", "color", "seller_type"]
    for field in optional_fields:
        if data.get(field) is None:
            score -= 5
            flags.append(f"missing_{field}")

    mileage = data.get("mileage_km")
    if mileage and mileage > 400_000:
        score -= 10
        flags.append("mileage_outlier")

    year = data.get("year")
    if year and year < 1995:
        score -= 15
        flags.append("year_anomaly")

    if not data.get("body_type") and not data.get("trim"):
        score -= 5
        flags.append("sparse_listing")

    price = data.get("normalized_price_aed", data.get("asking_price", 0))
    if price < 1000:
        score -= 30
        flags.append("price_too_low")
    elif price > 5_000_000:
        score -= 20
        flags.append("price_too_high")

    return max(score, 0), flags
