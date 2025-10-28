from enum import Enum


RESERVED_NAMES = {
    "sceanario"
}

DEFAULT_PROJECT = "default"


class ArtifactType(Enum):
    """Types of artifacts that can be stored"""
    METRICS = "metrics" # Run & Episode
    SCENARIO_STATS = "scenario_stats" # Run only
    PYTHON = "python" # Run & Episode
    CODE = "code" # Run & Episode (YAML)