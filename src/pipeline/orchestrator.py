import uuid
from datetime import datetime, timezone
from src.scrapers.base import BaseScraper, ScraperResult
from src.models.pipeline_run import PipelineRun
import structlog

logger = structlog.get_logger()


class PipelineOrchestrator:
    """Coordinates the full ingestion pipeline for a batch of scrapers."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def run_pipeline(self, scrapers: list[BaseScraper]) -> list[PipelineRun]:
        pipeline_runs = []
        for scraper in scrapers:
            logger.info("scraper_starting", source=scraper.source)
            scraper_result = await scraper.run()
            run = await self._record_run(scraper_result, scraper.source)
            pipeline_runs.append(run)
            logger.info("scraper_complete", source=scraper.source,
                        records=scraper_result.records_ingested,
                        run_id=str(run.run_id))
        return pipeline_runs

    async def _record_run(self, result: ScraperResult, source: str) -> PipelineRun:
        async with self.session_factory() as session:
            run = PipelineRun(
                run_id=uuid.UUID(result.run_id),
                source=source,
                started_at=result.started_at,
                completed_at=result.completed_at,
                pages_crawled=result.pages_crawled,
                records_ingested=result.records_ingested,
                error_count=len(result.errors),
                errors=result.errors,
                success=len(result.errors) == 0,
                parser_version="1.0.0",
                normalizer_version="1.0.0",
            )
            if run.completed_at and run.started_at:
                run.duration_seconds = int((run.completed_at - run.started_at).total_seconds())
            session.add(run)
            await session.commit()
            return run
