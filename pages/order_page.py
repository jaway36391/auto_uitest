"""订单页面 Page Object - 示例交易所订单历史页面交互封装

针对示例交易所 (www.example.com) 订单管理页面，封装订单列表查看、筛选和撤单操作。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, CriticalElement


class OrderPage(BasePage):
    """示例交易所 订单历史页面 Page Object

    URL: https://www.example.com/en/orders 或类似路径
    功能：展示用户历史订单、当前挂单，支持撤单操作
    """

    URL_PATH: str = "/en/orders"
    PAGE_TITLE: str = ""  # 订单页标题可能动态变化
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector=(
                "[data-testid='order-list'], .order-list, "
                ".order-table, table.orders, .order-history"
            ),
            name="订单列表",
            description="用户订单记录列表/表格",
        ),
        CriticalElement(
            selector=(
                "[data-testid='order-filter'], .order-filter, "
                ".filter-bar, .order-tabs, .tab-nav"
            ),
            name="订单筛选器",
            description="订单状态筛选器（全部/挂单中/已成交/已撤销）",
        ),
        CriticalElement(
            selector=(
                "[data-testid='open-orders-tab'], .open-orders, "
                "button[data-tab='open'], a[href*='open']"
            ),
            name="当前挂单标签",
            description="切换到当前挂单列表的标签页",
        ),
    ]

    # --- 元素定位器（可能需要根据实际 DOM 调整） ---
    _CANCEL_BUTTON = (
        "[data-testid='cancel-order'], button.cancel-order, "
        ".cancel-btn, button[aria-label='Cancel order']"
    )
    _CONFIRM_CANCEL = (
        "[data-testid='confirm-cancel'], button.confirm-cancel, "
        ".modal button.confirm, .dialog button.primary"
    )
    _ORDER_ROW = (
        "[data-testid='order-row'], .order-row, "
        "tr.order-item, .order-list-item"
    )

    @allure.step("撤销订单")
    def cancel_order(self, order_index: int = 0) -> None:
        """撤销指定位置的挂单

        点击订单行的撤单按钮，并在确认弹窗中确认撤销操作。

        Args:
            order_index: 要撤销的订单在列表中的索引位置（从0开始），默认撤销第一条
        """
        # 定位到指定订单行的撤单按钮
        order_rows = self.page.locator(self._ORDER_ROW)
        target_row = order_rows.nth(order_index)
        cancel_btn = target_row.locator(self._CANCEL_BUTTON).first
        cancel_btn.click()

        # 等待确认弹窗并点击确认
        confirm_btn = self.page.locator(self._CONFIRM_CANCEL).first
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()

        # 等待撤单操作完成
        self.page.wait_for_load_state("domcontentloaded")
