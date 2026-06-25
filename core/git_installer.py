"""Git detection, download, and silent installation."""

import os
import re
import subprocess
import sys
import tempfile
from typing import Callable, Optional, Tuple

from core.downloader import Downloader, DownloadError, get_downloader
from data.mirrors import GIT_MIRRORS, FALLBACK_GIT_VERSION, FALLBACK_GIT_PATCH


ProgressCallback = Callable[[float, str], None]
LogCallback = Callable[[str], None]


def check_git() -> Tuple[bool, Optional[str]]:
    """Check if Git is installed and return (installed, version).

    Returns (False, None) if not found.
    """
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        if result.returncode == 0:
            # "git version 2.47.0.windows.1"
            version = result.stdout.strip()
            return True, version
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False, None


def fetch_latest_git_version(
    downloader: Downloader,
    on_log: LogCallback | None = None,
) -> Tuple[str, str]:
    """Fetch the latest Git for Windows version from the mirror.

    Returns (version, patch) tuple. Falls back to hardcoded values.
    """
    try:
        # Try to get the latest version from the index page
        url = "https://npmmirror.com/mirrors/git-for-windows/"
        html = downloader.fetch_text(url, on_log)

        # Find all version directories like v2.47.0.windows.1/
        versions = re.findall(r'v(\d+\.\d+\.\d+)\.windows\.(\d+)/', html)
        if versions:
            # Sort by version and patch number
            versions.sort(
                key=lambda v: tuple(int(x) for x in v[0].split(".")) + (int(v[1]),),
                reverse=True,
            )
            version, patch = versions[0]
            downloader._log(on_log, f"检测到最新 Git 版本: v{version}.windows.{patch}")
            return version, patch

    except DownloadError:
        pass

    downloader._log(on_log, f"无法获取最新版本信息，使用备选版本 v{FALLBACK_GIT_VERSION}")
    return FALLBACK_GIT_VERSION, FALLBACK_GIT_PATCH


def install_git(
    downloader: Downloader,
    on_progress: ProgressCallback | None = None,
    on_log: LogCallback | None = None,
) -> str:
    """Download and install Git for Windows silently.

    Returns the version string.
    """
    # Determine latest version
    version, patch = fetch_latest_git_version(downloader, on_log)
    downloader._log(on_log, f"准备安装 Git v{version}.windows.{patch}")

    # Create temp directory for download
    temp_dir = os.path.join(tempfile.gettempdir(), "claude_code_installer")
    os.makedirs(temp_dir, exist_ok=True)

    # Download the installer
    try:
        exe_path = downloader.download_with_mirrors(
            mirrors=GIT_MIRRORS,
            version=version,
            patch=patch,
            dest_dir=temp_dir,
            filename=f"Git-{version}-64-bit.exe",
            on_progress=on_progress,
            on_log=on_log,
        )
    except DownloadError as e:
        raise DownloadError(f"Git 下载失败: {e}") from e

    # Silent install
    downloader._log(on_log, "正在安装 Git (静默安装)...")
    try:
        result = subprocess.run(
            [
                exe_path,
                "/VERYSILENT",
                "/NORESTART",
                "/NOCANCEL",
                "/SP-",
                "/CLOSEAPPLICATIONS",
                "/RESTARTAPPLICATIONS",
                "/SUPPRESSMSGBOXES",
            ],
            capture_output=True,
            text=True,
            timeout=600,  # Git install can take a while
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            downloader._log(on_log, f"Git 安装可能出错，返回码: {result.returncode}")
    except subprocess.TimeoutExpired:
        downloader._log(on_log, "Git 安装超时，请检查是否权限不足")
        raise DownloadError("Git 安装超时，请尝试以管理员身份运行")

    # Refresh PATH
    _refresh_git_path(on_log)

    # Clean up
    try:
        os.remove(exe_path)
    except OSError:
        pass

    # Verify installation
    installed, installed_version = check_git()
    if installed:
        downloader._log(on_log, f"Git 安装成功: {installed_version}")
        return installed_version
    else:
        downloader._log(on_log, "警告: Git 安装后未检测到。可能需要重启终端或手动添加到 PATH。")
        return f"git version {version}.windows.{patch}"


def _refresh_git_path(on_log: LogCallback | None = None):
    """Add Git installation paths to os.environ PATH."""
    if sys.platform != "win32":
        return

    common_git_paths = [
        r"C:\Program Files\Git\cmd",
        r"C:\Program Files\Git\bin",
        r"C:\Program Files (x86)\Git\cmd",
        r"C:\Program Files (x86)\Git\bin",
    ]

    existing = os.environ.get("PATH", "")
    for p in common_git_paths:
        if os.path.exists(p) and p not in existing:
            existing = f"{existing};{p}"

    os.environ["PATH"] = existing
    if on_log:
        on_log("已添加 Git 路径到 PATH")
