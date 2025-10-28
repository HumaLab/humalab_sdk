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


class MetricType(Enum):
    METRICS = ArtifactType.METRICS.value
    SCENARIO_STATS = ArtifactType.SCENARIO_STATS.value


class GraphType(Enum):
    """Types of graphs supported by Humalab."""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    GAUSSIAN = "gaussian"
    HEATMAP = "heatmap"
    THREE_D_MAP = "3d_map"


class ScenarioStatType(Enum):
    """Types of scenario stats based on data dimensions"""
    ONE_D = "1d"
    TWO_D = "2d"
    THREE_D = "3d"