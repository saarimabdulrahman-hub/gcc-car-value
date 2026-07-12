"""Dataset export — CSV, JSONL, Parquet interface."""

from ml.features.dataset_builder import DatasetBuilder


class DatasetExporter:
    def __init__(self, builder: DatasetBuilder): self._builder = builder

    def to_csv(self, path: str) -> None:
        self._builder.export_csv(path)

    def to_jsonl(self, path: str) -> None:
        self._builder.export_jsonl(path)

    def to_dataframe(self):
        return self._builder.to_dataframe()
