"""LightGBM training pipeline with evaluation, shadow deployment, and model registry."""
import hashlib
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from src.models.listing import Listing
from src.models.model_registry import ModelRegistry
from src.engine.features.base import FeatureRegistry, MarketContext

logger = structlog.get_logger()


async def build_training_dataset(session: AsyncSession, min_listings: int = 1000) -> pd.DataFrame | None:
    """Build training dataset from production listings with constructed targets."""
    stmt = (select(Listing)
            .where(Listing.quality_score >= 60,
                   Listing.status.in_(["active", "probably_sold", "sold_confirmed"]))
            .order_by(Listing.last_seen_at.desc())
            .limit(50000))
    result = await session.execute(stmt)
    rows = result.scalars().all()

    if len(rows) < min_listings:
        logger.warning("insufficient_training_data", count=len(rows), needed=min_listings)
        return None

    df = pd.DataFrame([{
        "make": r.make, "model": r.model, "year": r.year,
        "mileage_km": r.mileage_km, "spec": r.spec,
        "seller_type": r.seller_type, "warranty": r.warranty,
        "service_history": r.service_history,
        "city": r.city, "country": r.country,
        "asking_price_aed": r.normalized_price_aed,
        "quality_score": r.quality_score,
        "status": r.status,
        "delisting_confidence": r.delisting_confidence or 0,
    } for r in rows])

    # Build market context per segment
    segments = df.groupby(["make", "model", "country"])
    for (make, model_name, country), segment in segments:
        if len(segment) < 20:
            continue
        mask = (df["make"] == make) & (df["model"] == model_name) & (df["country"] == country)
        ctx = MarketContext(
            make=make, model=model_name, year=int(segment["year"].median()),
            country=country,
            segment_median_price=segment["asking_price_aed"].median(),
            segment_listing_count=len(segment),
            segment_price_volatility=float(segment["asking_price_aed"].std() / segment["asking_price_aed"].mean())
            if segment["asking_price_aed"].mean() > 0 else 0.05,
        )

    # Construct target: estimated transaction price
    df["target"] = _construct_target(df)

    return df


def _construct_target(df: pd.DataFrame) -> pd.Series:
    """Construct estimated transaction price from asking prices + signals."""
    target = df["asking_price_aed"].copy()

    # Sold confirmed → likely sold close to ask (5% discount)
    sold_mask = df["status"].isin(["sold_confirmed", "probably_sold"])
    target.loc[sold_mask] *= 0.95

    # High delisting confidence → stronger signal
    high_conf = df["delisting_confidence"] > 0.8
    target.loc[high_conf] *= 0.93

    return target


def train_model(df: pd.DataFrame, feature_names: list[str]) -> tuple[object, dict, float]:
    """Train LightGBM model. Returns (model, metrics_dict, mae)."""
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split

    X = df[feature_names].fillna(0)
    y = df["target"]

    if len(X) < 100:
        raise ValueError(f"Insufficient training data: {len(X)} rows")

    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X, y, test_size=0.15, random_state=42
    )

    model = lgb.LGBMRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        num_leaves=31,
        min_child_samples=30,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_holdout)
    mae = float(np.mean(np.abs(y_holdout - y_pred)))
    mape = float(np.mean(np.abs((y_holdout - y_pred) / y_holdout)) * 100)

    metrics = {
        "mae": mae,
        "mape": mape,
        "r2": float(np.corrcoef(y_pred, y_holdout)[0, 1] ** 2),
        "training_rows": len(X_train),
        "holdout_rows": len(X_holdout),
        "feature_importance": dict(zip(feature_names, model.feature_importances_.tolist())),
    }

    return model, metrics, mae


def compute_dataset_hash(df: pd.DataFrame) -> str:
    """Deterministic hash of training data for reproducibility."""
    sample = df.sample(min(1000, len(df)), random_state=42)
    raw = json.dumps(sample[["make", "model", "year", "asking_price_aed"]].values.tolist())
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


async def train_and_register(
    session: AsyncSession, git_commit: str = "unknown"
) -> ModelRegistry | None:
    """Full training pipeline: build dataset → train → register in model_registry."""
    import src.engine.features.listing_features  # noqa: F401 — register features
    import src.engine.features.market_features   # noqa: F401
    import src.engine.features.vehicle_features  # noqa: F401

    df = await build_training_dataset(session)
    if df is None:
        return None

    feature_names = list(FeatureRegistry.all().keys())
    model, metrics, mae = train_model(df, feature_names)

    # Persist model to stable directory (not tempfile).
    # Models are saved under src/ml/models/{model_name}.pkl
    from src.ml.model_persistence import save_model
    model_name = f"lightgbm_v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
    model_path = save_model(model, model_name)

    registry = ModelRegistry(
        trained_at=datetime.now(timezone.utc),
        model_type="lightgbm",
        model_path=model_path,
        model_name=model_name,
        mae=metrics["mae"],
        mape=metrics["mape"],
        r2_score=metrics["r2"],
        training_rows=metrics["training_rows"],
        holdout_rows=metrics["holdout_rows"],
        training_dataset_hash=compute_dataset_hash(df),
        feature_version="1.0.0",
        git_commit=git_commit,
        hyperparameters={"n_estimators": 200, "max_depth": 7, "learning_rate": 0.05},
        features_used=feature_names,
        status="training",
    )
    session.add(registry)
    await session.commit()
    logger.info("model_trained", model_name=registry.model_name, mae=mae, mape=metrics["mape"])
    return registry
