"""Claude Code CLI Installer - Entry point.

A GUI application for installing Claude Code CLI and dependencies
on Windows in China's network environment.
"""

import sys
import os

# Add project root to path for PyInstaller compatibility
if getattr(sys, "frozen", False):
    # Running as compiled .exe
    os.chdir(os.path.dirname(sys.executable))

# Ensure the project root is importable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Application entry point."""
    from gui.app import App

    app = App()
    app.run()


if __name__ == "__main__":
    main()
