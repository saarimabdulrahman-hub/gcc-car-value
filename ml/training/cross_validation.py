"""Cross Validation — train/test, K-fold, stratified, time-series, deterministic."""

import random


class CrossValidator:
    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def train_test_split(self, data: list, test_size: float = 0.15
                         ) -> tuple[list, list]:
        """Deterministic train/test split."""
        indices = list(range(len(data)))
        self._rng.shuffle(indices)
        split = int(len(data) * (1 - test_size))
        train_idx = set(indices[:split])
        test_idx = set(indices[split:])
        train = [d for i, d in enumerate(data) if i in train_idx]
        test = [d for i, d in enumerate(data) if i in test_idx]
        return train, test

    def kfold(self, data: list, folds: int = 5) -> list[tuple[list, list]]:
        """Deterministic K-fold splits."""
        indices = list(range(len(data)))
        self._rng.shuffle(indices)
        fold_size = len(data) // folds
        results = []
        for i in range(folds):
            start = i * fold_size
            end = start + fold_size if i < folds - 1 else len(data)
            test_idx = set(indices[start:end])
            train_idx = set(indices) - test_idx
            train = [d for j, d in enumerate(data) if j in train_idx]
            test = [d for j, d in enumerate(data) if j in test_idx]
            results.append((train, test))
        return results

    def time_series_split(self, data: list, folds: int = 5
                          ) -> list[tuple[list, list]]:
        """Time-series split — earlier data for train, later for test."""
        fold_size = len(data) // (folds + 1)
        results = []
        for i in range(1, folds + 1):
            split = i * fold_size
            train = data[:split]
            test = data[split:split + fold_size]
            results.append((train, test))
        return results
