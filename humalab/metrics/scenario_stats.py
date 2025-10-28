from humalab.metrics.metric import Metrics
from humalab.constants import ArtifactType, GraphType, ScenarioStatType
from humalab.humalab_api_client import EpisodeStatus
from typing import Any

class ScenarioStats(Metrics):
    """Metric to track scenario statistics such as total reward, length, and success.

    Attributes:
    """

    def __init__(self, 
                 name: str,
                 distribution_type: str,
                 scenario_stat_type: ScenarioStatType,
                 graph_type: GraphType,
                 ) -> None:
        super().__init__()
        self._name = name
        self._distribution_type = distribution_type
        self._scenario_stat_type = scenario_stat_type
        self._graph_type = graph_type
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
    def scenario_stat_type(self) -> ScenarioStatType:
        return self._scenario_stat_type
    
    @property
    def graph_type(self) -> GraphType:
        return self._graph_type
    
    @property
    def artifact_type(self) -> ArtifactType:
        return self._artifact_type
    
    def log(self, data: Any, x: Any = None, replace: bool = False) -> None:
        if x in self._values:
            if replace:
                self._values[x] = data
            else:   
                raise ValueError(f"Data for episode_id {x} already exists. Use replace=True to overwrite.")
        else:
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
        
    