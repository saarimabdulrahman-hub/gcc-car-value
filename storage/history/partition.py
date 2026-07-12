"""Partition strategy — monthly + marketplace partitions."""

from storage.history.models import PartitionKey

class PartitionManager:
    @staticmethod
    def assign(snapshot) -> PartitionKey:
        return PartitionKey.from_timestamp(snapshot.marketplace, snapshot.captured_at)

    @staticmethod
    def list_partitions(store) -> list[str]:
        return sorted(store.partition_distribution().keys())
