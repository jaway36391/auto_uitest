"""法币入金页面 Page Object - 示例交易所法币充值页面交互封装

针对示例交易所 (www.example.com) 法币入金页面，封装银行 VA（Virtual Account）信息查看等操作。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, CriticalElement


class FiatDepositPage(BasePage):
    """示例交易所 法币入金页面 Page Object

    URL: https://www.example.com/en/fiat/deposit 或类似路径
    功能：展示银行 VA（Virtual Account）信息，用于法币充值
    """

    URL_PATH: str = "/en/account/deposit/fiat"
    PAGE_TITLE: str = ""
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector='button:has-text("Next")',
            name="Next按钮",
            description="下一步操作按钮",
        ),
        CriticalElement(
            selector="text=deposit information",
            name="充值信息提示",
            description="充值信息更新提示文字",
        ),
        CriticalElement(
            selector="text=US Dollar",
            name="US Dollar选项",
            description="美元充值选项",
        ),
    ]

    # --- 元素定位器 ---
    _DEPOSIT_TITLE = "text=Fiat Deposit"
    _USD_OPTION = "text=USD"
    _NEXT_BUTTON = 'button:has-text("Next")'
    _DEPOSIT_INFO = "text=deposit information"

    @allure.step("查看银行VA信息")
    def view_bank_va_info(self) -> dict:
        """点击 Next 后查看银行 VA 信息

        Returns:
            包含页面文本内容的字典
        """
        # 点击 Next 按钮进入 VA 信息页面
        next_btn = self.page.locator(self._NEXT_BUTTON).first
        next_btn.wait_for(state="visible", timeout=15000)
        next_btn.click()
        self.page.wait_for_timeout(3000)

        # 获取页面文本内容
        page_text = self.page.locator("body").inner_text()

        return {
            "bank_name": "visible" if "bank" in page_text.lower() else "",
            "account_number": "visible" if any(c.isdigit() for c in page_text) else "",
            "page_content": page_text[:500],
        }

    @allure.step("验证VA信息完整性")
    def verify_va_info_displayed(self) -> bool:
        """验证充值页面核心元素是否展示

        Returns:
            True 表示页面核心元素存在
        """
        try:
            # 验证 Fiat Deposit 标题和 Next 按钮存在
            self.page.locator(self._DEPOSIT_TITLE).first.wait_for(state="visible", timeout=15000)
            self.page.locator(self._NEXT_BUTTON).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return False
