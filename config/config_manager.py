"""
Configuration management for Google Drive Sync Manager

Handles loading, saving, and managing application configuration.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Handle application configuration"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            "last_download_path": str(Path.home() / "Downloads"),
            "auto_refresh": True,
            "confirm_operations": True,
            "theme": "modern",
            "window_geometry": "1000x700",
            "credentials_file": "mycreds.txt",
            "log_level": "INFO",
            "max_concurrent_uploads": 3,
            "chunk_size": 8192
        }
        self._config = None

    @property
    def config(self) -> Dict[str, Any]:
        """Get configuration dictionary"""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults for missing keys
                config = {**self.default_config, **loaded_config}
                logger.info("Configuration loaded successfully")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

        logger.info("Using default configuration")
        return self.default_config.copy()

    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

            logger.info("Configuration saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self.default_config.copy()
        logger.info("Configuration reset to defaults")