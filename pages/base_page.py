"""Page Object 基类模块 - 定义所有页面对象的通用行为"""

from dataclasses import dataclass
from typing import List

import allure
from playwright.sync_api import Page, expect


@dataclass
class CriticalElement:
    """关键元素定义

    用于描述页面中必须存在的关键UI元素，供 verify_critical_elements() 验证。

    Attributes:
        selector: CSS 选择器或 Playwright 支持的定位器字符串
        name: 元素的可读名称，用于报告和日志
        description: 元素的详细描述（可选）
    """

    selector: str
    name: str
    description: str = ""


class BasePage:
    """Page Object 基类

    所有页面对象继承此基类，提供通用的导航、验证和监控能力。
    子类需要定义 URL_PATH、PAGE_TITLE 和 CRITICAL_ELEMENTS 类属性。

    Attributes:
        URL_PATH: 页面路径（相对于 base_url）
        PAGE_TITLE: 页面标题（用于验证页面加载）
        CRITICAL_ELEMENTS: 页面关键元素列表
    """

    URL_PATH: str = ""
    PAGE_TITLE: str = ""
    CRITICAL_ELEMENTS: List[CriticalElement] = []

    def __init__(self, page: Page, base_url: str):
        """初始化 BasePage

        Args:
            page: Playwright Page 实例
            base_url: 目标环境基础 URL
        """
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def full_url(self) -> str:
        """完整页面 URL"""
        return f"{self.base_url}{self.URL_PATH}"

    @allure.step("导航到页面")
    def navigate(self) -> None:
        """导航到页面"""
        self.page.goto(self.full_url, wait_until="domcontentloaded")

    @allure.step("验证页面加载成功")
    def verify_page_loaded(self) -> None:
        """验证页面基本加载

        断言当前 URL 匹配预期，如果定义了 PAGE_TITLE 则同时验证标题。
        """
        expect(self.page).to_have_url(self.full_url)
        if self.PAGE_TITLE:
            expect(self.page).to_have_title(self.PAGE_TITLE)

    @allure.step("验证关键元素存在")
    def verify_critical_elements(self) -> List[CriticalElement]:
        """验证所有关键元素可见，返回缺失元素列表

        遍历 CRITICAL_ELEMENTS 中定义的所有元素，使用 Playwright 的
        to_be_visible 断言验证可见性。

        Returns:
            缺失（不可见）的元素列表。空列表表示所有元素均可见。
        """
        missing: List[CriticalElement] = []
        for element in self.CRITICAL_ELEMENTS:
            locator = self.page.locator(element.selector)
            try:
                expect(locator).to_be_visible(timeout=10000)
            except AssertionError:
                missing.append(element)
        return missing

    def setup_console_listener(self) -> None:
        """设置控制台错误监听

        在页面导航前调用此方法，以捕获页面加载过程中的所有控制台错误消息。
        """
        self._console_errors: List[str] = []
        self.page.on(
            "console",
            lambda msg: (
                self._console_errors.append(msg.text) if msg.type == "error" else None
            ),
        )

    def get_console_errors(self) -> List[str]:
        """获取已捕获的控制台错误消息

        需要先调用 setup_console_listener() 设置监听。

        Returns:
            捕获到的控制台错误消息列表。
        """
        return getattr(self, "_console_errors", [])
