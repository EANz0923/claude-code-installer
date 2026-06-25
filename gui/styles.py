"""GUI styles, colors, and font configuration."""

import tkinter as tk
from tkinter import ttk

# Color scheme
COLOR_BG = "#f0f2f5"
COLOR_SURFACE = "#ffffff"
COLOR_PRIMARY = "#2563eb"
COLOR_PRIMARY_HOVER = "#1d4ed8"
COLOR_SUCCESS = "#16a34a"
COLOR_DANGER = "#dc2626"
COLOR_WARNING = "#f59e0b"
COLOR_TEXT = "#1e293b"
COLOR_TEXT_SECONDARY = "#64748b"
COLOR_BORDER = "#e2e8f0"
COLOR_LOG_BG = "#1e293b"
COLOR_LOG_TEXT = "#e2e8f0"
COLOR_LOG_INFO = "#94a3b8"
COLOR_LOG_SUCCESS = "#4ade80"
COLOR_LOG_ERROR = "#f87171"

# Fonts
FONT_FAMILY = "Microsoft YaHei UI"
FONT_FAMILY_MONO = "Consolas"

FONT_TITLE = (FONT_FAMILY, 14, "bold")
FONT_HEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_MONO = (FONT_FAMILY_MONO, 9)
FONT_BUTTON = (FONT_FAMILY, 10, "bold")
FONT_STATUS = (FONT_FAMILY, 9)


def setup_styles():
    """Configure ttk styles for the application."""
    style = ttk.Style()

    # Try to use a modern theme if available
    available = style.theme_names()
    for theme in ("vista", "clam", "alt"):
        if theme in available:
            style.theme_use(theme)
            break

    # Frame styles
    style.configure("Surface.TFrame", background=COLOR_SURFACE)
    style.configure("Card.TFrame", background=COLOR_SURFACE, relief="solid", borderwidth=1)
    style.configure("Main.TFrame", background=COLOR_BG)

    # Label styles
    style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLOR_TEXT, background=COLOR_BG)
    style.configure("Heading.TLabel", font=FONT_HEADING, foreground=COLOR_TEXT, background=COLOR_SURFACE)
    style.configure("Body.TLabel", font=FONT_BODY, foreground=COLOR_TEXT, background=COLOR_SURFACE)
    style.configure("Small.TLabel", font=FONT_SMALL, foreground=COLOR_TEXT_SECONDARY, background=COLOR_SURFACE)
    style.configure("Success.TLabel", font=FONT_BODY, foreground=COLOR_SUCCESS, background=COLOR_SURFACE)
    style.configure("Danger.TLabel", font=FONT_BODY, foreground=COLOR_DANGER, background=COLOR_SURFACE)

    # Button styles
    style.configure(
        "Primary.TButton",
        font=FONT_BUTTON,
        background=COLOR_PRIMARY,
        foreground="white",
        padding=(20, 8),
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("disabled", "#94a3b8")],
    )

    style.configure(
        "Secondary.TButton",
        font=FONT_BODY,
        padding=(16, 6),
    )

    style.configure(
        "Small.TButton",
        font=FONT_SMALL,
        padding=(8, 4),
    )

    # Progress bar
    style.configure(
        "TProgressbar",
        thickness=12,
        troughcolor=COLOR_BORDER,
        background=COLOR_PRIMARY,
    )

    # Notebook (tabs)
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        font=FONT_HEADING,
        padding=(24, 10),
        background=COLOR_BG,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLOR_SURFACE)],
        foreground=[("selected", COLOR_PRIMARY)],
    )

    # Separator
    style.configure("TSeparator", background=COLOR_BORDER)

    # Labelframe
    style.configure("Card.TLabelframe", background=COLOR_SURFACE, borderwidth=1, relief="solid")
    style.configure("Card.TLabelframe.Label", font=FONT_HEADING, foreground=COLOR_TEXT, background=COLOR_SURFACE)

    return style
