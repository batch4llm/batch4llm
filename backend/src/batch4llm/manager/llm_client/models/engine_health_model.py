from dataclasses import dataclass


@dataclass
class EngineHealth:
    healthy: bool
    error: str | None = None
