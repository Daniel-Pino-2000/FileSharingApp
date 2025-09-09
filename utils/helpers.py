"""
Utility functions for Google Drive Sync Manager

Contains helper functions for formatting, validation, and common operations.
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = float(size_bytes)

    for unit in units:
        if size < 1024.0:
            if unit == 'B':
                return f"{int(size)} {unit}"
            else:
                return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} {units[-1]}"


def format_datetime(date_str: str) -> str:
    """Format ISO datetime string to readable format"""
    if not date_str:
        return "-"

    try:
        # Handle different datetime formats
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        elif '+' not in date_str and date_str.count('T') == 1:
            date_str += '+00:00'

        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%Y-%m-%d %H:%M')

    except ValueError:
        # Fallback for malformed dates
        try:
            return date_str[:16].replace('T', ' ')
        except:
            return date_str if len(date_str) <= 20 else date_str[:20]


def get_file_type_description(mime_type: str) -> str:
    """Get human readable file type from MIME type"""
    if not mime_type:
        return "Unknown"

    # Common MIME type mappings
    type_mappings = {
        # Documents
        'application/pdf': 'PDF Document',
        'application/msword': 'Word Document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Document',
        'application/vnd.ms-excel': 'Excel Spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel Spreadsheet',
        'application/vnd.ms-powerpoint': 'PowerPoint Presentation',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint Presentation',

        # Text files
        'text/plain': 'Text File',
        'text/html': 'HTML File',
        'text/css': 'CSS File',
        'text/javascript': 'JavaScript File',
        'application/json': 'JSON File',
        'application/xml': 'XML File',
        'text/csv': 'CSV File',

        # Images
        'image/jpeg': 'JPEG Image',
        'image/jpg': 'JPEG Image',
        'image/png': 'PNG Image',
        'image/gif': 'GIF Image',
        'image/bmp': 'BMP Image',
        'image/svg+xml': 'SVG Image',
        'image/tiff': 'TIFF Image',

        # Audio
        'audio/mpeg': 'MP3 Audio',
        'audio/wav': 'WAV Audio',
        'audio/ogg': 'OGG Audio',
        'audio/flac': 'FLAC Audio',

        # Video
        'video/mp4': 'MP4 Video',
        'video/avi': 'AVI Video',
        'video/mov': 'MOV Video',
        'video/wmv': 'WMV Video',
        'video/mkv': 'MKV Video',

        # Archives
        'application/zip': 'ZIP Archive',
        'application/x-rar-compressed': 'RAR Archive',
        'application/x-tar': 'TAR Archive',
        'application/gzip': 'GZIP Archive',
        'application/x-7z-compressed': '7Z Archive',

        # Google Drive specific
        'application/vnd.google-apps.folder': 'Folder',
        'application/vnd.google-apps.document': 'Google Doc',
        'application/vnd.google-apps.spreadsheet': 'Google Sheet',
        'application/vnd.google-apps.presentation': 'Google Slides',
        'application/vnd.google-apps.drawing': 'Google Drawing',
        'application/vnd.google-apps.form': 'Google Form',
    }

    # Check exact match first
    if mime_type in type_mappings:
        return type_mappings[mime_type]

    # Try to extract general type
    if '/' in mime_type:
        main_type, sub_type = mime_type.split('/', 1)
        if main_type in ['image', 'audio', 'video', 'text']:
            return f"{main_type.capitalize()} File"

    # Fallback to MIME type or generic
    return mime_type.replace('application/', '').replace('/', ' ').title()


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """Validate if a file path is valid and accessible"""
    try:
        path = Path(file_path)

        if not path.exists():
            return False, "File or directory does not exist"

        if not path.is_file() and not path.is_dir():
            return False, "Path is neither a file nor directory"

        if not os.access(file_path, os.R_OK):
            return False, "No read permission for this path"

        return True, "Valid path"

    except Exception as e:
        return False, f"Invalid path: {str(e)}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    if not filename:
        return "untitled"

    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')

    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"

    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        max_name_len = 255 - len(ext)
        sanitized = name[:max_name_len] + ext

    return sanitized


def get_folder_size(folder_path: str) -> int:
    """Calculate total size of all files in a folder recursively"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    continue
    except Exception as e:
        logger.warning(f"Error calculating folder size for {folder_path}: {e}")

    return total_size


def count_files_in_folder(folder_path: str) -> Tuple[int, int]:
    """Count files and directories in a folder recursively"""
    file_count = 0
    dir_count = 0

    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            file_count += len(filenames)
            dir_count += len(dirnames)
    except Exception as e:
        logger.warning(f"Error counting items in {folder_path}: {e}")

    return file_count, dir_count


def create_backup_name(original_name: str) -> str:
    """Create a backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_name)
    return f"{name}_backup_{timestamp}{ext}"


def is_hidden_file(filename: str) -> bool:
    """Check if a file is hidden (starts with . on Unix systems)"""
    return filename.startswith('.')


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return os.path.splitext(filename.lower())[1]


def estimate_transfer_time(size_bytes: int, speed_bps: float) -> str:
    """Estimate transfer time based on file size and speed"""
    if speed_bps <= 0:
        return "Unknown"

    seconds = size_bytes / speed_bps

    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m {int(seconds % 60)}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def safe_path_join(*args) -> str:
    """Safely join path components, handling None values"""
    clean_args = [str(arg) for arg in args if arg is not None]
    return os.path.join(*clean_args) if clean_args else ""


def ensure_directory_exists(directory: str) -> bool:
    """Ensure a directory exists, creating it if necessary"""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


class ProgressTracker:
    """Helper class for tracking operation progress"""

    def __init__(self, total_items: int = 0):
        self.total_items = total_items
        self.completed_items = 0
        self.current_item = ""
        self.start_time = datetime.now()
        self.errors = []

    def update(self, completed: int, current_item: str = ""):
        """Update progress"""
        self.completed_items = completed
        self.current_item = current_item

    def add_error(self, error: str):
        """Add an error to the list"""
        self.errors.append(error)
        logger.error(error)

    @property
    def percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100.0

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def estimated_time_remaining(self) -> Optional[float]:
        """Estimate remaining time in seconds"""
        if self.completed_items == 0:
            return None

        elapsed = self.elapsed_time
        rate = self.completed_items / elapsed
        remaining_items = self.total_items - self.completed_items

        if rate > 0:
            return remaining_items / rate
        return None

    def get_status_message(self) -> str:
        """Get formatted status message"""
        if self.current_item:
            return f"Processing: {self.current_item} ({self.completed_items}/{self.total_items})"
        else:
            return f"Progress: {self.completed_items}/{self.total_items} ({self.percentage:.1f}%)"