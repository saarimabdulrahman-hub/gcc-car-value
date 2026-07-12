"""Historical Query API — filtered queries across current and snapshot stores."""

from storage.history.repository import HistoryRepository


class QueryAPI:
    """Convenience query methods over the HistoryRepository."""

    def __init__(self, repo: HistoryRepository):
        self._repo = repo

    def latest(self, fingerprint: str) -> dict | None:
        entry = self._repo.get_current(fingerprint)
        return {"fingerprint": entry.fingerprint, "price": entry.price,
                "mileage_km": entry.mileage_km, "status": entry.status,
                "lifecycle": entry.lifecycle_state,
                } if entry else None

    def price_history(self, fingerprint: str) -> list[dict]:
        return self._repo.get_price_timeline(fingerprint)

    def mileage_history(self, fingerprint: str) -> list[dict]:
        return self._repo.get_mileage_timeline(fingerprint)

    def lifecycle_history(self, fingerprint: str) -> list[dict]:
        return self._repo.get_lifecycle_timeline(fingerprint)

    def active(self) -> list[dict]:
        return [{"fingerprint": e.fingerprint, "price": e.price,
                 "marketplace": e.marketplace} for e in self._repo.list_active()]

    def recently_updated(self, max_age_s: float = 3600.0) -> list[dict]:
        return [{"fingerprint": e.fingerprint, "price": e.price}
                for e in self._repo.list_recently_updated(max_age_s)]
