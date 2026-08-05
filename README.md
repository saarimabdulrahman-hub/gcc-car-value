# GCC Car Value Platform

A consumer-first car valuation platform for the Gulf (GCC) market. Scrapes classifieds and auction listings from multiple sources, normalizes the data through a multi-stage pipeline, and computes fair market values using statistical and ML models with full explainability.

## Production architecture

- **Frontend:** the static HTML, CSS, JavaScript, and images under `ui/` are the
  production artifact. Vercel publishes that directory according to
  `vercel.json` at <https://gcc-car-value.vercel.app>.
- **API:** FastAPI runs on Render at <https://gcc-car-value.onrender.com>.
- **Fallback serving:** FastAPI can serve `ui/` during integrated local
  development, but it is not the production frontend host.

The former S3/CloudFront frontend workflow has been retired so a release has
one frontend source and one deployment path. See
[`docs/frontend-deployment.md`](docs/frontend-deployment.md).

For a source-backed visual explanation of the runtime, ingestion, valuation,
security, data, and deployment flows, see
[`docs/GCC_CAR_VALUE_ARCHITECTURE.md`](docs/GCC_CAR_VALUE_ARCHITECTURE.md).

## 🚗 What It Does

| Feature | Description |
|---------|-------------|
| **Multi-source scraping** | Dubizzle UAE/KSA, YallaMotor, Haraj KSA, CarSwitch, Emirates Auction, OpenSooq, Syarah, Mazadak, DubiCars |
| **Data pipeline** | Parse → validate (Pandera) → normalize → deduplicate → promote |
| **Valuation engine** | Statistical percentile-based + ML (LightGBM) with SHAP explainability |
| **Market analytics** | Price trends, good deal indicators, market liquidity scores |
| **Delisting detection** | Probabilistic detection of sold/removed listings |
| **AI explanations** | Natural-language valuation summaries via Claude API |

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python 3.12+), SQLAlchemy (async), Alembic
- **Database:** PostgreSQL 16
- **ML:** NumPy, SciPy, scikit-learn, LightGBM, SHAP, MLflow
- **Scraping:** httpx, BeautifulSoup4, lxml, custom rate limiter
- **Infrastructure:** Docker, S3, Prometheus, structlog, APScheduler
- **Auth:** JWT + API keys

## 🚀 Quick Start

```bash
# 1. Clone and enter
cd gcc-car-value

# 2. Set up environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Run migrations
alembic upgrade head

# 5. Start the server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Optional: serve only the production frontend at http://localhost:4173
python -m http.server 4173 --directory ui
```

## 📁 Project Structure

```
gcc-car-value/
├── main.py              # FastAPI app entry point
├── pyproject.toml       # Project config and dependencies
├── scrapy.cfg           # Scrapy configuration
├── gcc_car_value/       # Core package
│   ├── scrapers/        # Site-specific scrapers
│   ├── pipeline/        # Data processing pipeline
│   ├── models/          # SQLAlchemy models
│   └── valuation/       # Valuation engine
├── scripts/             # Utility and bulk scraping scripts
├── migrations/          # Alembic migrations
└── ui/                  # Static frontend
```

## 🔑 Environment Variables

See `.env.example` for all required variables. Key ones:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `S3_BUCKET` | S3 bucket for raw data storage |
| `ANTHROPIC_API_KEY` | Claude API key for AI explanations |
