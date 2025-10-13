import mongoengine as me
from minio import Minio
import os
import glob
import tempfile
import trimesh
from humalab_service.humalab_host import HumaLabHost
from humalab_service.services.stores.obj_store import ObjStore
from humalab_service.services.stores.namespace import ObjectType
from humalab_service.db.resource import ResourceDocument
from humalab_sdk.assets.archive import extract_archive


ASSET_TYPE_TO_EXTENSIONS = {
    "urdf": {"urdf"},
    "mjcf": {"xml"},
    "mesh": trimesh.available_formats(),
    "usd": {"usd"},
    "controller": {"py"},
    "global_controller": {"py"},
    "terminator": {"py"},
    "data": {},
}

class ResourceHandler:
    def __init__(self, working_path: str=tempfile.gettempdir()):
        self._minio_client = Minio(
            HumaLabHost.get_minio_service_address(),
            access_key="humalab",
            secret_key="humalab123",
            secure=False
        )
        self._obj_store = ObjStore(self._minio_client)
        self.working_path_root = working_path

    def search_resource_file(self, resource_filename: str | None, working_path: str, morph_type: str) -> str | None:
        found_filename = None
        if resource_filename:
            search_path = os.path.join(working_path, "**")
            search_pattern = os.path.join(search_path, resource_filename)
            files = glob.glob(search_pattern, recursive=True)
            if len(files) > 0:
                found_filename = files[0]
        
        if found_filename is None:
            for ext in ASSET_TYPE_TO_EXTENSIONS[morph_type]:
                search_pattern = os.path.join(working_path, "**", f"*.{ext}")
                files = glob.glob(search_pattern, recursive=True)
                if len(files) > 0:
                    found_filename = files[0]
                    break
        return found_filename
    
    def _save_file(self, filepath: str, data: bytes) -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(data)
        return filepath

    def _save_and_extract(self, working_path: str, local_filepath: str, file_content: bytes, file_type: str):
        os.makedirs(working_path, exist_ok=True)
        saved_filepath = self._save_file(local_filepath, file_content)
        _, ext = os.path.splitext(saved_filepath)
        ext = ext.lstrip('.')  # Remove leading dot
        if ext not in ASSET_TYPE_TO_EXTENSIONS[file_type]:
            extract_archive(saved_filepath, working_path)
            try:
                os.remove(saved_filepath)
            except Exception as e:
                print(f"Error removing saved file {saved_filepath}: {e}")

    def save_file(self,
                  resource_name: str,
                  resource_version: int,
                  object_type: ObjectType,
                  file_content: bytes,
                  file_url: str,
                  resource_type: str,
                  filename: str | None = None) -> str:
        working_path = self.get_working_path(object_type, resource_name, resource_version)
        local_filepath = os.path.join(working_path, os.path.basename(file_url))
        local_filename = None
        if os.path.exists(os.path.dirname(working_path)):
            # if directory exists, try to search for the file
            local_filename = self.search_resource_file(filename, working_path, resource_type)
        if local_filename is None:
            # if not found, save the file and extract the archive,
            # then search for the file again
            self._save_and_extract(working_path, local_filepath, file_content, resource_type)
            local_filename = self.search_resource_file(filename, working_path, resource_type)
        if local_filename is None:
            # if still not found, raise an error
            raise ValueError(f"Resource filename {filename} not found in {working_path}")
        return local_filename

    def get_working_path(self, obj_type: ObjectType, uuid: str, version: int) -> str:
        return os.path.join(self.working_path_root, "humalab", obj_type.value, uuid + "_" + str(version))

    def query_and_download_resource(self, resource_name: str, resource_version: int | None = None) -> tuple[str, str]:
        """ Query the resource from the database and download it from the object store.
        Args:
            resource_name (str): The name of the resource.
            resource_version (int | None): The version of the resource. If None, the latest version will be used.
        Returns:
            tuple[str, str]: A tuple containing the local filename of the resource and the working directory
                where the resource was downloaded and extracted.
        """
        me.connect("humalab", host=f"mongodb://{HumaLabHost.get_mongodb_service_address()}")
        if resource_version is None:
            resource = ResourceDocument.objects(name=resource_name.strip(), latest=True).first()
        else:
            resource = ResourceDocument.objects(name=resource_name.strip(), version=resource_version).first()
        if resource is None:
            raise ValueError(f"Resource {resource_name}:{resource_version} not found")
        return self.download_resource(resource.name, resource.version, resource.file_url, resource.resource_type.value, resource.filename)

    def download_resource(self,
                           resource_name: str,
                           resource_version: int,
                           resource_url: str,
                           resource_type: str,
                           resource_filename: str | None = None) -> tuple[str, str]:
        """ Download a resource from the object store.
        Args:
            resource_name (str): The name of the resource.
            resource_version (int): The version of the resource.
            resource_url (str): The URL of the resource in the object store.
            resource_type (str): The type of the resource (e.g., "urdf", "mjcf", "mesh", etc.).
            resource_filename (str | None): The specific filename to search for within the resource directory. If None, the first file found will be used.
        Returns:
            tuple[str, str]: A tuple containing the local filename of the resource and the working directory
                where the resource was downloaded and extracted.
        """
        return self._download_resource(resource_name,
                                       resource_version,
                                       ObjectType.RESOURCE,
                                       resource_url,
                                       resource_type,
                                       resource_filename)

    def _download_resource(self,
                       resource_name: str,
                       resource_version: int,
                       object_type: ObjectType,
                       resource_url: str,
                       resource_type: str,
                       resource_filename: str | None = None) -> tuple[str, str]:
        """
        Download an asset from the object store and extract it if necessary.

        Args:
            asset_uuid (str): The UUID of the asset.
            asset_version (int): The version of the asset.
            asset_type (ObjectType): The type of the asset (e.g., URDF, MJCF, Mesh, etc.).
            asset_url (str): The URL of the asset in the object store.
            asset_file_type (str): The type of the asset file (e.g., "urdf", "mjcf", "mesh", etc.).
            asset_filename (str | None): The specific filename to search for within the asset directory. If None, the first file found will be used.

        Returns:
            tuple[str, str]: A tuple containing the local filename of the asset and the working directory
                where the asset was downloaded and extracted.
        """
        working_path = self.get_working_path(object_type, resource_name, resource_version)
        local_filepath = os.path.join(working_path, os.path.basename(resource_url))
        if not os.path.exists(working_path):
            os.makedirs(working_path, exist_ok=True)
            self._obj_store.download_file(object_type, resource_url, local_filepath)
            _, ext = os.path.splitext(resource_url)
            ext = ext.lower().lstrip('.')
            if ext not in ASSET_TYPE_TO_EXTENSIONS[resource_type]:
                extract_archive(local_filepath, working_path)
        local_filename = self.search_resource_file(resource_filename, working_path, resource_type)
        if local_filename is None:
            raise ValueError(f"Resource filename {resource_filename} not found in {working_path}")
        return local_filename, working_path
