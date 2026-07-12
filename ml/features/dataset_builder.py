"""Dataset Builder — builds reproducible, versioned ML datasets from historical data."""

import hashlib, json, time
from storage.history.repository import HistoryRepository
from analytics.query.query_engine import QueryEngine
from analytics.intelligence.intelligence_engine import IntelligenceEngine
from analytics.query.models import FilterCriteria
from ml.features.feature_store import FeatureStore
from ml.features.registry import FeatureRegistry
from ml.features.models import DatasetVersion, FeatureVector
from ml.features.validators import FeatureValidator
from ml.features.versioning import DatasetVersionManager
from ml.features.config import FeatureStoreConfig


class DatasetBuilder:
    """Builds versioned ML-ready datasets from historical and market intelligence data.

    Usage:
        builder = DatasetBuilder(repo, query_engine, intelligence)
        dataset = builder.build(
            make="Toyota", marketplace="dubizzle",
            snapshot_range=(start_ts, end_ts),
        )
        builder.export_csv(dataset, "toyota_dubai.csv")
    """

    def __init__(self, repo: HistoryRepository,
                 query_engine: QueryEngine,
                 intelligence: IntelligenceEngine,
                 config: FeatureStoreConfig | None = None):
        self._repo = repo
        self._query = query_engine
        self._intelligence = intelligence
        self.config = config or FeatureStoreConfig()
        self._registry = FeatureRegistry()
        self._store = FeatureStore(self._registry)
        self._validator = FeatureValidator(self._registry)
        self._version_mgr = DatasetVersionManager()
        self._current_version: DatasetVersion | None = None

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self,
              make: str = "", model: str = "",
              marketplace: str = "", country: str = "",
              min_year: int = 0, max_year: int = 0,
              min_quality: int = 0,
              max_rows: int = 0,
              ) -> DatasetVersion:
        """Build a feature dataset from current + historical data."""
        start = time.perf_counter()

        # Filter criteria
        filters = FilterCriteria(
            make=make, model=model, marketplace=marketplace,
            country=country, year_min=min_year, year_max=max_year,
        )

        # Get current listings
        entries = self._get_entries(filters)

        # Build feature vectors
        for entry in entries:
            fp = entry.fingerprint
            lid = entry.listing_id

            # Gather raw values from entry data
            data = entry.data if hasattr(entry, 'data') else {}

            # Compute market intelligence features
            idx = self._intelligence.price_index(make=data.get("make", make),
                                                  model=data.get("model", model),
                                                  marketplace=entry.marketplace)
            dep = self._intelligence.depreciation(data.get("make", make),
                                                  data.get("model", model))
            liq = self._intelligence.liquidity(marketplace=entry.marketplace)

            # Build vector
            fv = FeatureVector(listing_id=lid, fingerprint=fp)
            fv.values = {
                "make": data.get("make", make),
                "model": data.get("model", model),
                "year": data.get("year", entry.data.get("year", 0)),
                "mileage_km": float(entry.mileage_km),
                "price": float(entry.price),
                "currency": getattr(entry, 'currency', 'AED'),
                "country": country or data.get("country", ""),
                "city": data.get("city", ""),
                "body_type": data.get("body_type", ""),
                "fuel_type": data.get("fuel_type", ""),
                "transmission": data.get("transmission", ""),
                "specification": data.get("specification", ""),
                "seller_type": data.get("seller_type", ""),
                "color": data.get("color", ""),
                "vehicle_age_years": float(2026 - data.get("year", 2020)),
                "days_active": 0.0,
                "snapshot_count": float(getattr(entry, 'snapshot_count', 1)),
                "price_index": idx.current_index,
                "depreciation_rate": dep.avg_annual_depreciation_pct,
                "liquidity_score": liq.inventory_turnover_30d,
                "market_health_score": 0.0,
                "ma_30d": 0.0,
                "volatility_90d": 0.0,
                "inventory_delta": 0.0,
                "momentum_score": 0.0,
                "freshness_score": 0.0,
            }
            self._store.save(fv)

            if max_rows and len(self._store.list_fingerprints()) >= max_rows:
                break

        # Validate
        self._validator.validate(self._store)

        # Version
        rows = self._store.to_rows()
        checksum = hashlib.sha256(
            json.dumps(rows[:100], default=str).encode()
        ).hexdigest()[:16] if rows else ""

        self._current_version = DatasetVersion(
            dataset_id=f"{marketplace or 'all'}_{make or 'all'}_{int(time.time())}",
            version=1,
            feature_schema_version=self._registry.schema_version,
            row_count=len(rows),
            feature_count=self._registry.count(),
            checksum=checksum,
            marketplace_coverage=[marketplace] if marketplace else [],
            filters_applied={"make": make, "model": model, "marketplace": marketplace},
        )
        self._version_mgr.add_version(self._current_version)

        return self._current_version

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_csv(self, path: str) -> None:
        rows = self._store.to_rows()
        if not rows: return
        keys = ["listing_id", "fingerprint"] + self._registry.list_names()
        with open(path, "w", encoding="utf-8") as f:
            f.write(",".join(keys) + "\n")
            for row in rows:
                vals = [str(row.get(k, "")) for k in keys]
                f.write(",".join(vals) + "\n")

    def export_jsonl(self, path: str) -> None:
        rows = self._store.to_rows()
        if not rows: return
        with open(path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, default=str) + "\n")

    def to_dataframe(self):
        """Return a pandas DataFrame (if pandas is installed)."""
        try:
            import pandas as pd
            return pd.DataFrame(self._store.to_rows())
        except ImportError:
            return None

    @property
    def current_version(self) -> DatasetVersion | None:
        return self._current_version

    def _get_entries(self, filters) -> list:
        try:
            entries = list(self._repo._current._store.values())
            # Apply basic filters
            if filters.marketplace:
                entries = [e for e in entries if e.marketplace == filters.marketplace]
            if filters.make:
                entries = [e for e in entries
                          if filters.make.lower() in str(e.data.get("make", "")).lower()]
            return entries
        except Exception:
            return []
