"""AI company and model catalog for the model configuration tab."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelInfo:
    """Information about a specific AI model."""
    id: str              # e.g. "claude-opus-4-8", "gpt-4o"
    name: str            # e.g. "Claude Opus 4.8", "GPT-4o"
    description: str     # brief capability description


@dataclass
class CompanyInfo:
    """Information about an AI company and its available models."""
    id: str              # e.g. "anthropic", "openai"
    name: str            # e.g. "Anthropic", "OpenAI"
    models: List[ModelInfo] = field(default_factory=list)
    api_key_prefix: str = ""          # e.g. "sk-ant-", "sk-"
    api_key_help: str = ""            # help text for the user
    base_url: str = ""                # default API base URL
    provider_config_key: str = ""     # key used in Claude Code config


# Catalog of supported companies
COMPANIES: List[CompanyInfo] = [
    CompanyInfo(
        id="anthropic",
        name="Anthropic",
        api_key_prefix="sk-ant-",
        api_key_help="在 https://console.anthropic.com/ 创建 API Key",
        base_url="https://api.anthropic.com",
        provider_config_key="anthropic",
        models=[
            ModelInfo("claude-opus-4-8", "Claude Opus 4.8", "最强 Opus 系列模型"),
            ModelInfo("claude-sonnet-4-6", "Claude Sonnet 4.6", "最佳速度/智能平衡"),
            ModelInfo("claude-haiku-4-5", "Claude Haiku 4.5", "最快、最具性价比"),
        ],
    ),
    CompanyInfo(
        id="openai",
        name="OpenAI",
        api_key_prefix="sk-",
        api_key_help="在 https://platform.openai.com/api-keys 创建 API Key",
        base_url="https://api.openai.com/v1",
        provider_config_key="openai",
        models=[
            ModelInfo("gpt-4o", "GPT-4o", "旗舰多模态模型"),
            ModelInfo("gpt-4o-mini", "GPT-4o Mini", "更小更快的变体"),
            ModelInfo("o4-mini", "o4-mini", "推理模型"),
        ],
    ),
    CompanyInfo(
        id="google",
        name="Google (Gemini)",
        api_key_prefix="",
        api_key_help="在 https://aistudio.google.com/apikey 创建 API Key",
        base_url="",
        provider_config_key="google",
        models=[
            ModelInfo("gemini-2.5-pro", "Gemini 2.5 Pro", "最强 Gemini 模型"),
            ModelInfo("gemini-2.5-flash", "Gemini 2.5 Flash", "快速高效"),
        ],
    ),
    CompanyInfo(
        id="deepseek",
        name="DeepSeek",
        api_key_prefix="sk-",
        api_key_help="在 https://platform.deepseek.com/ 创建 API Key",
        base_url="https://api.deepseek.com",
        provider_config_key="deepseek",
        models=[
            ModelInfo("deepseek-chat", "DeepSeek Chat (V3)", "通用对话模型"),
            ModelInfo("deepseek-reasoner", "DeepSeek Reasoner (R1)", "深度推理模型"),
        ],
    ),
    CompanyInfo(
        id="moonshot",
        name="Moonshot (Kimi)",
        api_key_prefix="sk-",
        api_key_help="在 https://platform.moonshot.cn/ 创建 API Key",
        base_url="https://api.moonshot.cn/v1",
        provider_config_key="moonshot",
        models=[
            ModelInfo("moonshot-v1-8k", "Moonshot v1 (8K)", "标准上下文"),
            ModelInfo("moonshot-v1-32k", "Moonshot v1 (32K)", "长上下文"),
            ModelInfo("moonshot-v1-128k", "Moonshot v1 (128K)", "超长上下文"),
        ],
    ),
    CompanyInfo(
        id="zhipu",
        name="智谱 AI (GLM)",
        api_key_prefix="",
        api_key_help="在 https://open.bigmodel.cn/ 创建 API Key",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        provider_config_key="zhipu",
        models=[
            ModelInfo("glm-4-plus", "GLM-4 Plus", "旗舰模型"),
            ModelInfo("glm-4-flash", "GLM-4 Flash", "快速版，支持免费额度"),
        ],
    ),
]


def find_company(company_id: str) -> CompanyInfo | None:
    """Find a company by its ID."""
    for company in COMPANIES:
        if company.id == company_id:
            return company
    return None
