"""Claude Code CLI Installer - Entry point (no console).

A GUI application for installing Claude Code CLI and dependencies
on Windows in China's network environment.
"""

import sys
import os
import traceback
import tkinter as tk
from tkinter import messagebox

# Add project root to path for PyInstaller compatibility
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _show_error(title: str, message: str):
    """Show an error dialog even before the main App is created."""
    try:
        root = tk.Tk()
        root.withdraw()  # hide the empty window
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        pass


def _global_excepthook(exc_type, exc_value, exc_tb):
    """Catch all unhandled exceptions and show a Chinese error dialog."""
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    tb_text = "".join(tb_lines)
    _show_error("程序错误", f"发生未处理的异常:\n\n{tb_text}")


def _global_thread_excepthook(args):
    """Catch exceptions from background threads."""
    tb_text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    _show_error("后台任务错误", f"后台线程发生异常:\n\n{tb_text}")


# Install global exception handlers
sys.excepthook = _global_excepthook
if hasattr(sys, "unraisablehook"):
    sys.unraisablehook = _global_excepthook
import threading
threading.excepthook = _global_thread_excepthook


def main():
    """Application entry point."""
    from gui.app import App
    app = App()
    app.run()


if __name__ == "__main__":
    main()
