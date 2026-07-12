"""Download manager — files, images, PDFs, streaming."""

from browser.models import DownloadInfo


class DownloadManager:
    """Manages file downloads from browser pages."""

    def __init__(self, download_path: str | None = None):
        self._path = download_path
        self._downloads: list[DownloadInfo] = []

    def add_download(self, info: DownloadInfo) -> None:
        self._downloads.append(info)

    def list_downloads(self) -> list[DownloadInfo]:
        return list(self._downloads)

    @property
    def total_bytes(self) -> int:
        return sum(d.size_bytes for d in self._downloads)
