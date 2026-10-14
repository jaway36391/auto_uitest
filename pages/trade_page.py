"""交易页面 Page Object - 示例交易所 Flash Trade 页面交互封装

针对示例交易所 (www.example.com) Flash Trade 页面，封装交易对选择、价格获取、
下单操作等核心交易功能。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, CriticalElement


class TradePage(BasePage):
    """示例交易所 Flash Trade 交易页面 Page Object

    URL: https://www.example.com/en/flash
    功能：闪兑交易（Flash Trade），支持快速买卖加密货币
    """

    URL_PATH: str = "/en/flash"
    PAGE_TITLE: str = ""  # 交易页标题可能动态变化
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector=(
                "[data-testid='trading-pair-selector'], .pair-selector, "
                ".trading-pair, .currency-selector, select.pair-select"
            ),
            name="交易对选择器",
            description="选择交易币对的下拉选择器组件",
        ),
        CriticalElement(
            selector=(
                "[data-testid='current-price'], .current-price, "
                ".price-display, .market-price, .quote-price"
            ),
            name="当前价格显示",
            description="当前交易对的实时价格展示",
        ),
        CriticalElement(
            selector=(
                "[data-testid='amount-input'], input[name='amount'], "
                ".amount-input, .trade-amount input"
            ),
            name="数量输入框",
            description="交易数量输入字段",
        ),
        CriticalElement(
            selector=(
                "[data-testid='trade-button'], button.trade-btn, "
                ".trade-submit, button[type='submit'].trade"
            ),
            name="交易按钮",
            description="提交交易的操作按钮（买入/卖出）",
        ),
    ]

    # --- 元素定位器（可能需要根据实际 DOM 调整） ---
    _PAIR_SELECTOR = (
        "[data-testid='trading-pair-selector'], .pair-selector, "
        ".trading-pair, .currency-selector"
    )
    _CURRENT_PRICE = (
        "[data-testid='current-price'], .current-price, "
        ".price-display, .market-price, .quote-price"
    )
    _SIDE_BUY = "[data-testid='order-side-buy'], .buy-btn, button.buy, [data-side='buy']"
    _SIDE_SELL = "[data-testid='order-side-sell'], .sell-btn, button.sell, [data-side='sell']"
    _PRICE_INPUT = (
        "[data-testid='order-price-input'], input[name='price'], "
        ".price-input input, .order-price input"
    )
    _AMOUNT_INPUT = (
        "[data-testid='amount-input'], input[name='amount'], "
        ".amount-input input, .order-amount input"
    )
    _SUBMIT_ORDER = (
        "[data-testid='trade-button'], button.trade-btn, "
        ".trade-submit, button[type='submit'].trade"
    )

    @allure.step("下限价单: 方向={side}, 价格={price}, 数量={amount}")
    def place_limit_order(self, side: str, price: str, amount: str) -> None:
        """下限价单

        Args:
            side: 交易方向，"buy" 或 "sell"
            price: 委托价格
            amount: 委托数量
        """
        # 选择买卖方向
        if side.lower() == "buy":
            self.page.locator(self._SIDE_BUY).first.click()
        else:
            self.page.locator(self._SIDE_SELL).first.click()

        # 填写价格（Flash Trade 可能不需要价格输入，此处保留兼容性）
        price_input = self.page.locator(self._PRICE_INPUT).first
        if price_input.is_visible():
            price_input.fill(price)

        # 填写数量
        self.page.locator(self._AMOUNT_INPUT).first.fill(amount)

        # 提交订单
        self.page.locator(self._SUBMIT_ORDER).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("获取当前交易价格")
    def get_current_price(self) -> str:
        """获取当前交易对的实时价格

        Returns:
            当前价格的文本内容，如 "42,150.00"
        """
        price_element = self.page.locator(self._CURRENT_PRICE).first
        price_element.wait_for(state="visible", timeout=10000)
        return price_element.text_content() or ""
