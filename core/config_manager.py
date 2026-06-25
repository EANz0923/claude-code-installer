"""Read and write Claude Code configuration files."""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from data.models import CompanyInfo


class ConfigManager:
    """Manages the Claude Code configuration file."""

    @staticmethod
    def get_config_path() -> str:
        """Get the path to the Claude Code config file."""
        return os.path.join(os.path.expanduser("~"), ".claude.json")

    @staticmethod
    def get_settings_path() -> str:
        """Get the path to the Claude Code settings file."""
        return os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "Claude",
            "settings.json",
        )

    def read_config(self) -> Dict[str, Any]:
        """Read the existing Claude Code config file.

        Returns an empty dict if the file does not exist.
        """
        config_path = self.get_config_path()
        if not os.path.exists(config_path):
            return {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            # Back up corrupt file
            backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(config_path, backup_path)
            return {}

    def save_provider_config(
        self,
        company: CompanyInfo,
        model_id: str,
        api_key: str,
    ) -> bool:
        """Save a third-party provider configuration to the Claude Code config.

        Writes to ~/.claude.json under the 'providers' key.

        Returns True if successful.
        """
        config = self.read_config()

        # Ensure providers section exists
        if "providers" not in config:
            config["providers"] = {}

        # Write provider configuration
        provider_key = company.provider_config_key or company.id
        provider_config = {
            "apiKey": api_key,
        }
        if company.base_url:
            provider_config["baseUrl"] = company.base_url

        config["providers"][provider_key] = provider_config

        # Also set the default model
        config["model"] = model_id

        # Write atomically: write to temp file, then rename
        config_path = self.get_config_path()
        temp_path = f"{config_path}.tmp"
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, config_path)
            return True
        except OSError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    def get_current_provider(self) -> Optional[Dict[str, Any]]:
        """Get the currently configured provider info.

        Returns a dict with 'company_id', 'model_id', 'api_key_masked', or None.
        """
        config = self.read_config()
        providers = config.get("providers", {})

        if not providers:
            return None

        # Return the first configured provider
        for provider_key, provider_data in providers.items():
            api_key = provider_data.get("apiKey", "")
            masked = self._mask_key(api_key)
            return {
                "company_id": provider_key,
                "model_id": config.get("model", ""),
                "api_key_masked": masked,
                "has_key": bool(api_key),
            }

        return None

    def test_connection(
        self,
        company: CompanyInfo,
        api_key: str,
    ) -> tuple[bool, str]:
        """Test the API connection for a given company and API key.

        Returns (success, message).
        """
        import urllib.request
        import urllib.error

        # Build a minimal request to test the key
        if company.id == "anthropic":
            return self._test_anthropic(api_key)
        elif company.id == "openai":
            return self._test_openai(api_key)
        elif company.id == "google":
            return self._test_google(api_key)
        elif company.id == "deepseek":
            return self._test_openai_compatible(company.base_url, api_key)
        elif company.id == "moonshot":
            return self._test_openai_compatible(company.base_url, api_key)
        elif company.id == "zhipu":
            return self._test_zhipu(api_key)
        else:
            return self._test_openai_compatible(company.base_url, api_key)

    def _test_anthropic(self, api_key: str) -> tuple[bool, str]:
        """Test Anthropic API key."""
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps({
                    "model": "claude-haiku-4-5",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "hi"}],
                }).encode("utf-8"),
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return True, "连接成功 - Anthropic API 可用"
                return False, f"API 返回状态码: {resp.status}"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 401:
                return False, "API Key 无效 (401 Unauthorized)"
            if e.code == 403:
                return False, "API Key 无权限 (403 Forbidden)"
            return False, f"HTTP {e.code}: {body[:200]}"
        except urllib.error.URLError as e:
            return False, f"网络错误: {e.reason}"

    def _test_openai(self, api_key: str) -> tuple[bool, str]:
        """Test OpenAI API key."""
        return self._test_openai_compatible("https://api.openai.com/v1", api_key)

    def _test_google(self, api_key: str) -> tuple[bool, str]:
        """Test Google (Gemini) API key."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return True, "连接成功 - Gemini API 可用"
                return False, f"API 返回状态码: {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return False, "API Key 无效 (400 Bad Request)"
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"网络错误: {e.reason}"

    def _test_openai_compatible(self, base_url: str, api_key: str) -> tuple[bool, str]:
        """Test an OpenAI-compatible API endpoint."""
        try:
            req = urllib.request.Request(
                f"{base_url}/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return True, "连接成功"
                return False, f"API 返回状态码: {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return False, f"API Key 无效 (HTTP {e.code})"
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"网络错误: {e.reason}"

    def _test_zhipu(self, api_key: str) -> tuple[bool, str]:
        """Test Zhipu AI (GLM) API key."""
        try:
            req = urllib.request.Request(
                "https://open.bigmodel.cn/api/paas/v4/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return True, "连接成功 - 智谱 AI API 可用"
                return False, f"API 返回状态码: {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return False, f"API Key 无效 (HTTP {e.code})"
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"网络错误: {e.reason}"

    @staticmethod
    def _mask_key(key: str) -> str:
        """Mask an API key for display, showing only prefix and suffix."""
        if not key:
            return "(未设置)"
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:6]}...{key[-4:]}"


# Singleton
_default_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get or create the default config manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = ConfigManager()
    return _default_manager
