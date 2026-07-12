"""Depreciation Engine — compute price by age, annual depreciation, mileage-adjusted."""

import statistics
from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.models import DepreciationCurve


class DepreciationEngine:
    def __init__(self, query: QueryEngine, max_age: int = 15):
        self._query = query; self._max_age = max_age

    def compute(self, make: str, model: str,
                marketplace: str = "") -> DepreciationCurve:
        f = FilterCriteria(make=make, model=model, marketplace=marketplace)
        all_listings = self._get_all(f)

        # Group by year to compute average price per age
        import datetime
        current_year = datetime.datetime.now().year
        age_prices: dict[int, list[float]] = {}
        for listing in all_listings:
            year = listing.data.get("year", 0) if hasattr(listing, 'data') else 0
            if year <= 0: continue
            age = current_year - year
            if 0 <= age <= self._max_age:
                age_prices.setdefault(age, []).append(listing.price)

        data_points = []
        for age in sorted(age_prices.keys()):
            prices = age_prices[age]
            avg = sum(prices) / len(prices)
            data_points.append({"age_years": age, "avg_price": round(avg),
                              "sample_count": len(prices)})

        # Compute annual depreciation from year 0 to oldest
        annual = 0.0
        if len(data_points) >= 2:
            y0 = data_points[0]
            yn = data_points[-1]
            years = yn["age_years"] - y0["age_years"]
            if years > 0 and y0["avg_price"] > 0:
                total_drop = (y0["avg_price"] - yn["avg_price"]) / y0["avg_price"]
                annual = (total_drop / years) * 100

        # Mileage factor: avg price difference per 10k km
        mileage_factor = 0.0
        if len(all_listings) >= 2:
            mileages = [(e.mileage_km, e.price) for e in all_listings if e.mileage_km > 0]
            if len(mileages) >= 2:
                mileages.sort()
                lo = mileages[:len(mileages)//2]
                hi = mileages[len(mileages)//2:]
                avg_lo = sum(p for _, p in lo) / len(lo)
                avg_hi = sum(p for _, p in hi) / len(hi)
                km_diff = (sum(m for m, _ in hi) / len(hi)) - (sum(m for m, _ in lo) / len(lo))
                if km_diff > 0:
                    mileage_factor = (avg_lo - avg_hi) / (km_diff / 10000)

        return DepreciationCurve(
            make=make, model=model,
            avg_annual_depreciation_pct=round(annual, 1),
            data_points=data_points,
            mileage_factor=round(mileage_factor, 1),
        )

    def _get_all(self, f):
        try:
            return list(self._query._repo._current._store.values())
        except Exception:
            return []
