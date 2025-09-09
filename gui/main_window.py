"""
Main application window for Google Drive Sync Manager

Contains the primary UI components and orchestrates the application flow.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import logging
from typing import List, Optional

from config.config_manager import ConfigManager
from core.gdrive_manager import GoogleDriveManager
from models.data_models import FileItem, NavigationState
from gui.theme import ModernTheme
from gui.dialogs import ProgressDialog, SettingsDialog, ConfirmDialog
from utils.helpers import format_file_size, format_datetime, get_file_type_description

logger = logging.getLogger(__name__)


class GoogleDriveSyncApp:
    """Main application class"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.drive_manager = None

        # Navigation state
        self.navigation = NavigationState(
            current_folder_id="root",
            current_folder_name="Root",
            history=[]
        )

        # UI components
        self.root = None
        self.tree = None
        self.status_label = None
        self.file_count_label = None
        self.path_label = None
        self.back_button = None

        # Initialize UI
        self._setup_main_window()
        self._setup_theme()
        self._setup_ui()

        # Initialize Google Drive connection
        self._initialize_drive()

    def _setup_main_window(self):
        """Setup main application window"""
        self.root = tk.Tk()
        self.root.title("Google Drive Sync Manager v2.1")
        self.root.geometry(self.config_manager.get('window_geometry', '1000x700'))
        self.root.minsize(800, 600)

        # Try to set application icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

        # Configure closing behavior
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_theme(self):
        """Apply modern theme to the application"""
        ModernTheme.configure_ttk_style()

    def _setup_ui(self):
        """Setup the complete user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, style="Modern.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Setup UI components
        self._setup_toolbar(main_frame)
        self._setup_navigation(main_frame)
        self._setup_file_list(main_frame)
        self._setup_status_bar(main_frame)

    def _setup_toolbar(self, parent):
        """Setup toolbar with action buttons"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # Upload operations
        upload_frame = ttk.LabelFrame(toolbar_frame, text="Upload", padding="8")
        upload_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            upload_frame,
            text="Files",
            command=self._upload_files,
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            upload_frame,
            text="Folder",
            command=self._upload_folder,
            style="Modern.TButton"
        ).pack(side=tk.LEFT)

        # Download operations
        download_frame = ttk.LabelFrame(toolbar_frame, text="Download", padding="8")
        download_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            download_frame,
            text="Download",
            command=self._download_selected,
            style="Modern.TButton"
        ).pack(side=tk.LEFT)

        # File management
        manage_frame = ttk.LabelFrame(toolbar_frame, text="Manage", padding="8")
        manage_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            manage_frame,
            text="New Folder",
            command=self._create_folder,
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            manage_frame,
            text="Delete",
            command=self._delete_selected,
            style="Modern.TButton"
        ).pack(side=tk.LEFT)

        # Utility operations
        utility_frame = ttk.LabelFrame(toolbar_frame, text="View", padding="8")
        utility_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            utility_frame,
            text="Refresh",
            command=self._refresh_files,
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            utility_frame,
            text="Settings",
            command=self._show_settings,
            style="Modern.TButton"
        ).pack(side=tk.LEFT)

    def _setup_navigation(self, parent):
        """Setup navigation bar"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=(0, 10))

        # Navigation buttons
        self.back_button = ttk.Button(
            nav_frame,
            text="← Back",
            command=self._go_back,
            state=tk.DISABLED,
            style="Modern.TButton"
        )
        self.back_button.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            nav_frame,
            text="🏠 Home",
            command=self._go_home,
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=(0, 15))

        # Current path display
        ttk.Label(
            nav_frame,
            text="Current location:",
            style="Modern.TLabel"
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.path_label = ttk.Label(
            nav_frame,
            text=self.navigation.current_folder_name,
            style="Heading.TLabel"
        )
        self.path_label.pack(side=tk.LEFT)

    def _setup_file_list(self, parent):
        """Setup file list with treeview"""
        # Container frame for treeview and scrollbars
        tree_container = ttk.Frame(parent)
        tree_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure treeview columns - FIXED: Added hidden columns for metadata
        columns = ("Name", "Size", "Modified", "Type", "file_id", "is_folder", "file_title", "mime_type")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Modern.Treeview"
        )

        # Configure visible column headers and properties
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Size", text="Size", anchor=tk.CENTER)
        self.tree.heading("Modified", text="Modified", anchor=tk.CENTER)
        self.tree.heading("Type", text="Type", anchor=tk.CENTER)

        # Configure visible column widths
        self.tree.column("Name", width=350, anchor=tk.W)
        self.tree.column("Size", width=100, anchor=tk.CENTER)
        self.tree.column("Modified", width=150, anchor=tk.CENTER)
        self.tree.column("Type", width=150, anchor=tk.CENTER)

        # Hide the metadata columns - FIXED: Hide columns that store metadata
        self.tree.column("file_id", width=0, stretch=False)
        self.tree.column("is_folder", width=0, stretch=False)
        self.tree.column("file_title", width=0, stretch=False)
        self.tree.column("mime_type", width=0, stretch=False)

        # Hide the headers for metadata columns
        self.tree.heading("file_id", text="")
        self.tree.heading("is_folder", text="")
        self.tree.heading("file_title", text="")
        self.tree.heading("mime_type", text="")

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
        self.tree.bind('<Return>', self._on_item_activate)

    def _setup_status_bar(self, parent):
        """Setup status bar at bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)

        # Status message
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
            style="Modern.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # File count
        self.file_count_label = ttk.Label(
            status_frame,
            text="0 items",
            relief=tk.SUNKEN,
            anchor=tk.CENTER,
            padding=(5, 2),
            style="Modern.TLabel"
        )
        self.file_count_label.pack(side=tk.RIGHT)

    def _initialize_drive(self):
        """Initialize Google Drive connection"""

        def init_thread():
            try:
                self.root.after(0, lambda: self._update_status("Connecting to Google Drive..."))

                credentials_file = self.config_manager.get('credentials_file', 'mycreds.txt')
                self.drive_manager = GoogleDriveManager(credentials_file)

                # Test connection
                if self.drive_manager.test_connection():
                    self.root.after(0, lambda: self._update_status("Connected to Google Drive"))
                    self.root.after(0, self._refresh_files)
                else:
                    raise Exception("Connection test failed")

            except Exception as e:
                logger.error(f"Failed to initialize Google Drive: {e}")
                self.root.after(0, lambda: self._show_drive_error(str(e)))

        threading.Thread(target=init_thread, daemon=True).start()

    def _show_drive_error(self, error_message: str):
        """Show Google Drive connection error"""
        self._update_status("Google Drive connection failed")
        messagebox.showerror(
            "Google Drive Connection Error",
            f"Failed to connect to Google Drive:\n\n{error_message}\n\n"
            "Please check your credentials and internet connection.\n"
            "You can update settings from the Settings menu."
        )

    def _update_status(self, message: str):
        """Update status bar message"""
        if self.status_label and self.status_label.winfo_exists():
            self.status_label.config(text=message)
            self.root.update_idletasks()

    def _refresh_files(self):
        """Refresh the file list from Google Drive"""
        if not self.drive_manager:
            self._update_status("Not connected to Google Drive")
            return

        def refresh_thread():
            try:
                self.root.after(0, lambda: self._update_status("Loading files..."))

                files = self.drive_manager.list_files(self.navigation.current_folder_id)

                # Update UI in main thread
                self.root.after(0, lambda: self._populate_file_list(files))

            except Exception as e:
                logger.error(f"Failed to refresh files: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to load files:\n{str(e)}"
                ))
                self.root.after(0, lambda: self._update_status("Error loading files"))

        threading.Thread(target=refresh_thread, daemon=True).start()

    def _populate_file_list(self, files: List[FileItem]):
        """Populate the file list treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add files to treeview
        for file_item in files:
            # Format display values
            icon = "📁" if file_item.is_folder else "📄"
            display_name = f"{icon} {file_item.title}"
            size_str = "-" if file_item.is_folder else format_file_size(file_item.size)
            modified_str = format_datetime(file_item.modified_date)
            type_str = get_file_type_description(file_item.mime_type)

            # Insert item - FIXED: Include metadata in values tuple
            item_id = self.tree.insert("", tk.END, values=(
                display_name,
                size_str,
                modified_str,
                type_str,
                file_item.id,  # file_id column
                str(file_item.is_folder),  # is_folder column
                file_item.title,  # file_title column
                file_item.mime_type  # mime_type column
            ))

        # Update status and navigation
        file_count = len(files)
        folder_count = sum(1 for f in files if f.is_folder)
        file_only_count = file_count - folder_count

        if folder_count > 0 and file_only_count > 0:
            count_text = f"{folder_count} folders, {file_only_count} files"
        elif folder_count > 0:
            count_text = f"{folder_count} folders"
        elif file_only_count > 0:
            count_text = f"{file_only_count} files"
        else:
            count_text = "Empty"

        self.file_count_label.config(text=count_text)
        self._update_status(f"Loaded {file_count} items")
        self._update_navigation()

    def _update_navigation(self):
        """Update navigation state and buttons"""
        # Update back button
        has_history = len(self.navigation.history) > 0
        self.back_button.config(state=tk.NORMAL if has_history else tk.DISABLED)

        # Update path label
        self.path_label.config(text=self.navigation.current_folder_name)

    def _on_item_double_click(self, event):
        """Handle double-click on file list item"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        # FIXED: Use column index instead of column name for hidden columns
        values = self.tree.item(item, 'values')
        if len(values) > 5:  # Ensure we have metadata columns
            is_folder = values[5] == 'True'  # is_folder column index
            file_id = values[4]  # file_id column index
            folder_name = values[6]  # file_title column index

            if is_folder:
                # Navigate to folder
                self._navigate_to_folder(file_id, folder_name)
            else:
                # Download file
                self._download_selected()

    def _on_item_activate(self, event):
        """Handle Enter key on selected item"""
        self._on_item_double_click(event)

    def _navigate_to_folder(self, folder_id: str, folder_name: str):
        """Navigate to a specific folder"""
        # Save current location to history
        self.navigation.history.append((
            self.navigation.current_folder_id,
            self.navigation.current_folder_name
        ))

        # Update navigation state
        self.navigation.current_folder_id = folder_id
        self.navigation.current_folder_name = folder_name

        # Refresh file list
        self._refresh_files()

    def _go_back(self):
        """Navigate back to previous folder"""
        if not self.navigation.history:
            return

        folder_id, folder_name = self.navigation.history.pop()
        self.navigation.current_folder_id = folder_id
        self.navigation.current_folder_name = folder_name

        self._refresh_files()

    def _go_home(self):
        """Navigate to root folder"""
        self.navigation.history.clear()
        self.navigation.current_folder_id = "root"
        self.navigation.current_folder_name = "Root"

        self._refresh_files()

    def _upload_files(self):
        """Upload multiple files"""
        if not self.drive_manager:
            messagebox.showwarning("No Connection", "Not connected to Google Drive")
            return

        file_paths = filedialog.askopenfilenames(
            title="Select files to upload",
            initialdir=self.config_manager.get('last_download_path', '')
        )

        if file_paths:
            self._perform_file_upload(list(file_paths))

    def _upload_folder(self):
        """Upload a folder recursively"""
        if not self.drive_manager:
            messagebox.showwarning("No Connection", "Not connected to Google Drive")
            return

        folder_path = filedialog.askdirectory(
            title="Select folder to upload",
            initialdir=self.config_manager.get('last_download_path', '')
        )

        if folder_path:
            self._perform_folder_upload(folder_path)

    def _perform_file_upload(self, file_paths: List[str]):
        """Perform file upload operation with progress tracking"""
        progress_dialog = ProgressDialog(self.root, "Uploading Files")

        def upload_thread():
            try:
                total_files = len(file_paths)
                uploaded_count = 0

                for i, file_path in enumerate(file_paths):
                    if progress_dialog.cancelled:
                        break

                    filename = os.path.basename(file_path)
                    progress = (i / total_files) * 100

                    progress_dialog.update_status(
                        f"Uploading: {filename} ({i + 1}/{total_files})",
                        progress
                    )

                    self.drive_manager.upload_file(
                        file_path,
                        self.navigation.current_folder_id
                    )
                    uploaded_count += 1

                # Show completion message
                if not progress_dialog.cancelled and uploaded_count > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Upload Complete",
                        f"Successfully uploaded {uploaded_count} file{'s' if uploaded_count != 1 else ''}"
                    ))

                    # Refresh file list
                    if self.config_manager.get('auto_refresh', True):
                        self.root.after(0, self._refresh_files)

            except Exception as e:
                logger.error(f"Upload failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Upload Error",
                    f"Upload failed:\n{str(e)}"
                ))
            finally:
                self.root.after(0, progress_dialog.close)

        threading.Thread(target=upload_thread, daemon=True).start()

    def _perform_folder_upload(self, folder_path: str):
        """Perform folder upload operation with progress tracking"""
        progress_dialog = ProgressDialog(self.root, "Uploading Folder")

        def upload_thread():
            try:
                folder_name = os.path.basename(folder_path)
                progress_dialog.update_status(f"Uploading folder: {folder_name}")

                self.drive_manager.upload_folder_recursive(
                    folder_path,
                    self.navigation.current_folder_id,
                    progress_callback=progress_dialog.update_status
                )

                if not progress_dialog.cancelled:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Upload Complete",
                        f"Successfully uploaded folder: {folder_name}"
                    ))

                    # Refresh file list
                    if self.config_manager.get('auto_refresh', True):
                        self.root.after(0, self._refresh_files)

            except Exception as e:
                logger.error(f"Folder upload failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Upload Error",
                    f"Folder upload failed:\n{str(e)}"
                ))
            finally:
                self.root.after(0, progress_dialog.close)

        threading.Thread(target=upload_thread, daemon=True).start()

    def _download_selected(self):
        """Download selected files"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select files to download")
            return

        # Filter out folders (for now)
        files_to_download = []
        for item in selection:
            values = self.tree.item(item, 'values')
            if len(values) > 5 and values[5] != 'True':  # Check is_folder column
                files_to_download.append(item)

        if not files_to_download:
            messagebox.showwarning(
                "No Files Selected",
                "Only files can be downloaded (folders not supported yet)"
            )
            return

        # Choose download location
        save_path = filedialog.askdirectory(
            title="Select download location",
            initialdir=self.config_manager.get('last_download_path', '')
        )

        if save_path:
            self.config_manager.set('last_download_path', save_path)
            self.config_manager.save_config()
            self._perform_download(files_to_download, save_path)

    def _perform_download(self, items: List[str], save_path: str):
        """Perform download operation with progress tracking"""
        progress_dialog = ProgressDialog(self.root, "Downloading Files")

        def download_thread():
            try:
                total_files = len(items)
                downloaded_count = 0

                for i, item in enumerate(items):
                    if progress_dialog.cancelled:
                        break

                    values = self.tree.item(item, 'values')
                    if len(values) > 6:
                        file_id = values[4]  # file_id column
                        file_name = values[6]  # file_title column

                        progress = (i / total_files) * 100
                        progress_dialog.update_status(
                            f"Downloading: {file_name} ({i + 1}/{total_files})",
                            progress
                        )

                        file_save_path = os.path.join(save_path, file_name)
                        self.drive_manager.download_file(file_id, file_save_path)
                        downloaded_count += 1

                if not progress_dialog.cancelled and downloaded_count > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Download Complete",
                        f"Successfully downloaded {downloaded_count} file{'s' if downloaded_count != 1 else ''} to:\n{save_path}"
                    ))

            except Exception as e:
                logger.error(f"Download failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Download Error",
                    f"Download failed:\n{str(e)}"
                ))
            finally:
                self.root.after(0, progress_dialog.close)

        threading.Thread(target=download_thread, daemon=True).start()

    def _create_folder(self):
        """Create a new folder"""
        if not self.drive_manager:
            messagebox.showwarning("No Connection", "Not connected to Google Drive")
            return

        folder_name = simpledialog.askstring(
            "Create Folder",
            "Enter folder name:",
            parent=self.root
        )

        if folder_name and folder_name.strip():
            self._perform_folder_creation(folder_name.strip())

    def _perform_folder_creation(self, folder_name: str):
        """Perform folder creation operation"""

        def create_thread():
            try:
                self.root.after(0, lambda: self._update_status(f"Creating folder: {folder_name}"))

                self.drive_manager.create_folder(
                    folder_name,
                    self.navigation.current_folder_id
                )

                self.root.after(0, lambda: self._update_status(f"Created folder: {folder_name}"))

                # Refresh file list
                if self.config_manager.get('auto_refresh', True):
                    self.root.after(0, self._refresh_files)

            except Exception as e:
                logger.error(f"Folder creation failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to create folder:\n{str(e)}"
                ))
                self.root.after(0, lambda: self._update_status("Ready"))

        threading.Thread(target=create_thread, daemon=True).start()

    def _delete_selected(self):
        """Delete selected files and folders"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select items to delete")
            return

        # Confirm deletion if enabled
        if self.config_manager.get('confirm_operations', True):
            item_count = len(selection)
            confirm_dialog = ConfirmDialog(
                self.root,
                "Confirm Delete",
                f"Are you sure you want to delete {item_count} item{'s' if item_count != 1 else ''}?\n\nThis action cannot be undone.",
                "Delete",
                "Cancel"
            )

            if not confirm_dialog.show():
                return

        self._perform_deletion(selection)

    def _perform_deletion(self, items: List[str]):
        """Perform deletion operation with progress tracking"""
        progress_dialog = ProgressDialog(self.root, "Deleting Items")

        def delete_thread():
            try:
                total_items = len(items)
                deleted_count = 0

                for i, item in enumerate(items):
                    if progress_dialog.cancelled:
                        break

                    values = self.tree.item(item, 'values')
                    if len(values) > 6:
                        file_id = values[4]  # file_id column
                        file_name = values[6]  # file_title column

                        progress = (i / total_items) * 100
                        progress_dialog.update_status(
                            f"Deleting: {file_name} ({i + 1}/{total_items})",
                            progress
                        )

                        self.drive_manager.delete_file(file_id)
                        deleted_count += 1

                if not progress_dialog.cancelled and deleted_count > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Delete Complete",
                        f"Successfully deleted {deleted_count} item{'s' if deleted_count != 1 else ''}"
                    ))

                    # Refresh file list
                    if self.config_manager.get('auto_refresh', True):
                        self.root.after(0, self._refresh_files)

            except Exception as e:
                logger.error(f"Deletion failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Delete Error",
                    f"Delete failed:\n{str(e)}"
                ))
            finally:
                self.root.after(0, progress_dialog.close)

        threading.Thread(target=delete_thread, daemon=True).start()

    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            # Select the item that was right-clicked
            self.tree.selection_set(item)

            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)

            values = self.tree.item(item, 'values')
            if len(values) > 5:
                is_folder = values[5] == 'True'  # is_folder column

                if is_folder:
                    context_menu.add_command(label="Open", command=lambda: self._on_item_double_click(event))
                    context_menu.add_separator()
                else:
                    context_menu.add_command(label="Download", command=self._download_selected)
                    context_menu.add_separator()

                context_menu.add_command(label="Delete", command=self._delete_selected)
                context_menu.add_separator()
                context_menu.add_command(label="Refresh", command=self._refresh_files)

                try:
                    context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    context_menu.grab_release()

    def _show_settings(self):
        """Show settings dialog"""
        settings_dialog = SettingsDialog(self.root, self.config_manager)
        self.root.wait_window(settings_dialog.dialog)

    def _on_closing(self):
        """Handle application closing"""
        try:
            # Save window geometry
            geometry = self.root.geometry()
            self.config_manager.set('window_geometry', geometry)
            self.config_manager.save_config()

            logger.info("Application closing gracefully")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

        finally:
            self.root.destroy()

    def run(self):
        """Start the application main loop"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise