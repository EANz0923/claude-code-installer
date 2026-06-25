"""Installation orchestrator that coordinates all installation steps."""

import threading
from typing import Callable, Optional

from core.downloader import Downloader, DownloadError, get_downloader
from core.node_installer import check_nodejs, install_nodejs, check_npm
from core.git_installer import check_git, install_git
from core.claude_code_installer import (
    check_claude_code,
    configure_npm_mirror,
    install_claude_code,
)


# Callback types
ProgressCallback = Callable[[float, str], None]
LogCallback = Callable[[str], None]
StepCallback = Callable[[str, bool, str], None]  # step_name, success, detail


class InstallStatus:
    """Status of a single installation component."""

    def __init__(self):
        self.installed = False
        self.version: Optional[str] = None
        self.in_progress = False
        self.error: Optional[str] = None

    @property
    def status_text(self) -> str:
        if self.error:
            return f"错误: {self.error}"
        if self.in_progress:
            return "安装中..."
        if self.installed:
            return f"已安装 ({self.version})"
        return "未安装"


class SystemStatus:
    """Tracks the status of all components."""

    def __init__(self):
        self.node = InstallStatus()
        self.git = InstallStatus()
        self.claude = InstallStatus()
        self.npm_mirror_configured = False


class Installer:
    """Orchestrates the full installation process."""

    def __init__(self):
        self.downloader = get_downloader()
        self.status = SystemStatus()

    def refresh_status(self, on_log: LogCallback | None = None):
        """Check and refresh the status of all installed components."""
        # Node.js
        node_ok, node_ver = check_nodejs()
        self.status.node.installed = node_ok
        self.status.node.version = node_ver
        self.status.node.error = None
        if on_log:
            if node_ok:
                on_log(f"Node.js: 已安装 (v{node_ver})")
            else:
                on_log("Node.js: 未安装")

        # npm
        npm_ok, npm_ver = check_npm()
        if on_log:
            if npm_ok:
                on_log(f"npm: 已安装 (v{npm_ver})")
            else:
                on_log("npm: 未安装")

        # Git
        git_ok, git_ver = check_git()
        self.status.git.installed = git_ok
        self.status.git.version = git_ver
        self.status.git.error = None
        if on_log:
            if git_ok:
                on_log(f"Git: 已安装 ({git_ver})")
            else:
                on_log("Git: 未安装")

        # Claude Code CLI
        claude_ok, claude_ver = check_claude_code()
        self.status.claude.installed = claude_ok
        self.status.claude.version = claude_ver
        self.status.claude.error = None
        if on_log:
            if claude_ok:
                on_log(f"Claude Code CLI: 已安装 ({claude_ver})")
            else:
                on_log("Claude Code CLI: 未安装")

    def run_dependency_install(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        on_step: StepCallback | None = None,
    ) -> bool:
        """Install missing dependencies (Node.js, Git).

        Returns True if all dependencies are installed.
        """
        success = True

        # Step 1: Install Node.js if missing
        if not self.status.node.installed:
            self.status.node.in_progress = True
            if on_step:
                on_step("Node.js", False, "安装中...")
            try:
                version = install_nodejs(
                    self.downloader,
                    on_progress=on_progress,
                    on_log=on_log,
                )
                self.status.node.installed = True
                self.status.node.version = version
                self.status.node.in_progress = False
                if on_step:
                    on_step("Node.js", True, f"v{version}")
            except DownloadError as e:
                self.status.node.in_progress = False
                self.status.node.error = str(e)
                if on_step:
                    on_step("Node.js", False, str(e))
                if on_log:
                    on_log(f"Node.js 安装失败: {e}")
                success = False

        # Step 2: Install Git if missing
        if not self.status.git.installed:
            self.status.git.in_progress = True
            if on_step:
                on_step("Git", False, "安装中...")
            try:
                version = install_git(
                    self.downloader,
                    on_progress=on_progress,
                    on_log=on_log,
                )
                self.status.git.installed = True
                self.status.git.version = version
                self.status.git.in_progress = False
                if on_step:
                    on_step("Git", True, version)
            except DownloadError as e:
                self.status.git.in_progress = False
                self.status.git.error = str(e)
                if on_step:
                    on_step("Git", False, str(e))
                if on_log:
                    on_log(f"Git 安装失败: {e}")
                # Git failure is not critical for Claude Code
                # Just warn, don't mark overall as failure

        # Step 3: Configure npm mirror
        if on_log:
            on_log("")
        npm_ok = configure_npm_mirror(on_log)
        self.status.npm_mirror_configured = npm_ok

        return success

    def run_claude_code_install(
        self,
        on_log: LogCallback | None = None,
        on_step: StepCallback | None = None,
    ) -> bool:
        """Install Claude Code CLI via npm.

        Returns True if successful.
        """
        self.status.claude.in_progress = True
        if on_step:
            on_step("Claude Code CLI", False, "安装中...")

        ok = install_claude_code(on_log)
        self.status.claude.in_progress = False

        if ok:
            # Verify
            claude_ok, claude_ver = check_claude_code()
            self.status.claude.installed = claude_ok
            self.status.claude.version = claude_ver
            if on_step:
                on_step("Claude Code CLI", claude_ok, claude_ver or "")
        else:
            self.status.claude.error = "安装失败"
            if on_step:
                on_step("Claude Code CLI", False, "安装失败")

        return ok

    def run_full_install(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        on_step: StepCallback | None = None,
    ) -> bool:
        """Run the complete installation: deps + Claude Code CLI.

        Returns True if everything is installed.
        """
        # First check current status
        if on_log:
            on_log("=== 检测系统环境 ===")
        self.refresh_status(on_log)

        # Install missing dependencies
        if on_log:
            on_log("")
            on_log("=== 安装依赖 ===")
        deps_ok = self.run_dependency_install(
            on_progress=on_progress,
            on_log=on_log,
            on_step=on_step,
        )

        if not deps_ok:
            if on_log:
                on_log("")
                on_log("依赖安装未完全成功，请检查上述错误。")
            return False

        # Install Claude Code CLI
        if on_log:
            on_log("")
            on_log("=== 安装 Claude Code CLI ===")

        claude_ok = self.run_claude_code_install(
            on_log=on_log,
            on_step=on_step,
        )

        if on_log:
            on_log("")
            if claude_ok:
                on_log("=== 安装完成! ===")
                on_log("在命令行中运行 'claude' 即可开始使用。")
            else:
                on_log("=== Claude Code CLI 安装失败 ===")
                on_log("请检查上述错误信息并重试。")

        return claude_ok


