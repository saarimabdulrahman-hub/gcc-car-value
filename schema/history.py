"""Vehicle history sub-model."""

from dataclasses import dataclass


@dataclass
class VehicleHistory:
    """Vehicle history and condition information."""
    accident_history: bool = False
    service_history: bool = False
    owners: int = 0
    warranty: bool = False
    export_status: str = ""
    import_status: str = ""
    notes: str = ""
