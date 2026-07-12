"""Dataset versioning — track dataset versions, checksums, schema versions."""

from ml.features.models import DatasetVersion


class DatasetVersionManager:
    def __init__(self): self._versions: list[DatasetVersion] = []

    def add_version(self, v: DatasetVersion) -> None:
        v.version = len(self._versions) + 1
        self._versions.append(v)

    def get_latest(self) -> DatasetVersion | None:
        return self._versions[-1] if self._versions else None

    def get_all(self) -> list[DatasetVersion]:
        return list(self._versions)
