from datetime import datetime
from enum import Enum

from humalab.constants import DEFAULT_PROJECT

class ResourceType(Enum):
    URDF = "urdf"
    MJCF = "mjcf"
    USD = "usd"
    MESH = "mesh"
    VIDEO = "video"
    IMAGE = "image"
    DATA = "data"



class ResourceFile:
    def __init__(self, 
                 name: str, 
                 version: int, 
                 filename: str,
                 resource_type: str | ResourceType,
                 project: str = DEFAULT_PROJECT,
                 description: str | None = None,
                 created_at: datetime | None = None):
        self._project = project
        self._name = name
        self._version = version
        self._filename = filename
        self._resource_type = ResourceType(resource_type)
        self._description = description
        self._created_at = created_at

    @property
    def project(self) -> str:
        return self._project
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def resource_type(self) -> ResourceType:
        return self._resource_type

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def description(self) -> str | None:
        return self._description
    
    def __repr__(self) -> str:
        return f"ResourceFile(project={self._project}, name={self._name}, version={self._version}, filename={self._filename}, resource_type={self._resource_type}, description={self._description}, created_at={self._created_at})"
    
    def __str__(self) -> str:
        return self.__repr__()

