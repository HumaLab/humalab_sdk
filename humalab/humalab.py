from contextlib import contextmanager
from humalab_sdk.run import Run
from humalab_sdk.humalab_config import HumalabConfig
from humalab_sdk.humalab_api_client import HumaLabApiClient
from humalab_sdk.constants import EpisodeStatus

import uuid
import os

from collections.abc import Generator

from humalab_sdk.scenario import Scenario

_cur_run: Run | None = None

def _pull_scenario(client: HumaLabApiClient,
                   scenario: str | list | dict | None = None,
                   scenario_id: str | None = None,) -> str | list | dict | None:
    if scenario_id is not None:
        scenario_response = client.get_scenario(uuid=scenario_id)
        return scenario_response["yaml_content"]
    return scenario

@contextmanager
def init(entity: str | None = None,
         project: str | None = None,
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
         num_env: int | None = None
         ) -> Generator[Run, None, None]:
    global _cur_run
    run = None
    try:
        humalab_config = HumalabConfig()
        entity = entity or humalab_config.entity
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
                                        scenario=scenario, 
                                        scenario_id=scenario_id)
        scenario_inst = Scenario()
        scenario_inst.init(run_id=id, 
                           scenario=final_scenario, 
                           seed=seed, 
                           episode_id=str(uuid.uuid4()),
                           num_env=num_env)

        run = Run(
            entity=entity,
            project=project,
            name=name,
            description=description,
            id=id,
            tags=tags,
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
    # TODO: Validate api_key against host given.
    # and retrieve entity information.
    humalab_config = HumalabConfig()
    humalab_config.api_key = api_key or humalab_config.api_key
    humalab_config.base_url = host or humalab_config.base_url
    humalab_config.timeout = timeout or humalab_config.timeout
    return True


if __name__ == "__main__":
    login(api_key="GSdIImnRJs1TQRpkN74PyIVHhX8_PISLOI9NVF6uO94",
          host="http://localhost:8000")
    
    with init(entity="default",
              project="test",
              name="my first run",
              description="testing the humalab sdk",
              tags=["tag1", "tag2"],
              scenario_id="cb9668c6-99fe-490c-a97c-e8c1f06b54a6",
              num_env=None) as run:
        print(f"Run ID: {run.id}")
        print(f"Run Name: {run.name}")
        print(f"Run Description: {run.description}")
        print(f"Run Tags: {run.tags}")
        print(f"Run Scenario YAML:\n{run.scenario.yaml}")

        scenario = run.scenario
        # Simulate some operations
        print("CUP position: ", scenario.scenario.cup.position)
        print("CUP orientation: ", scenario.scenario.cup.orientation)
        print("Asset: ", scenario.scenario.cup.asset)
        print("Friction: ", scenario.scenario.cup.friction)
        print("Num Objects: ", scenario.scenario.num_objects)
        scenario.reset()
        print("======================SCENARIO RESET==========================")
        print("CUP position: ", scenario.scenario.cup.position)
        print("CUP orientation: ", scenario.scenario.cup.orientation)
        print("Asset: ", scenario.scenario.cup.asset)
        print("Friction: ", scenario.scenario.cup.friction)
        print("Num Objects: ", scenario.scenario.num_objects)

        humalab_config = HumalabConfig()
        base_url = humalab_config.base_url
        api_key = humalab_config.api_key
        timeout = humalab_config.timeout

        api_client = HumaLabApiClient(base_url=base_url,
                                      api_key=api_key,
                                      timeout=timeout)
        resource = api_client.get_resource(name="lerobot", version=1)
        print("Resource metadata: ", resource)
        file_content = api_client.download_resource(name="lerobot")
        filename = os.path.basename(resource['resource_url'])
        filename = os.path.join(humalab_config.workspace_path, filename)
        with open(filename, "wb") as f:
            f.write(file_content)
        print(f"Resource file downloaded: {filename}")
