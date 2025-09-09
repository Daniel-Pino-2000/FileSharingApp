# Google Drive Sync Manager v2.1

A professional file management application for Google Drive with modern UI and advanced features.

## Features

- **Batch Operations**: Upload/download multiple files and folders
- **Progress Tracking**: Real-time progress dialogs for all operations
- **Modern UI**: Clean, intuitive interface with contemporary design
- **Folder Navigation**: Browse your Google Drive with full folder support
- **Auto-Refresh**: Automatic UI updates after upload/download operations
- **Settings Management**: Configurable preferences and behavior
- **Error Handling**: Comprehensive error handling and logging
- **Context Menus**: Right-click support for quick actions

## Project Structure

```
google-drive-sync/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── config/
│   ├── __init__.py
│   └── config_manager.py       # Configuration management
├── core/
│   ├── __init__.py
│   └── gdrive_manager.py       # Google Drive API wrapper
├── gui/
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── dialogs.py              # Dialog components
│   └── theme.py                # UI theme management
├── models/
│   ├── __init__.py
│   └── data_models.py          # Data structures
└── utils/
    ├── __init__.py
    └── helpers.py              # Utility functions
```

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Drive API credentials:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google Drive API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the credentials JSON file
   - Place it in the project directory as `client_secrets.json`

4. **Run the application:**
   ```bash
   python main.py
   ```

## First Time Setup

1. On first run, the application will open a web browser for Google OAuth
2. Sign in to your Google account and grant permissions
3. The credentials will be saved automatically for future use

## Usage

### Navigation
- **Home**: Return to Google Drive root folder
- **Back**: Navigate to previous folder
- **Double-click folders**: Open folders
- **Double-click files**: Download files

### File Operations
- **Upload Files**: Select multiple files to upload
- **Upload Folder**: Upload entire folders recursively
- **Download**: Select files and choose download location
- **Create Folder**: Create new folders in current location
- **Delete**: Remove files and folders (with confirmation)

### Features

#### Progress Tracking
All long-running operations show progress dialogs with:
- Current operation status
- Progress percentage (when applicable)
- Cancel option for most operations

#### Auto-Refresh
The file list automatically refreshes after successful operations when enabled in settings.

#### Settings
Access via Settings button to configure:
- Auto-refresh behavior
- Confirmation dialogs
- Default download location
- Credentials file location
- Logging level

### Keyboard Shortcuts
- **Enter**: Open selected folder or download selected file
- **F5**: Refresh file list
- **Delete**: Delete selected items (with confirmation)

### Context Menu
Right-click on items for quick access to:
- Open (folders)
- Download (files)
- Delete
- Refresh

## Configuration

Settings are automatically saved in `config.json`:

```json
{
  "last_download_path": "/path/to/downloads",
  "auto_refresh": true,
  "confirm_operations": true,
  "theme": "modern",
  "window_geometry": "1000x700",
  "credentials_file": "mycreds.txt",
  "log_level": "INFO"
}
```

## Logging

Application logs are saved to `gdrive_sync.log` with configurable log levels:
- DEBUG: Detailed debugging information
- INFO: General information (default)
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

## Troubleshooting

### Authentication Issues
- Delete `mycreds.txt` to reset credentials
- Ensure `client_secrets.json` is in the project directory
- Check internet connection
- Verify Google Drive API is enabled in Google Cloud Console

### File List Not Updating
- Enable auto-refresh in Settings
- Manually click Refresh button
- Check log file for error messages

### Upload/Download Failures
- Check file permissions
- Verify sufficient disk space
- Ensure stable internet connection
- Check log file for specific error details

## Requirements

- Python 3.7+
- PyDrive library
- Google API credentials
- Internet connection
- Tkinter (usually included with Python)

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Check existing issues on the repository
4. Create a new issue with detailed information

## Version History

### v2.1.0
- Refactored into modular architecture
- Fixed auto-refresh after uploads/downloads
- Improved error handling and user feedback
- Enhanced progress tracking
- Modern UI theme improvements
- Better folder upload support
- Comprehensive logging system

### v2.0.0
- Initial release with GUI
- Basic file operations
- Google Drive integration