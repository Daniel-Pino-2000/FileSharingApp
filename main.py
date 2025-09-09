#!/usr/bin/env python3
"""
Google Drive Sync Manager - Main Entry Point

Author: [Your Name]
Version: 2.1.0
License: MIT
"""

import sys
import logging
from tkinter import messagebox

from gui.main_window import GoogleDriveSyncApp


def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('gdrive_sync.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main application entry point"""
    logger = logging.getLogger(__name__)

    try:
        setup_logging()
        logger.info("Starting Google Drive Sync Manager v2.1.0")

        # Create and run application
        app = GoogleDriveSyncApp()
        app.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        try:
            messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")
        except:
            print(f"Fatal Error: Application failed to start: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()