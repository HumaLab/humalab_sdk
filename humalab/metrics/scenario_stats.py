from humalab.metrics.metric import Metrics
from humalab.humalab_api_client import EpisodeStatus
from typing import Any

class ScenarioStats(Metrics):
    """Metric to track scenario statistics such as total reward, length, and success.

    Attributes:
        name (str): The name of the metric.
        run_id (str): The ID of the run.
        episode_id (str): The ID of the episode.
        total_reward (float): The total reward accumulated in the episode.
        length (int): The length of the episode in steps.
        success (bool | None): Whether the episode was successful, if applicable.
    """

    def __init__(self, run_id: str) -> None:
        super().__init__()
        self._run_id = run_id
        self._values = {}
        self._results = {}

    @property
    def run_id(self) -> str:
        return self._run_id
    
    def log(self, data: Any, x: Any = None, replace: bool = False) -> None:
        raise NotImplementedError("Use log_with_status to log episode statistics with status.")
    
    def log_with_status(self, 
                        data: Any, 
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
        if episode_id in self._values:
            if replace:
                self._values[episode_id] = data
                self._results[episode_id] = episode_status
            else:   
                raise ValueError(f"Data for episode_id {episode_id} already exists. Use replace=True to overwrite.")
        else:
            self._values[episode_id] = data
            self._results[episode_id] = episode_status

    def _finalize(self) -> None:
        if not self._values:
            return
        super()._finalize()
        
    