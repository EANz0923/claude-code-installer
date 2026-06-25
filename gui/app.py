"""Main application window with tabbed interface."""

import tkinter as tk
from tkinter import ttk

from gui.styles import setup_styles, COLOR_BG, FONT_SMALL, COLOR_TEXT_SECONDARY
from gui.widgets.install_tab import InstallTab
from gui.widgets.model_config_tab import ModelConfigTab


class App:
    """Main application window."""

    def __init__(self):
        self.root = tk.Tk()
        self._setup_window()
        self._setup_styles()
        self._build_ui()

    def _setup_window(self):
        """Configure the main window."""
        self.root.title("Claude Code CLI Installer")
        self.root.geometry("920x680")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLOR_BG)

        # Center on screen
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

        # Try to set icon
        try:
            self.root.iconbitmap(default="resources/icon.ico")
        except Exception:
            pass  # icon not critical

    def _setup_styles(self):
        """Initialize ttk styles."""
        self.style = setup_styles()

    def _build_ui(self):
        """Build the main UI."""
        # Header
        header = ttk.Frame(self.root, style="Main.TFrame")
        header.pack(fill="x", padx=16, pady=(16, 0))

        title = ttk.Label(
            header,
            text="Claude Code CLI Installer",
            style="Title.TLabel",
        )
        title.pack(side="left")

        subtitle = ttk.Label(
            header,
            text="一键安装 · 国内镜像加速 · 模型配置",
            font=FONT_SMALL,
            foreground=COLOR_TEXT_SECONDARY,
            background=COLOR_BG,
        )
        subtitle.pack(side="left", padx=(12, 0), pady=(4, 0))

        # Notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)

        # Install tab
        self.install_tab = InstallTab(self.notebook)
        self.notebook.add(self.install_tab, text="  安装  ")

        # Model config tab
        self.model_config_tab = ModelConfigTab(self.notebook)
        self.notebook.add(self.model_config_tab, text="  模型配置  ")

        # Status bar
        status_bar = ttk.Frame(self.root, style="Main.TFrame")
        status_bar.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Label(
            status_bar,
            text="适配国内网络环境 · 镜像源: npmmirror.com / mirrors.huaweicloud.com",
            font=FONT_SMALL,
            foreground=COLOR_TEXT_SECONDARY,
            background=COLOR_BG,
        ).pack(side="left")

        ttk.Label(
            status_bar,
            text="v1.0.0",
            font=FONT_SMALL,
            foreground=COLOR_TEXT_SECONDARY,
            background=COLOR_BG,
        ).pack(side="right")

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
