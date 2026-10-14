"""法币出金页面 Page Object - 示例交易所法币提现页面交互封装

针对示例交易所 (www.example.com) 法币出金页面，封装银行卡管理（新增、删除）等操作。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, CriticalElement


class FiatWithdrawPage(BasePage):
    """示例交易所 法币出金页面 Page Object

    URL: https://www.example.com/en/fiat/withdraw 或类似路径
    功能：法币提现，管理银行卡（新增/删除）
    """

    URL_PATH: str = "/en/account/withdraw/fiat"
    PAGE_TITLE: str = ""
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector=(
                "[data-testid='withdraw-form'], .withdraw-form, "
                ".fiat-withdraw, .withdrawal-form, [class*='withdraw']"
            ),
            name="提现表单",
            description="法币提现操作表单区域",
        ),
        CriticalElement(
            selector=(
                "[data-testid='bank-card-list'], .bank-card-list, "
                ".bank-accounts, .saved-banks, [class*='bank-list']"
            ),
            name="银行卡列表",
            description="已绑定的银行卡列表",
        ),
        CriticalElement(
            selector=(
                "[data-testid='add-bank-btn'], button.add-bank, "
                "button:has-text('Add'), button:has-text('新增'), "
                "[class*='add-bank'], a[href*='add-bank']"
            ),
            name="新增银行卡按钮",
            description="添加新银行卡的操作按钮",
        ),
    ]

    # --- 元素定位器 ---
    _ADD_BANK_BUTTON = (
        "[data-testid='add-bank-btn'], button.add-bank, "
        "button:has-text('Add'), button:has-text('新增'), "
        "[class*='add-bank'], a[href*='add-bank']"
    )
    _BANK_CARD_ITEM = (
        "[data-testid='bank-card-item'], .bank-card-item, "
        ".bank-account-item, .saved-bank-item, [class*='bank-item']"
    )
    _DELETE_BANK_BUTTON = (
        "[data-testid='delete-bank-btn'], button.delete-bank, "
        "button[aria-label='Delete'], .delete-btn, "
        "button:has-text('Delete'), button:has-text('删除')"
    )
    _CONFIRM_DELETE = (
        "[data-testid='confirm-delete'], button.confirm-delete, "
        ".modal button.confirm, .dialog button.primary, "
        "button:has-text('Confirm'), button:has-text('确认')"
    )
    # 新增银行卡表单字段
    _BANK_NAME_INPUT = (
        "[data-testid='bank-name-input'], input[name='bankName'], "
        "input[placeholder*='bank'], input[placeholder*='Bank']"
    )
    _ACCOUNT_NAME_INPUT = (
        "[data-testid='account-name-input'], input[name='accountName'], "
        "input[placeholder*='name'], input[placeholder*='Name']"
    )
    _ACCOUNT_NUMBER_INPUT = (
        "[data-testid='account-number-input'], input[name='accountNumber'], "
        "input[placeholder*='account'], input[placeholder*='Account']"
    )
    _SUBMIT_BANK_BUTTON = (
        "[data-testid='submit-bank-btn'], button[type='submit'], "
        "button:has-text('Submit'), button:has-text('提交'), "
        "button:has-text('Save'), button:has-text('保存')"
    )

    @allure.step("点击新增银行卡")
    def click_add_bank(self) -> None:
        """点击新增银行卡按钮，打开添加银行卡表单"""
        add_btn = self.page.locator(self._ADD_BANK_BUTTON).first
        add_btn.wait_for(state="visible", timeout=10000)
        add_btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("填写银行卡信息并提交")
    def add_bank_card(self, bank_name: str, account_name: str, account_number: str) -> None:
        """新增银行卡

        Args:
            bank_name: 银行名称
            account_name: 账户持有人姓名
            account_number: 银行账号
        """
        self.click_add_bank()

        # 填写银行卡信息
        self.page.locator(self._BANK_NAME_INPUT).first.fill(bank_name)
        self.page.locator(self._ACCOUNT_NAME_INPUT).first.fill(account_name)
        self.page.locator(self._ACCOUNT_NUMBER_INPUT).first.fill(account_number)

        # 提交
        self.page.locator(self._SUBMIT_BANK_BUTTON).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("删除银行卡: index={card_index}")
    def delete_bank_card(self, card_index: int = 0) -> None:
        """删除指定位置的银行卡

        Args:
            card_index: 要删除的银行卡在列表中的索引（从0开始）
        """
        # 定位到指定银行卡
        bank_cards = self.page.locator(self._BANK_CARD_ITEM)
        target_card = bank_cards.nth(card_index)
        target_card.wait_for(state="visible", timeout=10000)

        # 点击删除按钮
        delete_btn = target_card.locator(self._DELETE_BANK_BUTTON).first
        delete_btn.click()

        # 确认删除
        confirm_btn = self.page.locator(self._CONFIRM_DELETE).first
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()

        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("获取银行卡数量")
    def get_bank_card_count(self) -> int:
        """获取当前已绑定的银行卡数量

        Returns:
            银行卡数量
        """
        bank_cards = self.page.locator(self._BANK_CARD_ITEM)
        try:
            bank_cards.first.wait_for(state="visible", timeout=10000)
            return bank_cards.count()
        except Exception:
            return 0
