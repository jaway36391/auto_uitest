"""市场行情页面 Page Object - 示例交易所市场列表页面交互封装

针对示例交易所 (www.example.com) 市场行情页面，定义关键 UI 元素和页面验证逻辑。
市场页面展示所有可交易币对的实时行情数据。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

from pages.base_page import BasePage, CriticalElement


class MarketsPage(BasePage):
    """示例交易所 市场行情页面 Page Object

    URL: https://www.example.com/en/markets
    功能：展示所有可交易币对的实时行情、涨跌幅、成交量等数据
    """

    URL_PATH: str = "/en/markets"
    PAGE_TITLE: str = ""  # 市场页标题可能动态变化
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector=(
                "[data-testid='market-table'], .market-table, "
                "table.markets, .market-list, .price-table"
            ),
            name="行情列表表格",
            description="展示所有交易对行情数据的表格/列表",
        ),
        CriticalElement(
            selector=(
                "[data-testid='market-search'], input[placeholder*='search'], "
                "input[placeholder*='Search'], .market-search input, .search-bar input"
            ),
            name="币种搜索框",
            description="搜索/筛选特定交易对的输入框",
        ),
        CriticalElement(
            selector=(
                "[data-testid='market-tabs'], .market-tabs, "
                ".category-tabs, .market-filter-tabs, nav.market-nav"
            ),
            name="市场分类标签",
            description="按分类筛选交易对的标签页（如全部、热门、新上线等）",
        ),
    ]
