from humalab.assets.files.resource_file import ResourceFile, ResourceType
from humalab.humalab_config import HumalabConfig
from humalab.humalab_api_client import HumaLabApiClient
from humalab.assets.files.urdf_file import URDFFile
import os
from typing import Any, Optional

        
def _asset_dir(humalab_config: HumalabConfig, name: str, version: int) -> str:
    return os.path.join(humalab_config.workspace_path, "assets", name, f"{version}")

def _create_asset_dir(humalab_config: HumalabConfig, name: str, version: int) -> bool:
    asset_dir = _asset_dir(humalab_config, name, version)
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir, exist_ok=True)
        return True
    return False

def download(name: str, 
             version: int | None=None,
             project: str = "default",
             
             host: str | None = None,
             api_key: str | None = None,
             timeout: float | None = None,
             ) -> Any:
    humalab_config = HumalabConfig()

    api_client = HumaLabApiClient(base_url=host,
                                  api_key=api_key,
                                  timeout=timeout)

    resource = api_client.get_resource(project_name=project, name=name, version=version)
    filename = os.path.basename(resource['resource_url'])
    filename = os.path.join(_asset_dir(humalab_config, name, resource["version"]), filename)
    if _create_asset_dir(humalab_config, name, resource["version"]):
        file_content = api_client.download_resource(project_name=project, name="lerobot")
        with open(filename, "wb") as f:
            f.write(file_content)
    
    if resource["resource_type"].lower() == "urdf":
        return URDFFile(project=project,
                        name=name,
                        version=resource["version"],
                        description=resource.get("description"),
                        filename=filename,
                        urdf_filename=resource.get("filename"),
                        created_at=resource.get("created_at"))

    return ResourceFile(project=project,
                        name=name, 
                        version=resource["version"], 
                        filename=filename,
                        resource_type=resource["resource_type"],
                        description=resource.get("description"),
                        created_at=resource.get("created_at"))

def list_resources(project: str = "default",
                   resource_types: Optional[list[str | ResourceType]] = None,
                   limit: int = 20,
                   offset: int = 0,
                   latest_only: bool = True,
                    
                    host: str | None = None,
                    api_key: str | None = None,
                    timeout: float | None = None,) -> list[ResourceFile]:
    api_client = HumaLabApiClient(base_url=host,
                                  api_key=api_key,
                                  timeout=timeout)

    resource_type_string = None
    if resource_types:
        resource_type_strings = {rt.value if isinstance(rt, ResourceType) else rt for rt in resource_types}
        resource_type_string = ",".join(resource_type_strings)
    resp = api_client.get_resources(project_name=project,
                                    resource_types=resource_type_string,
                                    limit=limit,
                                    offset=offset,
                                    latest_only=latest_only)
    resources = resp.get("resources", [])
    ret_list = []
    for resource in resources:
        ret_list.append(ResourceFile(name=resource["name"],
                                    version=resource.get("version"),
                                    project=project,
                                    filename=resource.get("filename"),
                                    resource_type=resource.get("resource_type"),
                                    description=resource.get("description"),
                                    created_at=resource.get("created_at")))
    return ret_list