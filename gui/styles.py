"""GUI styles - Modern Dark Theme."""

import tkinter as tk
from tkinter import ttk

# ── Color Palette ──────────────────────────────────────
COLOR_BG = "#0d1117"
COLOR_SURFACE = "#161b22"
COLOR_SURFACE_HOVER = "#1c2333"
COLOR_BORDER = "#30363d"
COLOR_TEXT = "#e6edf3"
COLOR_TEXT_SECONDARY = "#8b949e"
COLOR_TEXT_MUTED = "#6e7681"

COLOR_PRIMARY = "#6366f1"
COLOR_PRIMARY_HOVER = "#818cf8"
COLOR_PRIMARY_ACTIVE = "#4f46e5"

COLOR_SUCCESS = "#22c55e"
COLOR_DANGER = "#ef4444"
COLOR_WARNING = "#f59e0b"

COLOR_LOG_BG = "#0b1017"
COLOR_LOG_TEXT = "#a8b0c0"

COLOR_INPUT_BG = "#1c2128"
COLOR_INPUT_BORDER = "#30363d"

# ── Fonts ──────────────────────────────────────────────
FONT_FAMILY = "Microsoft YaHei UI"
FONT_FAMILY_MONO = "Consolas"

FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_MONO = (FONT_FAMILY_MONO, 9)
FONT_BUTTON = (FONT_FAMILY, 10, "bold")


def btn(parent, text, command=None, style="primary", state="normal", **kw):
    """Create a styled tk.Button. External padx/pady override defaults."""
    if style == "primary":
        bg, fg, hov = COLOR_PRIMARY, "#ffffff", COLOR_PRIMARY_HOVER
    elif style == "danger":
        bg, fg, hov = COLOR_DANGER, "#ffffff", "#f87171"
    else:
        bg, fg, hov = COLOR_SURFACE_HOVER, COLOR_TEXT, COLOR_BORDER

    font = kw.pop("font", FONT_BUTTON)
    padx = kw.pop("padx", 18)
    pady = kw.pop("pady", 8)

    return tk.Button(parent, text=text, font=font,
                     fg=fg, bg=bg, activeforeground=fg, activebackground=hov,
                     disabledforeground=COLOR_TEXT_MUTED,
                     relief="flat", borderwidth=0, padx=padx, pady=pady,
                     cursor="hand2", state=state, command=command,
                     highlightthickness=0, **kw)


def lbl(parent, text="", font=FONT_BODY, fg=COLOR_TEXT, bg=None, **kw):
    """Create a styled tk.Label."""
    return tk.Label(parent, text=text, font=font, fg=fg,
                    bg=bg if bg is not None else COLOR_SURFACE, **kw)


def entry(parent, textvariable=None, show="", width=32, font=FONT_BODY):
    """Create a styled tk.Entry."""
    return tk.Entry(parent, textvariable=textvariable, show=show, font=font,
                    width=width, fg=COLOR_TEXT, bg=COLOR_INPUT_BG,
                    insertbackground=COLOR_TEXT, relief="flat",
                    highlightthickness=1, highlightbackground=COLOR_INPUT_BORDER,
                    highlightcolor=COLOR_PRIMARY, borderwidth=0)


def card(parent, **kw):
    """Create a dark surface frame."""
    return tk.Frame(parent, bg=COLOR_SURFACE, **kw)


def dot(parent, color="#6e7681", size=10):
    """Create a status dot canvas."""
    c = tk.Canvas(parent, width=size+4, height=size+4,
                  bg=COLOR_SURFACE, highlightthickness=0)
    d = c.create_oval(2, 2, size+2, size+2, fill=color, outline="")
    return c, d


def setup_styles():
    """Configure ttk styles for Notebook and Combobox."""
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_BODY)
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Main.TFrame", background=COLOR_BG)
    style.configure("Surface.TFrame", background=COLOR_SURFACE)
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_BODY)

    # Notebook — fixed tab size to prevent jumping when switching
    TAB_PAD_X = 32
    TAB_PAD_Y = 10
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure("TNotebook.Tab", font=FONT_BUTTON,
                    padding=[TAB_PAD_X, TAB_PAD_Y, TAB_PAD_X, TAB_PAD_Y],
                    background=COLOR_BG, foreground=COLOR_TEXT_SECONDARY, borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", COLOR_SURFACE), ("active", COLOR_SURFACE_HOVER)],
              foreground=[("selected", COLOR_PRIMARY)],
              padding=[("selected", [TAB_PAD_X, TAB_PAD_Y, TAB_PAD_X, TAB_PAD_Y]),
                       ("active", [TAB_PAD_X, TAB_PAD_Y, TAB_PAD_X, TAB_PAD_Y])])

    # Labelframe
    style.configure("Card.TLabelframe", background=COLOR_SURFACE, borderwidth=0, relief="flat")
    style.configure("Card.TLabelframe.Label", font=FONT_HEADING, foreground=COLOR_TEXT,
                    background=COLOR_SURFACE)

    # Progress bar
    style.configure("TProgressbar", thickness=10, troughcolor=COLOR_BG,
                    background=COLOR_PRIMARY, borderwidth=0)

    return style
