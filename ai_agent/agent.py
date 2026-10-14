"""AI Agent 核心 - 封装 browser-use + LLM 的巡检代理

用自然语言描述测试任务，AI Agent 自动执行浏览器操作并返回结果。
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import List, Optional

import allure
from browser_use import Agent, BrowserSession
from playwright.async_api import BrowserContext

from ai_agent.config import AIConfig, LLMProvider, get_ai_config

logger = logging.getLogger(__name__)


@dataclass
class PatrolResult:
    """巡检任务执行结果"""
    task: str
    success: bool
    summary: str
    steps_taken: int = 0
    screenshots: List[bytes] = field(default_factory=list)
    error: Optional[str] = None
    raw_output: str = ""


def _create_llm(config: AIConfig):
    """根据配置创建 LLM 实例"""
    if config.provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI
        kwargs = {
            "model": config.openai_model,
            "api_key": config.openai_api_key,
        }
        if config.openai_base_url:
            kwargs["base_url"] = config.openai_base_url
        return ChatOpenAI(**kwargs)
    elif config.provider == LLMProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.anthropic_model,
            api_key=config.anthropic_api_key,
        )
    elif config.provider == LLMProvider.ZHIPU:
        from langchain_openai import ChatOpenAI
        # 智谱 API 兼容 OpenAI 格式
        return ChatOpenAI(
            model=config.zhipu_model,
            api_key=config.zhipu_api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4",
        )
    else:
        raise ValueError(f"不支持的 LLM 提供商: {config.provider}")


class PatrolAgent:
    """交易所 UI 巡检 AI Agent

    封装 browser-use Agent，提供自然语言驱动的巡检能力。
    """

    def __init__(
        self,
        config: Optional[AIConfig] = None,
        browser_context: Optional[BrowserContext] = None,
    ):
        self.config = config or get_ai_config()
        self.llm = _create_llm(self.config)
        self._browser_context = browser_context

    async def execute(self, task: str) -> PatrolResult:
        """执行自然语言描述的巡检任务

        Args:
            task: 自然语言测试任务描述，如 "导航到法币入金页面，查看银行VA信息"

        Returns:
            PatrolResult 执行结果
        """
        logger.info(f"开始执行巡检任务: {task}")

        try:
            # 创建 browser-use Agent
            agent = Agent(
                task=task,
                llm=self.llm,
                max_steps=self.config.max_steps,
                use_vision=self.config.use_vision,
                browser_session=BrowserSession(
                    browser_context=self._browser_context,
                ) if self._browser_context else None,
            )

            # 执行任务
            result = await agent.run()

            # 解析结果
            final_result = result.final_result() if result else ""
            history = result.history if result else []

            return PatrolResult(
                task=task,
                success=True,
                summary=final_result or "任务执行完成",
                steps_taken=len(history),
                raw_output=str(final_result),
            )

        except Exception as e:
            logger.error(f"巡检任务执行失败: {task}, 错误: {e}")
            return PatrolResult(
                task=task,
                success=False,
                summary=f"任务执行失败: {str(e)}",
                error=str(e),
            )


async def run_patrol_task(
    task: str,
    config: Optional[AIConfig] = None,
    browser_context: Optional[BrowserContext] = None,
) -> PatrolResult:
    """便捷函数：执行单个巡检任务

    Args:
        task: 自然语言测试任务描述
        config: AI 配置（可选，默认从环境变量加载）
        browser_context: Playwright 浏览器上下文（可选，用于注入 cookies）

    Returns:
        PatrolResult 执行结果
    """
    agent = PatrolAgent(config=config, browser_context=browser_context)
    return await agent.execute(task)
