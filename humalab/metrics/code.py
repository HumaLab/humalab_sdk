class Code:
    """Class for logging code artifacts."""
    def __init__(self, 
                 run_id: str, 
                 key: str,
                 code_content: str,
                 episode_id: str | None = None) -> None:
        super().__init__()
        self._run_id = run_id
        self._key = key
        self._code_content = code_content
        self._episode_id = episode_id

    @property
    def run_id(self) -> str:
        return self._run_id
    
    @property
    def key(self) -> str:
        return self._key
    
    @property
    def code_content(self) -> str:
        return self._code_content
    
    @property
    def episode_id(self) -> str | None:
        return self._episode_id
