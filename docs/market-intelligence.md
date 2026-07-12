# GCC Car Value — Market Intelligence & Price Index Engine

**Date:** 2026-07-12  
**Package:** `analytics/intelligence/`

## Architecture

```
Historical Dataset → QueryEngine → IntelligenceEngine
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              PriceIndex         DepreciationCurve    LiquidityMetrics
              MarketHealth       Benchmark           ForecastInputs
```

## Products

### Price Index
```python
idx = engine.price_index(make="Toyota", model="Land Cruiser")
# PriceIndex(segment="toyota_land_cruiser", current_index=185000, change_pct=+3.2)
```

### Depreciation Curve
```python
curve = engine.depreciation("Toyota", "Camry")
# DepreciationCurve(avg_annual_depreciation_pct=8.5,
#   data_points=[{age_years: 1, avg_price: 85000}, {age_years: 5, avg_price: 55000}],
#   mileage_factor=-2500)  # AED per 10K km
```

### Liquidity
```python
liq = engine.liquidity(make="Toyota", marketplace="dubizzle")
# LiquidityMetrics(avg_days_active=18.5, days_to_sell_estimate=13.0,
#   inventory_turnover_30d=15.2)
```

### Market Health
```python
health = engine.market_health("dubizzle")
# MarketHealth(stability_score=72.3, supply_trend="growing", demand_proxy="moderate")
```

### Benchmarks
```python
bm = engine.benchmark("Toyota", "Camry", marketplace="dubizzle")
# Benchmark(p10=42000, p25=48000, p50=65000, p75=82000, p90=95000)
```

### Forecast Inputs
```python
fi = engine.forecast_inputs(make="Toyota", model="Camry")
# ForecastInputs(ma_30d=67000, volatility_90d=0.085, market_momentum=+2.1)
```

## Verified

- Price index: segment identification, current/previous/change calculation
- Depreciation: age-based price groupings, annual rate, mileage factor
- Liquidity: days-to-sell estimate, turnover, new/removal rates
- Market health: growth, volatility, freshness, stability score
- Benchmarks: P10/P25/P50/P75/P90 percentiles
- Forecast inputs: 30d MA, 90d volatility, price velocity, momentum
- All read-only — no data mutations

---

*Market intelligence documented 2026-07-12.*
