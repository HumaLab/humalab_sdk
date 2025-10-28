from humalab.metrics.metric import Metrics
from humalab.constants import ArtifactType, GraphType, MetricDimType
from humalab.humalab_api_client import EpisodeStatus
from typing import Any


SCENARIO_STATS_NEED_FLATTEN = {
    "uniform_1d",
    "bernoulli_1d",
    "categorical_1d",
    "discrete_1d",
    "log_uniform_1d",
    "gaussian_1d",
    "truncated_gaussian_1d"
}


class ScenarioStats(Metrics):
    """Metric to track scenario statistics such as total reward, length, and success.

    Attributes:
    """

    def __init__(self, 
                 name: str,
                 distribution_type: str,
                 metric_dim_type: MetricDimType,
                 graph_type: GraphType,
                 ) -> None:
        super().__init__(
            metric_dim_type=metric_dim_type,
            graph_type=graph_type
        )
        self._name = name
        self._distribution_type = distribution_type
        self._artifact_type = ArtifactType.SCENARIO_STATS
        self._values = {}
        self._results = {}

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def distribution_type(self) -> str:
        return self._distribution_type

    @property
    def artifact_type(self) -> ArtifactType:
        return self._artifact_type
    
    def log(self, data: Any, x: Any = None, replace: bool = False) -> None:
        if x in self._values:
            if replace:
                if self._distribution_type in SCENARIO_STATS_NEED_FLATTEN:
                    data = data[0]
                self._values[x] = data
            else:   
                raise ValueError(f"Data for episode_id {x} already exists. Use replace=True to overwrite.")
        else:
            if self._distribution_type in SCENARIO_STATS_NEED_FLATTEN:
                data = data[0]
            self._values[x] = data
    
    def log_status(self, 
                   episode_id: str,
                   episode_status: EpisodeStatus, 
                   replace: bool = False) -> None:
        """Log a new data point for the metric. The behavior depends on the granularity.    

        Args:
            data (Any): The data point to log.
            x (Any | None): The x-axis value associated with the data point.
                if None, the current step is used.
            replace (bool): Whether to replace the last logged value.
        """
        if episode_id in self._results:
            if replace:
                self._results[episode_id] = episode_status
            else:   
                raise ValueError(f"Data for episode_id {episode_id} already exists. Use replace=True to overwrite.")
        else:
            self._results[episode_id] = episode_status

    def _finalize(self) -> dict:
        ret_val = {
            "values": self._values,
            "results": self._results,
            "distribution_type": self._distribution_type,
        }
        self._values = {}
        self._results = {}
        return ret_val
        
    