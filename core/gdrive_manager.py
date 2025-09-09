"""
Google Drive API Manager

Handles all Google Drive API operations including authentication,
file operations, and folder management.
"""

import os
import logging
from typing import List, Callable, Optional

try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from pydrive.files import GoogleDriveFile
except ImportError:
    raise ImportError("PyDrive not installed. Run: pip install PyDrive")

from models.data_models import FileItem

logger = logging.getLogger(__name__)


class GoogleDriveManager:
    """Handles Google Drive operations"""

    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.drive = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive"""
        try:
            gauth = GoogleAuth()
            gauth.LoadCredentialsFile(self.credentials_file)

            if gauth.credentials is None:
                logger.info("No stored credentials found, starting OAuth flow")
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                logger.info("Access token expired, refreshing")
                gauth.Refresh()
            else:
                logger.info("Using stored credentials")
                gauth.Authorize()

            gauth.SaveCredentialsFile(self.credentials_file)
            self.drive = GoogleDrive(gauth)
            logger.info("Successfully authenticated with Google Drive")

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test if connection to Google Drive is working"""
        try:
            # Try to list root folder
            self.drive.ListFile({'q': "'root' in parents and trashed=false", 'maxResults': 1}).GetList()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def list_files(self, parent_id: str = "root") -> List[FileItem]:
        """List files in a specific folder"""
        try:
            logger.debug(f"Listing files in folder: {parent_id}")
            query = f"'{parent_id}' in parents and trashed=false"
            file_list = self.drive.ListFile({'q': query}).GetList()

            items = []
            for f in file_list:
                try:
                    items.append(FileItem(
                        id=f['id'],
                        title=f['title'],
                        size=int(f.get('fileSize', 0)),
                        modified_date=f.get('modifiedDate', ''),
                        mime_type=f.get('mimeType', ''),
                        is_folder=f.get('mimeType') == 'application/vnd.google-apps.folder',
                        parent_id=parent_id
                    ))
                except ValueError as e:
                    logger.warning(f"Skipping invalid file item: {e}")
                    continue

            # Sort: folders first, then by name
            items.sort(key=lambda x: (not x.is_folder, x.title.lower()))
            logger.info(f"Listed {len(items)} files from folder {parent_id}")
            return items

        except Exception as e:
            logger.error(f"Failed to list files in {parent_id}: {e}")
            raise

    def upload_file(self, file_path: str, parent_id: str = "root",
                    progress_callback: Optional[Callable[[str], None]] = None) -> str:
        """Upload a single file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_name = os.path.basename(file_path)
            logger.info(f"Starting upload: {file_name} to folder {parent_id}")

            if progress_callback:
                progress_callback(f"Uploading {file_name}...")

            gfile = self.drive.CreateFile({
                'title': file_name,
                'parents': [{'id': parent_id}]
            })

            gfile.SetContentFile(file_path)
            gfile.Upload()

            logger.info(f"Successfully uploaded {file_name} (ID: {gfile['id']})")
            return gfile['id']

        except Exception as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            raise

    def upload_folder_recursive(self, local_folder: str, parent_id: str = "root",
                                progress_callback: Optional[Callable[[str], None]] = None) -> str:
        """Upload a folder and all its contents recursively"""
        try:
            if not os.path.exists(local_folder):
                raise FileNotFoundError(f"Folder not found: {local_folder}")

            folder_name = os.path.basename(local_folder)
            logger.info(f"Starting recursive folder upload: {folder_name}")

            # Create the main folder
            folder_id = self.create_folder(folder_name, parent_id)
            folder_map = {'.': folder_id}  # Track created folders

            # Walk through all files and directories
            for root, dirs, files in os.walk(local_folder):
                # Calculate relative path from the base folder
                rel_path = os.path.relpath(root, local_folder)
                current_parent_id = folder_map.get(rel_path, folder_id)

                # Create subdirectories
                for dir_name in dirs:
                    dir_rel_path = os.path.join(rel_path, dir_name) if rel_path != '.' else dir_name

                    if progress_callback:
                        progress_callback(f"Creating folder: {dir_rel_path}")

                    subfolder_id = self.create_folder(dir_name, current_parent_id)
                    folder_map[dir_rel_path] = subfolder_id

                # Upload files in current directory
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    file_rel_path = os.path.join(rel_path, file_name) if rel_path != '.' else file_name

                    if progress_callback:
                        progress_callback(f"Uploading: {file_rel_path}")

                    self.upload_file(file_path, current_parent_id)

            logger.info(f"Successfully uploaded folder: {folder_name}")
            return folder_id

        except Exception as e:
            logger.error(f"Failed to upload folder {local_folder}: {e}")
            raise

    def download_file(self, file_id: str, save_path: str,
                      progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """Download a file"""
        try:
            logger.info(f"Starting download: {file_id} to {save_path}")

            if progress_callback:
                progress_callback(f"Downloading {os.path.basename(save_path)}...")

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            gfile = self.drive.CreateFile({'id': file_id})
            gfile.GetContentFile(save_path)

            logger.info(f"Successfully downloaded to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            raise

    def create_folder(self, folder_name: str, parent_id: str = "root") -> str:
        """Create a new folder"""
        try:
            logger.info(f"Creating folder: {folder_name} in {parent_id}")

            folder = self.drive.CreateFile({
                'title': folder_name,
                'parents': [{'id': parent_id}],
                'mimeType': 'application/vnd.google-apps.folder'
            })
            folder.Upload()

            logger.info(f"Created folder: {folder_name} (ID: {folder['id']})")
            return folder['id']

        except Exception as e:
            logger.error(f"Failed to create folder {folder_name}: {e}")
            raise

    def delete_file(self, file_id: str) -> bool:
        """Delete a file or folder"""
        try:
            logger.info(f"Deleting file: {file_id}")
            gfile = self.drive.CreateFile({'id': file_id})
            gfile.Delete()
            logger.info(f"Successfully deleted file: {file_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            raise

    def get_file_info(self, file_id: str) -> Optional[FileItem]:
        """Get detailed information about a specific file"""
        try:
            gfile = self.drive.CreateFile({'id': file_id})
            gfile.FetchMetadata()

            return FileItem(
                id=gfile['id'],
                title=gfile['title'],
                size=int(gfile.get('fileSize', 0)),
                modified_date=gfile.get('modifiedDate', ''),
                mime_type=gfile.get('mimeType', ''),
                is_folder=gfile.get('mimeType') == 'application/vnd.google-apps.folder',
                parent_id=gfile.get('parents', [{'id': 'root'}])[0]['id']
            )

        except Exception as e:
            logger.error(f"Failed to get file info for {file_id}: {e}")
            return None