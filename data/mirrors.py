"""Mirror URLs for downloading tools in China network environment."""

from dataclasses import dataclass, field
from typing import List

# npm registry mirrors (used for npm install)
NPM_REGISTRY_MIRRORS = [
    {
        "name": "npmmirror (阿里云)",
        "url": "https://registry.npmmirror.com",
    },
    {
        "name": "华为云",
        "url": "https://mirrors.huaweicloud.com/repository/npm/",
    },
]


@dataclass
class DownloadMirror:
    """Configuration for a download mirror site."""
    name: str                          # human-readable name
    base_url: str                      # base URL for downloads
    download_pattern: str              # URL pattern with {base} and {version} placeholders


# Node.js download mirrors
NODE_MIRRORS: List[DownloadMirror] = [
    DownloadMirror(
        name="npmmirror (阿里云)",
        base_url="https://npmmirror.com/mirrors/node",
        download_pattern="{base}/v{version}/node-v{version}-x64.msi",
    ),
    DownloadMirror(
        name="华为云",
        base_url="https://mirrors.huaweicloud.com/nodejs",
        download_pattern="{base}/v{version}/node-v{version}-x64.msi",
    ),
]

# Git for Windows download mirrors
GIT_MIRRORS: List[DownloadMirror] = [
    DownloadMirror(
        name="npmmirror (阿里云)",
        base_url="https://npmmirror.com/mirrors/git-for-windows",
        download_pattern="{base}/v{version}.windows.{patch}/Git-{version}-64-bit.exe",
    ),
    DownloadMirror(
        name="华为云",
        base_url="https://mirrors.huaweicloud.com/git-for-windows",
        download_pattern="{base}/v{version}.windows.{patch}/Git-{version}-64-bit.exe",
    ),
]


# Known-good fallback versions (used when mirror version detection fails)
FALLBACK_NODE_VERSION = "22.20.0"
FALLBACK_GIT_VERSION = "2.47.0"
FALLBACK_GIT_PATCH = "1"
