import uuid
import traceback

from humalab.constants import DEFAULT_PROJECT, RESERVED_NAMES
from humalab.humalab_api_client import HumaLabApiClient, RunStatus
from humalab.metrics.metric import Metrics
from humalab.episode import Episode

from humalab.scenarios.scenario import Scenario

class Run:
    def __init__(self,
                 scenario: Scenario,
                 project: str = DEFAULT_PROJECT,
                 name: str | None = None,
                 description: str | None = None,
                 id: str | None = None,
                 tags: list[str] | None = None,

                 base_url: str | None = None,
                 api_key: str | None = None,
                 timeout: float | None = None,
                 ) -> None:
        """
        Initialize a new Run instance.
        
        Args:
            project (str): The project name under which the run is created.
            scenario (Scenario): The scenario instance for the run.
            name (str | None): The name of the run.
            description (str | None): A description of the run.
            id (str | None): The unique identifier for the run. If None, a UUID is generated.
            tags (list[str] | None): A list of tags associated with the run.
        """
        self._project = project
        self._id = id or str(uuid.uuid4())
        self._name = name or ""
        self._description = description or ""
        self._tags = tags or []

        self._scenario = scenario
        self._logs = {}
        self._is_finished = False

        self._api_client = HumaLabApiClient(base_url=base_url,
                                            api_key=api_key,
                                            timeout=timeout)

    
    @property
    def project(self) -> str:
        """The project name under which the run is created.
        
        Returns:
            str: The project name.
        """
        return self._project
    
    @property
    def id(self) -> str:
        """The unique identifier for the run.
        
        Returns:
            str: The run ID.
        """
        return self._id
    
    @property
    def name(self) -> str:
        """The name of the run.

        Returns:
            str: The run name.
        """
        return self._name
    
    @property
    def description(self) -> str:
        """The description of the run.

        Returns:
            str: The run description.
        """
        return self._description
    
    @property
    def tags(self) -> list[str]:
        """The tags associated with the run.

        Returns:
            list[str]: The list of tags.
        """
        return self._tags
    
    @property
    def scenario(self) -> Scenario:
        """The scenario associated with the run.

        Returns:
            Scenario: The scenario instance.
        """
        return self._scenario
    
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self._is_finished:
            return
        if exception_type is not None:
            err_msg = "".join(traceback.format_exception(exception_type, exception_value, exception_traceback))
            self.finish(status=RunStatus.ERRORED, err_msg=err_msg)
        else:
            self.finish()

    def create_episode(self, episode_id: str | None = None) -> Episode:
        """Reset the run for a new episode.

        Args:
            status (EpisodeStatus): The status of the current episode before reset.
        """
        episode = None
        episode_id = episode_id or str(uuid.uuid4())
        cur_scenario, episode_vals = self._scenario.resolve()
        episode = Episode(run_id=self._id,
                        episode_id=episode_id,
                        scenario_conf=cur_scenario,
                        episode_vals=episode_vals)
        return episode

    
    def add_metric(self, name: str, metric: Metrics) -> None:
        if name in self._logs:
            raise ValueError(f"{name} is a reserved name and is not allowed.")
        self._logs[name] = metric
        
    def log(self, data: dict, x: dict | None = None, replace: bool = False) -> None:
        for key, value in data.items():
            if key in RESERVED_NAMES:
                raise ValueError(f"{key} is a reserved name and is not allowed.")
            if key not in self._logs:
                self._logs[key] = key
            else:
                cur_val = self._logs[key]
                if isinstance(cur_val, Metrics):
                    cur_x = x.get(key) if x is not None else None
                    cur_val.log(value, x=cur_x, replace=replace)
                else:
                    if replace:
                        self._logs[key] = value
                    else:
                        raise ValueError(f"Cannot log value for key '{key}' as there is already a value logged.")
    
    def finish(self,
               status: RunStatus = RunStatus.FINISHED,
               err_msg: str | None = None) -> None:
        """Finish the run and submit final metrics.

        Args:
            status (RunStatus): The final status of the run.
            err_msg (str | None): An optional error message.
        """
        if self._is_finished:
            raise RuntimeError("Run has already been finished.")
        self._is_finished = True
        # TODO: submit final metrics
        for key, value in self._logs.items():
            if isinstance(value, Metrics):
                value.submit()

        self._api_client.update_run(
            run_id=self._id,
            status=status,
            err_msg=err_msg
        )