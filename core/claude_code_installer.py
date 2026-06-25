"""Install Claude Code CLI via npm."""

import subprocess
import sys
from typing import Callable, Optional

LogCallback = Callable[[str], None]


def check_claude_code() -> tuple[bool, str | None]:
    """Check if Claude Code CLI is installed.

    Returns (installed, version_string_or_None).
    """
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        if result.returncode == 0:
            version = result.stdout.strip() or "installed"
            return True, version
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False, None


def configure_npm_mirror(on_log: LogCallback | None = None) -> bool:
    """Configure npm to use the Chinese mirror registry.

    Returns True if successful.
    """
    mirror_url = "https://registry.npmmirror.com"

    if on_log:
        on_log(f"配置 npm 镜像源: {mirror_url}")

    try:
        result = subprocess.run(
            ["npm", "config", "set", "registry", mirror_url],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        if result.returncode != 0:
            if on_log:
                on_log(f"npm config 警告: {result.stderr.strip()}")
            return False

        if on_log:
            on_log("npm 镜像源配置成功")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        if on_log:
            on_log(f"配置 npm 镜像源失败: {e}")
        return False


def install_claude_code(on_log: LogCallback | None = None) -> bool:
    """Install Claude Code CLI via npm globally.

    Returns True if successful.
    """
    if on_log:
        on_log("开始安装 Claude Code CLI...")
        on_log("运行: npm install -g @anthropic-ai/claude-code")

    try:
        process = subprocess.Popen(
            ["npm", "install", "-g", "@anthropic-ai/claude-code"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        for line in process.stdout:
            stripped = line.rstrip()
            if stripped:
                if on_log:
                    on_log(stripped)

        process.wait()

        if process.returncode == 0:
            if on_log:
                on_log("Claude Code CLI 安装成功!")
            return True
        else:
            if on_log:
                on_log(f"安装失败，npm 返回码: {process.returncode}")
            return False

    except FileNotFoundError:
        if on_log:
            on_log("错误: 找不到 npm 命令。请确保 Node.js 已正确安装。")
        return False
    except Exception as e:
        if on_log:
            on_log(f"安装出错: {e}")
        return False
