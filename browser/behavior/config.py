from dataclasses import dataclass, field

@dataclass
class BehaviourConfig:
    max_sessions: int = 100
    default_profile_name: str = "normal"
    seed: int | None = None  # For deterministic replay
