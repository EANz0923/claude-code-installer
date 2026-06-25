"""Reusable progress bar + log output compound widget - Dark Theme."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from gui.styles import (
    COLOR_BG, COLOR_SURFACE, COLOR_LOG_BG, COLOR_LOG_TEXT,
    COLOR_TEXT_SECONDARY, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_PRIMARY, FONT_MONO, FONT_SMALL, FONT_BODY,
)


class ProgressFrame(tk.Frame):
    """Compound widget: status label + progress bar + scrollable log."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG)

        # Status label
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(self, textvariable=self.status_var, font=FONT_SMALL,
                 fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG).pack(fill="x", pady=(0, 4), anchor="w")

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self, variable=self.progress_var, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 6))

        # Detail label
        self.detail_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.detail_var, font=FONT_SMALL,
                 fg=COLOR_TEXT_SECONDARY, bg=COLOR_BG).pack(fill="x", pady=(0, 6), anchor="w")

        # Log output
        log_container = tk.Frame(self, bg=COLOR_LOG_BG, highlightthickness=1,
                                 highlightbackground="#1f2937")
        log_container.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_container, wrap="word", bg=COLOR_LOG_BG,
                                fg=COLOR_LOG_TEXT, font=FONT_MONO,
                                insertbackground=COLOR_LOG_TEXT,
                                relief="flat", borderwidth=0, padx=10, pady=8,
                                state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(log_container, command=self.log_text.yview)
        sb.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=sb.set)

        # Tags
        self.log_text.tag_configure("ts", foreground=COLOR_TEXT_SECONDARY)
        self.log_text.tag_configure("info", foreground=COLOR_LOG_TEXT)
        self.log_text.tag_configure("ok", foreground=COLOR_SUCCESS)
        self.log_text.tag_configure("err", foreground=COLOR_DANGER)
        self.log_text.tag_configure("hl", foreground=COLOR_PRIMARY)

    def set_status(self, text: str):
        self.status_var.set(text)

    def set_progress(self, percent: float, detail: str = ""):
        self.progress_var.set(percent)
        self.detail_var.set(detail)
        if percent < 0:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start(10)
        else:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.stop()

    def append_log(self, message: str, tag: str = "info"):
        self.log_text.configure(state="normal")
        ts = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert("end", ts, "ts")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def reset(self):
        self.set_progress(0, "")
        self.set_status("就绪")
