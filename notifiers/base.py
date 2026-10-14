"""告警通知器基类模块

定义 TestResult 数据类和 BaseNotifier 抽象基类。
所有具体通知器（企业微信、钉钉等）均继承 BaseNotifier 实现。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import httpx
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """测试结果摘要"""

    environment: str
    total: int
    passed: int
    failed: int
    duration_seconds: float
    failed_cases: List[str] = field(default_factory=list)
    report_url: str = ""


class BaseNotifier(ABC):
    """通知器抽象基类

    子类需实现 format_message() 方法，定义具体的消息格式。
    send() 方法负责发送通知，捕获所有异常确保不影响测试流程。
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self._client = httpx.Client(timeout=10.0)

    @abstractmethod
    def format_message(self, result: TestResult) -> dict:
        """格式化通知消息体，由子类实现"""
        ...

    def send(self, result: TestResult) -> bool:
        """发送通知

        调用 format_message() 格式化消息后 POST 到 webhook_url。
        捕获所有异常，失败时仅记录日志不抛出，返回 False。

        Args:
            result: 测试结果摘要

        Returns:
            True 表示发送成功，False 表示发送失败
        """
        try:
            payload = self.format_message(result)
            response = self._client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"告警通知发送成功: {self.__class__.__name__}")
            return True
        except Exception as e:
            logger.error(f"告警通知发送失败: {self.__class__.__name__}, 错误: {e}")
            return False

    def close(self) -> None:
        """释放 httpx 客户端资源"""
        self._client.close()
