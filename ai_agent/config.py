"""AI Agent 配置 - LLM 模型和 browser-use 相关配置"""

from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    """LLM 提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"


class AIConfig(BaseSettings):
    """AI Agent 配置

    通过环境变量（AI_ 前缀）加载。
    智谱 API 兼容 OpenAI 格式，使用 base_url 指向智谱 endpoint。
    """
    # LLM 配置
    provider: LLMProvider = Field(default=LLMProvider.ZHIPU, description="LLM 提供商")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI 模型名称")
    openai_base_url: Optional[str] = Field(default=None, description="OpenAI 兼容 API Base URL")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API Key")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", description="Anthropic 模型名称")

    # 智谱配置
    zhipu_api_key: Optional[str] = Field(default=None, description="智谱 API Key")
    zhipu_model: str = Field(default="glm-4v-plus", description="智谱模型名称")

    # browser-use 配置
    max_steps: int = Field(default=20, description="Agent 最大执行步骤数")
    use_vision: bool = Field(default=True, description="是否使用视觉模型分析页面截图")

    model_config = {
        "env_prefix": "AI_",
        "case_sensitive": False,
    }


def get_ai_config() -> AIConfig:
    """加载 AI 配置"""
    return AIConfig()
