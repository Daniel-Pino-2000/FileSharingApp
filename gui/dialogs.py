"""
Dialog components for Google Drive Sync Manager

Contains progress dialogs, settings dialog, and other modal windows.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
import os

from config.config_manager import ConfigManager


class ProgressDialog:
    """Progress dialog for long-running operations"""

    def __init__(self, parent, title: str = "Processing...", cancellable: bool = True):
        self.parent = parent
        self.title = title
        self.cancellable = cancellable
        self.cancelled = False

        # Ensure theme is configured
        self._ensure_theme()
        self._create_dialog()

    def _ensure_theme(self):
        """Ensure theme is configured before creating UI"""
        try:
            from gui.theme import ModernTheme
            ModernTheme.configure_ttk_style()
        except Exception:
            # If theme configuration fails, continue with default styles
            pass

    def _create_dialog(self):
        """Create the progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("450x180")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Center the dialog
        self._center_dialog()

        # Prevent closing with X button unless cancellable
        if not self.cancellable:
            self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        else:
            self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)

        self._setup_ui()

    def _center_dialog(self):
        """Center dialog on parent"""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width - 450) // 2
        y = parent_y + (parent_height - 180) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Setup progress dialog UI"""
        # Try to use Modern.TFrame style with fallback
        try:
            main_frame = ttk.Frame(self.dialog, padding="20", style="Modern.TFrame")
        except tk.TclError:
            main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        try:
            title_label = ttk.Label(
                main_frame,
                text=self.title,
                style="Heading.TLabel"
            )
        except tk.TclError:
            title_label = ttk.Label(
                main_frame,
                text=self.title,
                font=('Segoe UI', 10, 'bold')
            )
        title_label.pack(pady=(0, 15))

        # Status label
        try:
            self.status_label = ttk.Label(
                main_frame,
                text="Initializing...",
                style="Modern.TLabel"
            )
        except tk.TclError:
            self.status_label = ttk.Label(
                main_frame,
                text="Initializing..."
            )
        self.status_label.pack(pady=(0, 10))

        # Progress bar with robust style handling
        try:
            self.progress = ttk.Progressbar(
                main_frame,
                mode='indeterminate',
                style="Modern.TProgressbar"
            )
        except tk.TclError:
            # Fallback to default style
            self.progress = ttk.Progressbar(
                main_frame,
                mode='indeterminate'
            )
        self.progress.pack(fill=tk.X, pady=(0, 15))
        self.progress.start(10)  # Update every 10ms

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        if self.cancellable:
            try:
                self.cancel_button = ttk.Button(
                    button_frame,
                    text="Cancel",
                    command=self.cancel,
                    style="Modern.TButton"
                )
            except tk.TclError:
                self.cancel_button = ttk.Button(
                    button_frame,
                    text="Cancel",
                    command=self.cancel
                )
            self.cancel_button.pack(side=tk.RIGHT)

    def update_status(self, status: str, progress: Optional[float] = None):
        """Update status text and optionally progress"""
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=status)

            # Update progress bar if specific progress given
            if progress is not None:
                if hasattr(self, 'progress'):
                    self.progress.config(mode='determinate')
                    self.progress.config(value=progress)

            self.dialog.update()

    def cancel(self):
        """Cancel operation"""
        self.cancelled = True
        if hasattr(self, 'cancel_button'):
            self.cancel_button.config(state=tk.DISABLED, text="Cancelling...")
        self.update_status("Cancelling operation...")

    def close(self):
        """Close dialog"""
        if hasattr(self, 'progress') and self.progress.winfo_exists():
            self.progress.stop()
        if hasattr(self, 'dialog') and self.dialog.winfo_exists():
            self.dialog.destroy()


class SettingsDialog:
    """Settings configuration dialog"""

    def __init__(self, parent, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.dialog = None

        # Variables for settings
        self.auto_refresh_var = tk.BooleanVar()
        self.confirm_ops_var = tk.BooleanVar()
        self.download_path_var = tk.StringVar()
        self.creds_path_var = tk.StringVar()
        self.log_level_var = tk.StringVar()

        self._load_current_settings()
        self._ensure_theme()
        self._create_dialog()

    def _ensure_theme(self):
        """Ensure theme is configured before creating UI"""
        try:
            from gui.theme import ModernTheme
            ModernTheme.configure_ttk_style()
        except Exception:
            pass

    def _load_current_settings(self):
        """Load current settings into variables"""
        self.auto_refresh_var.set(self.config_manager.get('auto_refresh', True))
        self.confirm_ops_var.set(self.config_manager.get('confirm_operations', True))
        self.download_path_var.set(self.config_manager.get('last_download_path', ''))
        self.creds_path_var.set(self.config_manager.get('credentials_file', 'mycreds.txt'))
        self.log_level_var.set(self.config_manager.get('log_level', 'INFO'))

    def _create_dialog(self):
        """Create settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings - Google Drive Sync Manager")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Center dialog
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        x = parent_x + 50
        y = parent_y + 50
        self.dialog.geometry(f"+{x}+{y}")

        self._setup_ui()

    def _setup_ui(self):
        """Setup settings dialog UI"""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook for tabs with robust style handling
        try:
            notebook = ttk.Notebook(main_frame, style="Modern.TNotebook")
        except tk.TclError:
            notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Setup tabs
        self._setup_general_tab(notebook)
        self._setup_advanced_tab(notebook)
        self._setup_about_tab(notebook)

        # Button frame
        self._setup_buttons(main_frame)

    def _setup_general_tab(self, notebook):
        """Setup general settings tab"""
        general_frame = ttk.Frame(notebook, padding="15")
        notebook.add(general_frame, text="General")

        # UI Preferences section
        ui_frame = ttk.LabelFrame(general_frame, text="User Interface", padding="10")
        ui_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Checkbutton(
            ui_frame,
            text="Auto-refresh file list after operations",
            variable=self.auto_refresh_var
        ).pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(
            ui_frame,
            text="Confirm destructive operations (delete, etc.)",
            variable=self.confirm_ops_var
        ).pack(anchor=tk.W, pady=2)

        # File Operations section
        file_frame = ttk.LabelFrame(general_frame, text="File Operations", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(file_frame, text="Default download location:").pack(anchor=tk.W, pady=(0, 5))

        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(
            path_frame,
            textvariable=self.download_path_var,
            state=tk.READONLY
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            path_frame,
            text="Browse",
            command=self._browse_download_path
        ).pack(side=tk.RIGHT, padx=(5, 0))

    def _setup_advanced_tab(self, notebook):
        """Setup advanced settings tab"""
        advanced_frame = ttk.Frame(notebook, padding="15")
        notebook.add(advanced_frame, text="Advanced")

        # Authentication section
        auth_frame = ttk.LabelFrame(advanced_frame, text="Authentication", padding="10")
        auth_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(auth_frame, text="Credentials file path:").pack(anchor=tk.W, pady=(0, 5))

        creds_frame = ttk.Frame(auth_frame)
        creds_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(
            creds_frame,
            textvariable=self.creds_path_var
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            creds_frame,
            text="Browse",
            command=self._browse_creds_file
        ).pack(side=tk.RIGHT, padx=(5, 0))

        # Logging section
        log_frame = ttk.LabelFrame(advanced_frame, text="Logging", padding="10")
        log_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(log_frame, text="Log level:").pack(anchor=tk.W, pady=(0, 5))

        log_combo = ttk.Combobox(
            log_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state=tk.READONLY,
            width=15
        )
        log_combo.pack(anchor=tk.W, pady=5)

        # Performance section
        perf_frame = ttk.LabelFrame(advanced_frame, text="Performance", padding="10")
        perf_frame.pack(fill=tk.X)

        ttk.Label(
            perf_frame,
            text="These settings affect upload/download performance.",
            font=('Segoe UI', 8)
        ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(perf_frame, text="Note: Changes require application restart.").pack(anchor=tk.W)

    def _setup_about_tab(self, notebook):
        """Setup about tab"""
        about_frame = ttk.Frame(notebook, padding="15")
        notebook.add(about_frame, text="About")

        # Title
        title_label = ttk.Label(
            about_frame,
            text="Google Drive Sync Manager",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(20, 5))

        version_label = ttk.Label(
            about_frame,
            text="Version 2.1.0",
            font=('Segoe UI', 10)
        )
        version_label.pack(pady=(0, 20))

        # Description
        about_text = """A professional file management application for Google Drive 
with advanced features including:

• Batch file and folder operations
• Progress tracking for long operations  
• Modern, intuitive user interface
• Comprehensive error handling and logging
• Configurable settings and preferences
• Context menus and keyboard shortcuts
• Automatic UI refresh after uploads
• Recursive folder upload support
• Enhanced error handling and user feedback

Built with Python and Tkinter
Licensed under MIT License"""

        text_widget = tk.Text(
            about_frame,
            height=15,
            width=50,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg=about_frame.cget('background'),
            font=('Segoe UI', 9)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, pady=10)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)

    def _setup_buttons(self, parent):
        """Setup dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # Try to use Modern.TButton style with fallbacks
        try:
            ttk.Button(
                button_frame,
                text="Cancel",
                command=self._cancel,
                style="Modern.TButton"
            ).pack(side=tk.RIGHT, padx=(5, 0))

            ttk.Button(
                button_frame,
                text="OK",
                command=self._save_and_close,
                style="Modern.TButton"
            ).pack(side=tk.RIGHT)

            ttk.Button(
                button_frame,
                text="Apply",
                command=self._apply_settings,
                style="Modern.TButton"
            ).pack(side=tk.RIGHT, padx=(0, 5))
        except tk.TclError:
            # Fallback to default button style
            ttk.Button(
                button_frame,
                text="Cancel",
                command=self._cancel
            ).pack(side=tk.RIGHT, padx=(5, 0))

            ttk.Button(
                button_frame,
                text="OK",
                command=self._save_and_close
            ).pack(side=tk.RIGHT)

            ttk.Button(
                button_frame,
                text="Apply",
                command=self._apply_settings
            ).pack(side=tk.RIGHT, padx=(0, 5))

    def _browse_download_path(self):
        """Browse for download directory"""
        path = filedialog.askdirectory(
            title="Select default download folder",
            initialdir=self.download_path_var.get()
        )
        if path:
            self.download_path_var.set(path)

    def _browse_creds_file(self):
        """Browse for credentials file"""
        path = filedialog.askopenfilename(
            title="Select credentials file",
            initialdir=os.path.dirname(self.creds_path_var.get()) or ".",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.creds_path_var.set(path)

    def _apply_settings(self):
        """Apply settings without closing dialog"""
        try:
            updates = {
                'auto_refresh': self.auto_refresh_var.get(),
                'confirm_operations': self.confirm_ops_var.get(),
                'last_download_path': self.download_path_var.get(),
                'credentials_file': self.creds_path_var.get(),
                'log_level': self.log_level_var.get(),
            }

            self.config_manager.update(updates)

            if self.config_manager.save_config():
                messagebox.showinfo("Settings", "Settings applied successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings:\n{str(e)}")

    def _save_and_close(self):
        """Save settings and close dialog"""
        self._apply_settings()
        self.dialog.destroy()

    def _cancel(self):
        """Cancel settings dialog"""
        self.dialog.destroy()


class ConfirmDialog:
    """Simple confirmation dialog"""

    def __init__(self, parent, title: str, message: str,
                 confirm_text: str = "Yes", cancel_text: str = "No"):
        self.parent = parent
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui(message, confirm_text, cancel_text)
        self._center_dialog()

    def _setup_ui(self, message: str, confirm_text: str, cancel_text: str):
        """Setup confirmation dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Message
        ttk.Label(
            main_frame,
            text=message,
            wraplength=300,
            justify=tk.CENTER
        ).pack(pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()

        ttk.Button(
            button_frame,
            text=cancel_text,
            command=self._cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text=confirm_text,
            command=self._confirm
        ).pack(side=tk.RIGHT)

    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _confirm(self):
        """Confirm action"""
        self.result = True
        self.dialog.destroy()

    def _cancel(self):
        """Cancel action"""
        self.result = False
        self.dialog.destroy()

    def show(self) -> bool:
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result