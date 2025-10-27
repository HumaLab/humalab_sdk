from typing import Optional
from dataclasses import dataclass

from humalab.humalab_api_client import HumaLabApiClient
from humalab.scenarios.scenario import Scenario

@dataclass
class ScenarioMetadata:
    id: str
    version: int
    project: str
    name: str
    description: str | None
    created_at: str
    updated_at: str


def list_scenarios(project: str = "default",
                   limit: int = 20,
                   offset: int = 0,     
                   include_inactive: bool = False,
                   search: Optional[str] = None,
                   status_filter: Optional[str] = None,

                   base_url: str | None = None,
                   api_key: str | None = None,
                   timeout: float | None = None,
                   ) -> list[dict]:
    """
    List all scenarios for a given project.
    
    Args:
        project: The project name to list scenarios from.
        base_url: The base URL of the HumaLab API.
        api_key: The API key for authentication.
        timeout: The timeout for API requests.

    Returns:
        A list of scenario metadata dictionaries.
    """
    api_client = HumaLabApiClient(base_url=base_url,
                                  api_key=api_key,
                                  timeout=timeout)
    resp = api_client.get_scenarios(project_name=project,
                                    limit=limit,
                                    offset=offset,
                                    include_inactive=include_inactive,
                                    search=search,
                                    status_filter=status_filter)
    ret_list = []
    for scenario in resp.get("scenarios", []):
        scenario["project"] = project
        ret_list.append(ScenarioMetadata(id=scenario["uuid"],
                                         version=scenario["version"],
                                         project=project,
                                         name=scenario["name"],
                                         description=scenario.get("description"),
                                         created_at=scenario.get("created_at"),
                                         updated_at=scenario.get("updated_at")))
    return ret_list

def get_scenario(scenario_id: str,
                 version: int | None = None,
                 project: str = "default",
                 seed: int | None=None,
                 
                 base_url: str | None = None,
                 api_key: str | None = None,
                 timeout: float | None = None,) -> Scenario:
    api_client = HumaLabApiClient(base_url=base_url,
                                  api_key=api_key,
                                  timeout=timeout)
    scenario_resp = api_client.get_scenario(
        project_name=project,
        uuid=scenario_id, version=version)
    scenario = Scenario()

    scenario.init(scenario=scenario_resp["yaml_content"],
                  seed=seed,
                  scenario_id=f"{scenario_id}:{version}" if version is not None else scenario_id)
    return scenario