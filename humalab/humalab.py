from contextlib import contextmanager

from humalab.assets.files.resource_file import ResourceFile
from humalab.assets.files.urdf_file import URDFFile
from humalab.assets.resource_manager import ResourceManager
from humalab.run import Run
from humalab.humalab_config import HumalabConfig
from humalab.humalab_api_client import HumaLabApiClient
from humalab.constants import EpisodeStatus
import requests

import uuid
import os

from collections.abc import Generator

from humalab.scenario import Scenario

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
    """
    Initialize a new HumaLab run.
    
    Args:
        entity: The entity (user or team) under which to create the run.
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
        num_env: The number of parallel environments to run.
    """
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
        
        project_resp = api_client.create_project(name=project)

        scenario_inst = Scenario()
        scenario_inst.init(run_id=id, 
                           scenario=final_scenario, 
                           seed=seed, 
                           episode_id=str(uuid.uuid4()),
                           num_env=num_env)
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
        print("create_run response: ", run_response)

        run = Run(
            entity=run_response['created_by'],
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
              scenario_id="4ee3b2bb-1968-4b7f-8f96-4c5e64179c08",
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

        scenario_string = """
        scenario:
          cup:
            position: "${uniform: [0.7, 0.7, 0.7], 
                                [1.5, 1.3, 0.7], [2, 3]}"
            orientation: "${uniform: 0.3, 0.7}"
            asset: "${categorical: ['lerobot', 'apple2', 'apple3'], [0.1, 0.3, 0.5]}"
            friction: "${gaussian: 0.3, 0.05}"
          hello: 13
          jkjk: test
          num_objects: "${discrete: 5, 10}"
          dfdjkjk: "hello"
        """
        with init(entity="default",
            project="test",
            name="my first run",
            description="testing the humalab sdk",
            tags=["tag1", "tag2"],
            scenario=scenario_string,
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

        resource = ResourceManager()
        urdf_file: URDFFile = resource.download(name="lerobot", version=1)
        print("URDF File: ", urdf_file.filename)
        print("URDF Description: ", urdf_file.description)
        print("URDF Created At: ", urdf_file.created_at)
        print("URDF Root Path: ", urdf_file._root_path)
        print("URDF Root Path: ", urdf_file._urdf_filename)

        urdf_file: URDFFile = resource.download(name="lerobot")
        print("URDF File: ", urdf_file.filename)
        print("URDF Description: ", urdf_file.description)
        print("URDF Created At: ", urdf_file.created_at)
        print("URDF Root Path: ", urdf_file._root_path)
        print("URDF Root Path: ", urdf_file._urdf_filename)

        atlas_file: ResourceFile = resource.download(name="atlas")
        print("Atlas File: ", atlas_file.filename)
        print("Atlas Description: ", atlas_file.description)
        print("Atlas Created At: ", atlas_file.created_at)

        
        """
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
        """
