"""HTTP download engine with mirror fallback, retry, and progress reporting."""

import os
import re
import time
import hashlib
import urllib.request
import urllib.error
import tempfile
import threading
from typing import Callable, Optional, List

from data.mirrors import DownloadMirror


# Callback types
ProgressCallback = Callable[[float, str], None]  # percent (0-100), message
LogCallback = Callable[[str], None]               # log line


class DownloadError(Exception):
    """Raised when a download fails after all retries and mirrors."""

    def __init__(self, message: str, mirror_errors: List[str] | None = None):
        super().__init__(message)
        self.mirror_errors = mirror_errors or []


class Downloader:
    """Handles HTTP downloads with mirror fallback and retry logic."""

    def __init__(
        self,
        connect_timeout: int = 30,
        read_timeout: int = 300,
        max_retries: int = 3,
        retry_delay_base: float = 2.0,
    ):
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base

    def download(
        self,
        url: str,
        dest_path: str,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        expected_size: int | None = None,
    ) -> bool:
        """Download a file from a URL to a local path with progress.

        Returns True if successful, raises DownloadError on failure.
        """
        self._log(on_log, f"开始下载: {url}")

        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self.retry_delay_base ** attempt
                    self._log(on_log, f"重试 {attempt}/{self.max_retries} (等待 {delay:.0f}s)...")
                    time.sleep(delay)

                self._do_download(url, dest_path, on_progress, on_log, expected_size)
                self._log(on_log, f"下载完成: {os.path.basename(dest_path)}")
                return True

            except (urllib.error.URLError, OSError, TimeoutError) as e:
                self._log(on_log, f"下载失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise DownloadError(
                        f"下载失败，已重试 {self.max_retries} 次: {e}"
                    ) from e

        return False  # unreachable

    def download_with_mirrors(
        self,
        mirrors: List[DownloadMirror],
        version: str,
        dest_dir: str,
        filename: str | None = None,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        patch: str | None = None,
    ) -> str:
        """Download a file trying each mirror in order.

        Returns the path to the downloaded file.
        Raises DownloadError if all mirrors fail.
        """
        mirror_errors: List[str] = []

        for mirror in mirrors:
            try:
                self._log(on_log, f"尝试镜像: {mirror.name}")

                url = mirror.download_pattern.format(
                    base=mirror.base_url, version=version, patch=patch or ""
                )
                # Clean up double slashes (not in https://)
                url = re.sub(r"(?<!:)//+", "/", url)

                if filename is None:
                    filename = os.path.basename(url)
                dest_path = os.path.join(dest_dir, filename)

                self.download(url, dest_path, on_progress, on_log)
                return dest_path

            except DownloadError as e:
                self._log(on_log, f"镜像 {mirror.name} 失败: {e}")
                mirror_errors.append(f"{mirror.name}: {e}")

        raise DownloadError(
            f"所有镜像均下载失败 (共 {len(mirrors)} 个)",
            mirror_errors=mirror_errors,
        )

    def fetch_text(self, url: str, on_log: LogCallback | None = None) -> str:
        """Fetch a URL and return its text content."""
        self._log(on_log, f"请求: {url}")

        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self.retry_delay_base ** attempt
                    time.sleep(delay)

                req = urllib.request.Request(url, headers={"User-Agent": "ClaudeCodeInstaller/1.0"})
                with urllib.request.urlopen(req, timeout=self.connect_timeout) as resp:
                    return resp.read().decode("utf-8", errors="replace")

            except (urllib.error.URLError, OSError) as e:
                if attempt == self.max_retries - 1:
                    raise DownloadError(f"请求失败: {e}") from e

        return ""  # unreachable

    def _do_download(
        self,
        url: str,
        dest_path: str,
        on_progress: ProgressCallback | None,
        on_log: LogCallback | None,
        expected_size: int | None,
    ):
        """Perform the actual HTTP download."""
        req = urllib.request.Request(url, headers={"User-Agent": "ClaudeCodeInstaller/1.0"})
        with urllib.request.urlopen(req, timeout=self.read_timeout) as resp:
            # Get file size
            content_length = resp.headers.get("Content-Length")
            total_size = (
                int(content_length)
                if content_length
                else expected_size
            )

            if total_size:
                self._log(on_log, f"文件大小: {total_size / 1024 / 1024:.1f} MB")

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)

            downloaded = 0
            chunk_size = 64 * 1024  # 64KB

            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size and on_progress:
                        percent = min(downloaded / total_size * 100, 100.0)
                        on_progress(percent, f"{downloaded / 1024 / 1024:.1f} / {total_size / 1024 / 1024:.1f} MB")

            if total_size and downloaded != total_size:
                raise OSError(
                    f"下载不完整: 期望 {total_size} bytes, 实际 {downloaded} bytes"
                )

    @staticmethod
    def _log(callback: LogCallback | None, message: str):
        if callback:
            callback(message)


# Singleton instance
_default_downloader: Downloader | None = None


def get_downloader() -> Downloader:
    """Get or create the default downloader instance."""
    global _default_downloader
    if _default_downloader is None:
        _default_downloader = Downloader()
    return _default_downloader