class InstallerThread(threading.Thread):
    """Runs the installer in a background thread, marshalling GUI updates."""

    def __init__(
        self,
        root,  # tkinter.Tk
        installer: Installer,
        mode: str,  # "full" or "claude_only"
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        on_step: StepCallback | None = None,
        on_done: Callable[[bool], None] | None = None,
    ):
        super().__init__(daemon=True)
        self.root = root
        self.installer = installer
        self.mode = mode
        self._on_progress = on_progress
        self._on_log = on_log
        self._on_step = on_step
        self._on_done = on_done

    def run(self):
        try:
            if self.mode == "full":
                result = self.installer.run_full_install(
                    on_progress=self._safe_progress,
                    on_log=self._safe_log,
                    on_step=self._safe_step,
                )
            else:
                result = self.installer.run_claude_code_install(
                    on_log=self._safe_log,
                    on_step=self._safe_step,
                )

            if self._on_done:
                self.root.after(0, self._on_done, result)

        except Exception as e:
            self._safe_log(f"严重错误: {e}")
            if self._on_done:
                self.root.after(0, self._on_done, False)

    def _safe_progress(self, percent: float, message: str):
        """Marshal progress update to the main thread."""
        if self._on_progress:
            self.root.after(0, self._on_progress, percent, message)

    def _safe_log(self, message: str):
        """Marshal log message to the main thread."""
        if self._on_log:
            self.root.after(0, self._on_log, message)

    def _safe_step(self, step_name: str, success: bool, detail: str):
        """Marshal step completion to the main thread."""
        if self._on_step:
            self.root.after(0, self._on_step, step_name, success, detail)


# Singleton
_default_installer: Installer | None = None


def get_installer() -> Installer:
    """Get or create the default installer instance."""
    global _default_installer
    if _default_installer is None:
        _default_installer = Installer()
    return _default_installer
