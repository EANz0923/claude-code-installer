"""Node.js detection, download, and silent installation."""

import os
import re
import subprocess
import sys
import tempfile
from typing import Callable, Optional, Tuple

from core.downloader import Downloader, DownloadError, get_downloader
from data.mirrors import NODE_MIRRORS, FALLBACK_NODE_VERSION


ProgressCallback = Callable[[float, str], None]
LogCallback = Callable[[str], None]


def check_nodejs() -> Tuple[bool, Optional[str]]:
    """Check if Node.js is installed and return (installed, version).

    Returns (False, None) if not found.
    """
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        if result.returncode == 0:
            version = result.stdout.strip().lstrip("v")
            return True, version
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False, None


def check_npm() -> Tuple[bool, Optional[str]]:
    """Check if npm is installed and return (installed, version)."""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False, None


def fetch_latest_node_version(
    downloader: Downloader,
    on_log: LogCallback | None = None,
) -> str:
    """Fetch the latest Node.js LTS version from the mirror.

    Falls back to FALLBACK_NODE_VERSION if parsing fails.
    """
    try:
        # Try to get the latest version from the index page
        url = "https://npmmirror.com/mirrors/node/latest-v22.x/"
        html = downloader.fetch_text(url, on_log)

        # Parse version from links like href="node-v22.20.0-x64.msi"
        match = re.search(r'node-v(\d+\.\d+\.\d+)-x64\.msi', html)
        if match:
            version = match.group(1)
            downloader._log(on_log, f"检测到最新 Node.js 版本: v{version}")
            return version

        # Try latest/ directory
        url = "https://npmmirror.com/mirrors/node/latest/"
        html = downloader.fetch_text(url, on_log)
        match = re.search(r'node-v(\d+\.\d+\.\d+)-x64\.msi', html)
        if match:
            version = match.group(1)
            downloader._log(on_log, f"检测到最新 Node.js 版本: v{version}")
            return version

    except DownloadError:
        downloader._log(on_log, f"无法获取最新版本信息，使用备选版本 v{FALLBACK_NODE_VERSION}")

    return FALLBACK_NODE_VERSION


def install_nodejs(
    downloader: Downloader,
    on_progress: ProgressCallback | None = None,
    on_log: LogCallback | None = None,
) -> str:
    """Download and install Node.js silently.

    Returns the installed version string.
    """
    # Determine latest version
    version = fetch_latest_node_version(downloader, on_log)
    downloader._log(on_log, f"准备安装 Node.js v{version}")

    # Create temp directory for download
    temp_dir = os.path.join(tempfile.gettempdir(), "claude_code_installer")
    os.makedirs(temp_dir, exist_ok=True)

    # Download the MSI
    try:
        msi_path = downloader.download_with_mirrors(
            mirrors=NODE_MIRRORS,
            version=version,
            dest_dir=temp_dir,
            filename=f"node-v{version}-x64.msi",
            on_progress=on_progress,
            on_log=on_log,
        )
    except DownloadError as e:
        raise DownloadError(f"Node.js 下载失败: {e}") from e

    # Silent install via msiexec
    downloader._log(on_log, "正在安装 Node.js (静默安装)...")
    try:
        result = subprocess.run(
            ["msiexec", "/i", msi_path, "/quiet", "/norestart"],
            capture_output=True,
            text=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else f"msiexec 返回码: {result.returncode}"
            downloader._log(on_log, f"安装可能出错: {error_msg}")
    except subprocess.TimeoutExpired:
        downloader._log(on_log, "安装超时，请检查是否权限不足")
        raise DownloadError("Node.js 安装超时，请尝试以管理员身份运行")
    except FileNotFoundError:
        downloader._log(on_log, "找不到 msiexec，正在尝试手动安装...")
        # Fallback: just run the MSI directly
        try:
            subprocess.run(
                ["start", "/wait", msi_path],
                shell=True,
                timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            raise DownloadError("无法运行 Node.js 安装程序")

    # Refresh PATH by reading from registry
    _refresh_path(on_log)

    # Clean up
    try:
        os.remove(msi_path)
    except OSError:
        pass

    # Verify installation
    installed, installed_version = check_nodejs()
    if installed:
        downloader._log(on_log, f"Node.js 安装成功: v{installed_version}")
        return installed_version
    else:
        downloader._log(on_log, "警告: Node.js 安装后未检测到。可能需要重启终端或手动添加到 PATH。")
        return version  # Return expected version even if verification fails


def _refresh_path(on_log: LogCallback | None = None):
    """Refresh os.environ PATH by reading from Windows registry."""
    if sys.platform != "win32":
        return

    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        )
        path, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)

        # Also try user PATH
        try:
            user_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
            user_path, _ = winreg.QueryValueEx(user_key, "Path")
            winreg.CloseKey(user_key)
            new_path = f"{path};{user_path}"
        except OSError:
            new_path = path

        os.environ["PATH"] = new_path
        if on_log:
            on_log("已刷新系统 PATH 环境变量")

    except OSError:
        # Add common Node.js install paths
        common_paths = [
            r"C:\Program Files\nodejs",
            r"C:\Program Files (x86)\nodejs",
        ]
        existing = os.environ.get("PATH", "")
        for p in common_paths:
            if p not in existing:
                existing = f"{existing};{p}"
        os.environ["PATH"] = existing
        if on_log:
            on_log("已添加 Node.js 默认安装路径到 PATH")
