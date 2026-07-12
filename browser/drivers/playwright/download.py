"""Playwright download manager."""

from browser.models import DownloadInfo


class PlaywrightDownload:
    """Wraps a Playwright Download object."""

    def __init__(self, pw_download):
        self._pw_download = pw_download

    async def save(self, path: str) -> DownloadInfo:
        await self._pw_download.save_as(path)
        return DownloadInfo(
            url=self._pw_download.url,
            suggested_filename=self._pw_download.suggested_filename,
            path=path,
        )
