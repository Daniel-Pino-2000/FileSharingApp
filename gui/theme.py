"""
Theme management for Google Drive Sync Manager

Handles UI theming and styling configuration.
"""

from tkinter import ttk


class ModernTheme:
    """Modern theme configuration"""

    COLORS = {
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'success': '#27ae60',
        'danger': '#e74c3c',
        'warning': '#f39c12',
        'info': '#17a2b8',
        'light': '#ecf0f1',
        'dark': '#34495e',
        'white': '#ffffff',
        'gray': '#7f8c8d',
        'light_gray': '#f8f9fa',
        'border': '#dee2e6'
    }

    FONTS = {
        'default': ('Segoe UI', 9),
        'heading': ('Segoe UI', 10, 'bold'),
        'button': ('Segoe UI', 9),
        'status': ('Segoe UI', 8),
        'tree': ('Segoe UI', 9)
    }

    @classmethod
    def configure_ttk_style(cls):
        """Configure ttk styles for modern look"""
        style = ttk.Style()

        # Use native theme as base
        try:
            style.theme_use('clam')  # Cross-platform theme
        except:
            pass

        # Configure Treeview
        style.configure(
            "Modern.Treeview",
            background=cls.COLORS['white'],
            foreground=cls.COLORS['primary'],
            rowheight=25,
            fieldbackground=cls.COLORS['white'],
            font=cls.FONTS['tree']
        )

        style.configure(
            "Modern.Treeview.Heading",
            background=cls.COLORS['primary'],
            foreground=cls.COLORS['white'],
            font=cls.FONTS['heading'],
            relief='flat'
        )

        style.map(
            "Modern.Treeview.Heading",
            background=[('active', cls.COLORS['dark'])]
        )

        # Configure buttons
        style.configure(
            "Modern.TButton",
            padding=(10, 5),
            font=cls.FONTS['button'],
            borderwidth=1,
            focuscolor='none'
        )

        style.map(
            "Modern.TButton",
            background=[('active', cls.COLORS['light'])],
            relief=[('pressed', 'flat'), ('!pressed', 'raised')]
        )

        # Success button
        style.configure(
            "Success.TButton",
            padding=(10, 5),
            font=cls.FONTS['button']
        )

        # Danger button
        style.configure(
            "Danger.TButton",
            padding=(10, 5),
            font=cls.FONTS['button']
        )

        # Configure frames
        style.configure(
            "Modern.TFrame",
            background=cls.COLORS['light_gray']
        )

        # Configure labels
        style.configure(
            "Modern.TLabel",
            background=cls.COLORS['light_gray'],
            foreground=cls.COLORS['primary'],
            font=cls.FONTS['default']
        )

        style.configure(
            "Heading.TLabel",
            background=cls.COLORS['light_gray'],
            foreground=cls.COLORS['primary'],
            font=cls.FONTS['heading']
        )

        # Configure progress bar
        style.configure(
            "Modern.TProgressbar",
            background=cls.COLORS['secondary'],
            troughcolor=cls.COLORS['light'],
            borderwidth=0,
            lightcolor=cls.COLORS['secondary'],
            darkcolor=cls.COLORS['secondary']
        )

        # Configure notebook
        style.configure(
            "Modern.TNotebook",
            background=cls.COLORS['light_gray'],
            borderwidth=0
        )

        style.configure(
            "Modern.TNotebook.Tab",
            padding=(12, 8),
            font=cls.FONTS['default']
        )

        return style

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Get color value by name"""
        return cls.COLORS.get(color_name, cls.COLORS['primary'])

    @classmethod
    def get_font(cls, font_name: str) -> tuple:
        """Get font configuration by name"""
        return cls.FONTS.get(font_name, cls.FONTS['default'])