

class ResourceFile:
    def __init__(self, 
                 name: str, 
                 version: int, 
                 resource_type: str, 
                 filepath: str):
        self._name = name
        self._version = version
        self._resource_type = resource_type
        self._filepath = filepath

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def resource_type(self) -> str:
        return self._resource_type
    
    @property
    def filepath(self) -> str:
        return self._filepath
