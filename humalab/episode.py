from humalab.constants import RESERVED_NAMES, ArtifactType
from humalab.humalab_api_client import HumaLabApiClient, EpisodeStatus
from humalab.metrics.metric import Metrics
from omegaconf import DictConfig, ListConfig, OmegaConf
from typing import Any
import pickle
import traceback

from humalab.utils import is_standard_type


class Episode:
    def __init__(self, 
                 run_id: str, 
                 episode_id: str, 
                 scenario_conf: DictConfig | ListConfig,
                 episode_vals: dict | None = None,

                 base_url: str | None = None,
                 api_key: str | None = None,
                 timeout: float | None = None,):
        self._run_id = run_id
        self._episode_id = episode_id
        self._episode_status = EpisodeStatus.RUNNING
        self._scenario_conf = scenario_conf
        self._logs = {}
        self._episode_vals = episode_vals or {}
        self._is_finished = False

        self._api_client = HumaLabApiClient(base_url=base_url,
                                            api_key=api_key,
                                            timeout=timeout)

    @property
    def run_id(self) -> str:
        return self._run_id
    
    @property
    def episode_id(self) -> str:
        return self._episode_id

    @property
    def scenario(self) -> DictConfig | ListConfig:
        return self._scenario_conf
    
    @property
    def status(self) -> EpisodeStatus:
        return self._episode_status
    
    @property
    def episode_vals(self) -> dict:
        return self._episode_vals
    
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self._is_finished:
            return
        if exception_type is not None:
            err_msg = "".join(traceback.format_exception(exception_type, exception_value, exception_traceback))
            self.finish(status=EpisodeStatus.ERRORED, err_msg=err_msg)
        else:
            self.finish(status=EpisodeStatus.SUCCESS)

    def __getattr__(self, name: Any) -> Any:
        if name in self._scenario_conf:
            return self._scenario_conf[name]
        raise AttributeError(f"'Scenario' object has no attribute '{name}'")

    def __getitem__(self, key: Any) -> Any:
        if key in self._scenario_conf:
            return self._scenario_conf[key]
        raise KeyError(f"'Scenario' object has no key '{key}'")

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

    @property
    def yaml(self) -> str:
        """The current scenario configuration as a YAML string.

        Returns:
            str: The current scenario as a YAML string.
        """
        return OmegaConf.to_yaml(self._scenario_conf)
    
    def discard(self) -> None:
        self._finish(EpisodeStatus.CANCELED)

    def success(self) -> None:
        self._finish(EpisodeStatus.SUCCESS)
    
    def fail(self) -> None:
        self._finish(EpisodeStatus.FAILED)

    def finish(self, status: EpisodeStatus, err_msg: str | None = None) -> None:
        if self._is_finished:
            raise RuntimeError("Episode has already been finished.")
        self._is_finished = True
        self._episode_status = status

        self._api_client.upload_code(
            artifact_key="scenario",
            run_id=self._run_id,
            episode_id=self._episode_id,
            code_content=self.yaml
        )

        # TODO: submit final metrics
        for key, value in self._logs.items():
            if isinstance(value, Metrics):
                value.finalize()
            else:
                if not is_standard_type(value):
                    raise ValueError(f"Value for key '{key}' is not a standard type.")
                pickled = pickle.dumps(value)
                self._api_client.upload_python(
                    artifact_key=key,
                    run_id=self._run_id,
                    episode_id=self._episode_id,
                    pickled_bytes=pickled
                )
        
        self._api_client.update_episode(
            run_id=self._run_id,
            episode_id=self._episode_id,
            status=status,
            err_msg=err_msg
        )
