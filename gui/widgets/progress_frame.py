"""Reusable progress bar + log output compound widget."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from gui.styles import (
    COLOR_LOG_BG,
    COLOR_LOG_TEXT,
    COLOR_LOG_INFO,
    COLOR_LOG_SUCCESS,
    COLOR_LOG_ERROR,
    FONT_MONO,
    FONT_SMALL,
)


class ProgressFrame(ttk.Frame):
    """Compound widget: status label + progress bar + scrollable log."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Status label
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            font=FONT_SMALL,
            foreground=COLOR_LOG_INFO,
        )
        self.status_label.pack(fill="x", pady=(0, 4))

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            mode="determinate",
            style="TProgressbar",
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))

        # Progress detail label
        self.detail_var = tk.StringVar(value="")
        self.detail_label = ttk.Label(
            self,
            textvariable=self.detail_var,
            font=FONT_SMALL,
            foreground=COLOR_LOG_INFO,
        )
        self.detail_label.pack(fill="x", pady=(0, 4))

        # Log output
        log_frame = tk.Frame(self, bg=COLOR_LOG_BG, bd=1, relief="sunken")
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            log_frame,
            wrap="word",
            bg=COLOR_LOG_BG,
            fg=COLOR_LOG_TEXT,
            font=FONT_MONO,
            insertbackground=COLOR_LOG_TEXT,
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=6,
            state="disabled",
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Log tags for colored text
        self.log_text.tag_configure("info", foreground=COLOR_LOG_INFO)
        self.log_text.tag_configure("success", foreground=COLOR_LOG_SUCCESS)
        self.log_text.tag_configure("error", foreground=COLOR_LOG_ERROR)
        self.log_text.tag_configure("timestamp", foreground=COLOR_LOG_INFO)

    def set_status(self, text: str):
        """Update the status label."""
        self.status_var.set(text)

    def set_progress(self, percent: float, detail: str = ""):
        """Update the progress bar and detail text.

        percent: 0-100
        detail: text shown below the progress bar
        """
        self.progress_var.set(percent)
        self.detail_var.set(detail)
        # Switch to indeterminate if percent is negative
        if percent < 0:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start(10)
        else:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.stop()

    def append_log(self, message: str, tag: str = "info"):
        """Append a line to the log output."""
        self.log_text.configure(state="normal")

        # Add timestamp
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert("end", timestamp, "timestamp")

        # Add message with tag
        self.log_text.insert("end", message + "\n", tag)

        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self):
        """Clear all log output."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def reset(self):
        """Reset progress bar and status."""
        self.set_progress(0, "")
        self.set_status("就绪")
