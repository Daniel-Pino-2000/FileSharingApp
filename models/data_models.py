"""
Data models for Google Drive Sync Manager

Contains data classes and structures used throughout the application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FileItem:
    """Data class for file information"""
    id: str
    title: str
    size: int
    modified_date: str
    mime_type: str
    is_folder: bool = False
    parent_id: str = "root"

    def __post_init__(self):
        """Post-init validation"""
        if not self.id:
            raise ValueError("File ID cannot be empty")
        if not self.title:
            raise ValueError("File title cannot be empty")


@dataclass
class UploadProgress:
    """Data class for tracking upload progress"""
    current_file: str
    completed: int
    total: int
    status: str = "Processing"

    @property
    def percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100.0


@dataclass
class NavigationState:
    """Data class for navigation state"""
    current_folder_id: str
    current_folder_name: str
    history: list

    def __post_init__(self):
        if self.history is None:
            self.history = []