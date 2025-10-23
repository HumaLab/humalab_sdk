"""HTTP client for accessing HumaLab service APIs with API key authentication."""

import os
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin


class HumaLabApiClient:
    """HTTP client for making authenticated requests to HumaLab service APIs."""
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None
    ):
        """
        Initialize the HumaLab API client.
        
        Args:
            base_url: Base URL for the HumaLab service (defaults to localhost:8000)
            api_key: API key for authentication (defaults to HUMALAB_API_KEY env var)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("HUMALAB_SERVICE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("HUMALAB_API_KEY")
        self.timeout = timeout or 30.0  # Default timeout of 30 seconds
        
        # Ensure base_url ends without trailing slash
        self.base_url = self.base_url.rstrip('/')
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Set HUMALAB_API_KEY environment variable "
                "or pass api_key parameter to HumaLabApiClient constructor."
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "HumaLab-SDK/1.0"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request to the HumaLab service.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be joined with base_url)
            data: JSON data for request body
            params: Query parameters
            files: Files for multipart upload
            **kwargs: Additional arguments passed to requests
            
        Returns:
            requests.Response object
            
        Raises:
            requests.exceptions.RequestException: For HTTP errors
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip('/'))
        headers = self._get_headers()
        
        # If files are being uploaded, don't set Content-Type (let requests handle it)
        if files:
            headers.pop("Content-Type", None)
        
        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            files=files,
            headers=headers,
            timeout=self.timeout,
            **kwargs
        )
        
        # Raise an exception for HTTP error responses
        response.raise_for_status()
        
        return response
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, files=files, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)
    
    # Convenience methods for common API operations
    
    def get_resources(
        self, 
        resource_types: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        latest_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get list of all resources.
        
        Args:
            resource_types: Comma-separated resource types to filter by
            limit: Maximum number of resources to return
            offset: Number of resources to skip
            latest_only: If true, only return latest version of each resource
            
        Returns:
            Resource list with pagination info
        """
        params = {
            "limit": limit,
            "offset": offset,
            "latest_only": latest_only
        }
        if resource_types:
            params["resource_types"] = resource_types
            
        response = self.get("/resources", params=params)
        return response.json()
    
    def get_resource(self, name: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a specific resource.
        
        Args:
            name: Resource name
            version: Specific version (defaults to latest)
            
        Returns:
            Resource data
        """
        if version is not None:
            endpoint = f"/resources/{name}/{version}"
        else:
            endpoint = f"/resources/{name}"
        
        response = self.get(endpoint)
        return response.json()
    
    def download_resource(
        self, 
        name: str, 
        version: Optional[int] = None
    ) -> bytes:
        """
        Download a resource file.
        
        Args:
            name: Resource name
            version: Specific version (defaults to latest)
            
        Returns:
            Resource file content as bytes
        """
        if version is not None:
            endpoint = f"/resources/{name}/download?version={version}"
        else:
            endpoint = f"/resources/{name}/download"

        response = self.get(endpoint)
        return response.content
    
    def upload_resource(
        self, 
        name: str, 
        file_path: str, 
        resource_type: str,
        description: Optional[str] = None,
        filename: Optional[str] = None,
        allow_duplicate_name: bool = False
    ) -> Dict[str, Any]:
        """
        Upload a resource file.
        
        Args:
            name: Resource name
            file_path: Path to file to upload
            resource_type: Type of resource (urdf, mjcf, etc.)
            description: Optional description
            filename: Optional custom filename
            allow_duplicate_name: Allow creating new version with existing name
            
        Returns:
            Created resource data
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if description:
                data['description'] = description
            if filename:
                data['filename'] = filename
                
            params = {
                'resource_type': resource_type,
                'allow_duplicate_name': allow_duplicate_name
            }
            
            response = self.post(f"/resources/{name}/upload", files=files, params=params)
            return response.json()
    
    def get_resource_types(self) -> List[str]:
        """Get list of all available resource types."""
        response = self.get("/resources/types")
        return response.json()
    
    def delete_resource(self, name: str, version: Optional[int] = None) -> None:
        """
        Delete a resource.
        
        Args:
            name: Resource name
            version: Specific version to delete (if None, deletes all versions)
        """
        if version is not None:
            endpoint = f"/resources/{name}/{version}"
        else:
            endpoint = f"/resources/{name}"
        
        self.delete(endpoint)
    
    def get_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of all scenarios."""
        response = self.get("/scenarios")
        return response.json()
    
    def get_scenario(self, uuid: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a specific scenario.
        
        Args:
            uuid: Scenario UUID
            version: Specific version (defaults to latest)
            
        Returns:
            Scenario data
        """
        if version is not None:
            endpoint = f"/scenarios/{uuid}/{version}"
        else:
            endpoint = f"/scenarios/{uuid}"
        
        response = self.get(endpoint)
        return response.json()
    
    # Run CI API methods
    
    def create_project(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            Created project data
        """
        data = {"name": name}
        if description:
            data["description"] = description
            
        response = self.post("/projects", data=data)
        return response.json()
    
    def get_projects(
        self, 
        limit: int = 20, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of projects.
        
        Args:
            limit: Maximum number of projects to return
            offset: Number of projects to skip
            
        Returns:
            Project list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        response = self.get("/projects", params=params)
        return response.json()
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data
        """
        response = self.get(f"/projects/{project_id}")
        return response.json()
    
    def delete_project(self, project_id: str) -> None:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
        """
        self.delete(f"/projects/{project_id}")
    
    def create_run(
        self, 
        name: str, 
        project_id: str,
        description: Optional[str] = None,
        arguments: Optional[List[Dict[str, str]]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new run.
        
        Args:
            name: Run name
            project_id: Project ID
            description: Optional run description
            arguments: Optional list of key-value arguments
            tags: Optional list of tags
            
        Returns:
            Created run data with runId
        """
        data = {
            "name": name,
            "project_id": project_id,
            "arguments": arguments or [],
            "tags": tags or []
        }
        if description:
            data["description"] = description
            
        response = self.post("/runs", data=data)
        return response.json()
    
    def get_runs(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of runs.
        
        Args:
            project_id: Filter by project ID
            status: Filter by status (running, finished, failed, killed)
            tags: Filter by tags
            limit: Maximum number of runs to return
            offset: Number of runs to skip
            
        Returns:
            Run list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        if project_id:
            params["project_id"] = project_id
        if status:
            params["status"] = status
        if tags:
            params["tags"] = ",".join(tags)
            
        response = self.get("/runs", params=params)
        return response.json()
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get a specific run.
        
        Args:
            run_id: Run ID
            
        Returns:
            Run data
        """
        response = self.get(f"/runs/{run_id}")
        return response.json()
    
    def update_run(
        self,
        run_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        arguments: Optional[List[Dict[str, str]]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update a run.
        
        Args:
            run_id: Run ID
            name: Optional new name
            description: Optional new description
            status: Optional new status
            arguments: Optional new arguments
            tags: Optional new tags
            
        Returns:
            Updated run data
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if status is not None:
            data["status"] = status
        if arguments is not None:
            data["arguments"] = arguments
        if tags is not None:
            data["tags"] = tags
            
        response = self.put(f"/runs/{run_id}", data=data)
        return response.json()
    
    def create_episode(
        self, 
        run_id: str, 
        episode_name: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new episode.
        
        Args:
            run_id: Run ID
            episode_name: Episode name
            status: Optional episode status
            
        Returns:
            Created episode data
        """
        data = {
            "episode_name": episode_name,
            "run_id": run_id
        }
        if status:
            data["status"] = status
            
        response = self.post("/episodes", data=data)
        return response.json()
    
    def get_episodes(
        self,
        run_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of episodes.
        
        Args:
            run_id: Filter by run ID
            status: Filter by status
            limit: Maximum number of episodes to return
            offset: Number of episodes to skip
            
        Returns:
            Episode list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        if run_id:
            params["run_id"] = run_id
        if status:
            params["status"] = status
            
        response = self.get("/episodes", params=params)
        return response.json()
    
    def get_episode(self, run_id: str, episode_name: str) -> Dict[str, Any]:
        """
        Get a specific episode.
        
        Args:
            run_id: Run ID
            episode_name: Episode name
            
        Returns:
            Episode data
        """
        response = self.get(f"/episodes/{run_id}/{episode_name}")
        return response.json()
    
    def update_episode(
        self,
        run_id: str,
        episode_name: str,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an episode.
        
        Args:
            run_id: Run ID
            episode_name: Episode name
            status: Optional new status
            
        Returns:
            Updated episode data
        """
        data = {}
        if status is not None:
            data["status"] = status
            
        response = self.put(f"/episodes/{run_id}/{episode_name}", data=data)
        return response.json()
    
    def delete_episode(self, run_id: str, episode_name: str) -> None:
        """
        Delete an episode.
        
        Args:
            run_id: Run ID
            episode_name: Episode name
        """
        self.delete(f"/episodes/{run_id}/{episode_name}")
    
    def upload_blob(
        self,
        artifact_key: str,
        run_id: str,
        file_path: str,
        artifact_type: str,
        episode_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a blob artifact (image/video).
        
        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            file_path: Path to file to upload
            artifact_type: Type of artifact ('image' or 'video')
            episode_name: Optional episode name (None for run-level artifacts)
            description: Optional description
            
        Returns:
            Created artifact data
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            form_data = {
                'artifact_key': artifact_key,
                'run_id': run_id,
                'artifact_type': artifact_type
            }
            if episode_name:
                form_data['episode_name'] = episode_name
            if description:
                form_data['description'] = description
                
            response = self.post("/artifacts/blob/upload", files=files, data=form_data)
            return response.json()
    
    def upsert_metrics(
        self,
        artifact_key: str,
        run_id: str,
        metric_type: str,
        metric_data: List[Dict[str, Any]],
        episode_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upsert metrics artifact (create or append).
        
        Args:
            artifact_key: Artifact key identifier
            run_id: Run ID
            metric_type: Type of metric display ('line', 'bar', 'scatter', 'gauge', 'counter')
            metric_data: List of metric data points with 'key', 'values', 'timestamp'
            episode_name: Optional episode name (None for run-level artifacts)
            description: Optional description
            
        Returns:
            Created/updated artifact data
        """
        data = {
            "artifact_key": artifact_key,
            "run_id": run_id,
            "metric_type": metric_type,
            "metric_data": metric_data
        }
        if episode_name:
            data["episode_name"] = episode_name
        if description:
            data["description"] = description
            
        response = self.post("/artifacts/metrics", data=data)
        return response.json()
    
    def get_artifacts(
        self,
        run_id: Optional[str] = None,
        episode_name: Optional[str] = None,
        artifact_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get list of artifacts.
        
        Args:
            run_id: Filter by run ID
            episode_name: Filter by episode name
            artifact_type: Filter by artifact type
            limit: Maximum number of artifacts to return
            offset: Number of artifacts to skip
            
        Returns:
            Artifact list with pagination info
        """
        params = {"limit": limit, "offset": offset}
        if run_id:
            params["run_id"] = run_id
        if episode_name:
            params["episode_name"] = episode_name
        if artifact_type:
            params["artifact_type"] = artifact_type
            
        response = self.get("/artifacts", params=params)
        return response.json()
    
    def get_artifact(
        self, 
        run_id: str, 
        episode_name: str, 
        artifact_key: str
    ) -> Dict[str, Any]:
        """
        Get a specific artifact.
        
        Args:
            run_id: Run ID
            episode_name: Episode name
            artifact_key: Artifact key
            
        Returns:
            Artifact data
        """
        response = self.get(f"/artifacts/{run_id}/{episode_name}/{artifact_key}")
        return response.json()
    
    def download_artifact_blob(
        self, 
        run_id: str, 
        episode_name: str, 
        artifact_key: str
    ) -> bytes:
        """
        Download a blob artifact file.
        
        Args:
            run_id: Run ID
            episode_name: Episode name
            artifact_key: Artifact key
            
        Returns:
            Artifact file content as bytes
        """
        response = self.get(f"/artifacts/{run_id}/{episode_name}/{artifact_key}/download")
        return response.content
