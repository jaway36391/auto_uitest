"""首页 Page Object - 示例交易所首页交互封装

针对示例交易所 (www.example.com) 首页，定义关键 UI 元素和页面验证逻辑。
首页包含导航栏、Hero 区域、市场概览等核心模块。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

from pages.base_page import BasePage, CriticalElement


class HomePage(BasePage):
    """示例交易所 首页 Page Object

    URL: https://www.example.com/ 或 https://www.example.com/en/
    功能：展示平台概览、导航入口、市场行情摘要
    """

    URL_PATH: str = "/"
    PAGE_TITLE: str = ""  # 首页标题可根据目标交易所实际情况填写
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector="nav, header nav, [data-testid='main-nav'], .navbar, .header-nav",
            name="主导航栏",
            description="页面顶部主导航栏，包含各功能入口链接",
        ),
        CriticalElement(
            selector=(
                "[data-testid='hero-section'], .hero, .banner, "
                "section.hero, .home-banner, main > section:first-child"
            ),
            name="Hero 区域",
            description="首页顶部 Hero/Banner 展示区域",
        ),
        CriticalElement(
            selector=(
                "[data-testid='market-overview'], .market-overview, "
                ".market-section, .price-ticker, .market-data"
            ),
            name="市场概览",
            description="首页市场行情概览区域，展示主要币种价格",
        ),
    ]
