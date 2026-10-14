"""交易记录页面 Page Object - 示例交易所交易历史页面交互封装

针对示例交易所 (www.example.com) 交易记录页面，封装交易历史查看和筛选操作。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, CriticalElement


class TransactionHistoryPage(BasePage):
    """示例交易所 交易记录页面 Page Object

    URL: https://www.example.com/en/transactions 或类似路径
    功能：展示用户的交易历史记录（充值、提现、交易等）
    """

    URL_PATH: str = "/en/asset/deposit_withdraw_records"
    PAGE_TITLE: str = ""
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector=(
                "[data-testid='transaction-list'], .transaction-list, "
                ".transaction-table, table.transactions, "
                ".history-list, [class*='transaction-list']"
            ),
            name="交易记录列表",
            description="交易历史记录列表/表格",
        ),
        CriticalElement(
            selector=(
                "[data-testid='transaction-filter'], .transaction-filter, "
                ".filter-bar, .history-filter, .tab-nav, "
                "[class*='filter'], [class*='tabs']"
            ),
            name="交易记录筛选器",
            description="按类型/时间筛选交易记录的控件",
        ),
        CriticalElement(
            selector=(
                "[data-testid='transaction-item'], .transaction-item, "
                "tr.transaction-row, .history-item, "
                "[class*='transaction-item'], [class*='history-row']"
            ),
            name="交易记录条目",
            description="单条交易记录展示",
        ),
    ]

    # --- 元素定位器 ---
    _TRANSACTION_LIST = (
        "[data-testid='transaction-list'], .transaction-list, "
        ".transaction-table, table.transactions, .history-list"
    )
    _TRANSACTION_ITEM = (
        "[data-testid='transaction-item'], .transaction-item, "
        "tr.transaction-row, .history-item"
    )
    _FILTER_TABS = (
        "[data-testid='transaction-filter'], .transaction-filter, "
        ".filter-bar, .history-filter, .tab-nav"
    )
    _DATE_RANGE_PICKER = (
        "[data-testid='date-range'], .date-range-picker, "
        "input[type='date'], .date-filter"
    )

    @allure.step("验证交易记录列表已加载")
    def verify_transaction_list_loaded(self) -> bool:
        """验证交易记录列表是否成功加载

        Returns:
            True 表示列表已加载且有数据，False 表示加载失败或无数据
        """
        try:
            transaction_list = self.page.locator(self._TRANSACTION_LIST).first
            transaction_list.wait_for(state="visible", timeout=15000)
            return True
        except Exception:
            return False

    @allure.step("获取交易记录数量")
    def get_transaction_count(self) -> int:
        """获取当前页面展示的交易记录数量

        Returns:
            交易记录条目数量
        """
        items = self.page.locator(self._TRANSACTION_ITEM)
        try:
            items.first.wait_for(state="visible", timeout=15000)
            return items.count()
        except Exception:
            return 0

    @allure.step("筛选交易类型: {filter_type}")
    def filter_by_type(self, filter_type: str) -> None:
        """按类型筛选交易记录

        Args:
            filter_type: 筛选类型文本（如 "All", "Deposit", "Withdrawal", "Trade"）
        """
        filter_tab = self.page.locator(
            f"{self._FILTER_TABS} >> text='{filter_type}'"
        ).first
        filter_tab.wait_for(state="visible", timeout=10000)
        filter_tab.click()
        self.page.wait_for_load_state("domcontentloaded")
