"""Main application window with tabbed interface - Dark Theme."""

import tkinter as tk
from tkinter import ttk

from gui.styles import (
    setup_styles, COLOR_BG, COLOR_TEXT, COLOR_TEXT_SECONDARY,
    COLOR_PRIMARY, FONT_TITLE, FONT_SMALL, lbl,
)
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
        self.root.title("Claude Code CLI Installer")
        self.root.geometry("920x680")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLOR_BG)

        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

        try:
            self.root.iconbitmap(default="resources/icon.ico")
        except Exception:
            pass

    def _setup_styles(self):
        self.style = setup_styles()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLOR_BG)
        header.pack(fill="x", padx=20, pady=(18, 4))

        title = tk.Label(header, text="Claude Code CLI Installer",
                         font=FONT_TITLE, fg=COLOR_TEXT, bg=COLOR_BG)
        title.pack(side="left")

        sub = tk.Label(header, text="一键安装 · 国内镜像加速 · 模型配置",
                       font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG)
        sub.pack(side="left", padx=(14, 0), pady=(6, 0))

        # Divider
        div = tk.Frame(self.root, bg="#21262d", height=1)
        div.pack(fill="x", padx=20)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=12)

        self.install_tab = InstallTab(self.notebook)
        self.notebook.add(self.install_tab, text="   安装   ")

        self.model_config_tab = ModelConfigTab(self.notebook)
        self.notebook.add(self.model_config_tab, text="  模型配置  ")

        # Status bar
        sb = tk.Frame(self.root, bg=COLOR_BG)
        sb.pack(fill="x", padx=20, pady=(0, 10))

        lbl(sb, "适配国内网络环境 · npmmirror.com / mirrors.huaweicloud.com",
            font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG).pack(side="left")
        lbl(sb, "v1.0.0", font=FONT_SMALL, fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG).pack(side="right")

    def run(self):
        self.root.mainloop()
