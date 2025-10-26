from contextlib import contextmanager

from omegaconf import OmegaConf

from humalab.run import Run
from humalab.humalab_config import HumalabConfig
from humalab.humalab_api_client import HumaLabApiClient
from humalab.constants import EpisodeStatus
import requests

import uuid

from collections.abc import Generator

from humalab.scenario import Scenario

_cur_run: Run | None = None

def _pull_scenario(client: HumaLabApiClient,
                   project_name: str,
                   scenario: str | list | dict | None = None,
                   scenario_id: str | None = None,) -> str | list | dict | None:
    if scenario_id is not None:
        scenario_arr = scenario_id.split(":")
        if len(scenario_arr) < 1:
            raise ValueError("Invalid scenario_id format. Expected 'scenario_id' or 'scenario_name:version'.")
        scenario_real_id = scenario_arr[0]
        scenario_version = int(scenario_arr[1]) if len(scenario_arr) > 1 else None

        scenario_response = client.get_scenario(
            project_name=project_name,
            uuid=scenario_real_id, version=scenario_version)
        return scenario_response["yaml_content"]
    return scenario

@contextmanager
def init(project: str | None = None,
         name: str | None = None,
         description: str | None = None,
         id: str | None = None,
         tags: list[str] | None = None,
         scenario: str | list | dict | None = None,
         scenario_id: str | None = None,
         base_url: str | None = None,
         api_key: str | None = None,
         seed: int | None=None,
         timeout: float | None = None,
         # num_env: int | None = None,
         auto_create_scenario: bool = False,
         ) -> Generator[Run, None, None]:
    """
    Initialize a new HumaLab run.
    
    Args:
        project: The project name under which to create the run.
        name: The name of the run.
        description: A description of the run.
        id: The unique identifier for the run. If None, a new UUID will be generated.
        tags: A list of tags to associate with the run.
        scenario: The scenario configuration as a string, list, or dict.
        scenario_id: The unique identifier of a pre-defined scenario to use.
        base_url: The base URL of the HumaLab server.
        api_key: The API key for authentication.
        seed: An optional seed for scenario randomization.
        timeout: The timeout for API requests.
        # num_env: The number of parallel environments to run. (Not supported yet.)
        auto_create_scenario: Whether to automatically create the scenario if it does not exist.
    """
    global _cur_run
    run = None
    try:
        humalab_config = HumalabConfig()
        project = project or "default"
        name = name or ""
        description = description or ""
        id = id or str(uuid.uuid4())

        base_url = base_url or humalab_config.base_url
        api_key = api_key or humalab_config.api_key
        timeout = timeout or humalab_config.timeout

        api_client = HumaLabApiClient(base_url=base_url,
                                      api_key=api_key,
                                      timeout=timeout)
        final_scenario = _pull_scenario(client=api_client, 
                                        project_name=project,
                                        scenario=scenario, 
                                        scenario_id=scenario_id)
        
        project_resp = api_client.create_project(name=project)

        scenario_inst = Scenario()
        scenario_inst.init(run_id=id, 
                           scenario=final_scenario, 
                           seed=seed, 
                           episode_id=str(uuid.uuid4()),
                           #num_env=num_env
                           )
        if scenario_id is None and scenario is not None and auto_create_scenario:
            scenario_response = api_client.create_scenario(
                project_name=project_resp['name'],
                name=f"{name} scenario",
                description="Auto-created scenario",
                yaml_content=OmegaConf.to_yaml(scenario_inst.template),
            )
            scenario_id = scenario_response['uuid']
        try:
            run_response = api_client.get_run(run_id=id)
            api_client.update_run(
                run_id=run_response['run_id'],
            )

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # If not found then create a new run,
                # so ignore not found error.
                run_response = None
            else:
                # Otherwise re-raise the exception.
                raise

        if run_response is None:
            run_response = api_client.create_run(name=name,
                                                 project_name=project_resp['name'],
                                                 description=description,
                                                 tags=tags)
            id = run_response['run_id']
            api_client.update_run(
                run_id=id,
                description=description,
            )

        run = Run(
            project=project_resp['name'],
            name=run_response["name"],
            description=run_response.get("description"),
            id=run_response['run_id'],
            tags=run_response.get("tags"),
            scenario=scenario_inst,
        )

        _cur_run = run
        yield run
    finally:
        if run:
            run.finish()
        

def finish(status: EpisodeStatus = EpisodeStatus.PASS,
           quiet: bool | None = None) -> None:
    global _cur_run
    if _cur_run:
        _cur_run.finish(status=status, quiet=quiet)

def login(api_key: str | None = None,
          relogin: bool | None = None,
          host: str | None = None,
          force: bool | None = None,
          timeout: float | None = None) -> bool:
    humalab_config = HumalabConfig()
    humalab_config.api_key = api_key or humalab_config.api_key
    humalab_config.base_url = host or humalab_config.base_url
    humalab_config.timeout = timeout or humalab_config.timeout
    return True
