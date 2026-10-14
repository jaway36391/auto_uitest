"""法币入金 - 查看银行VA信息测试

验证法币入金页面能正常展示银行 Virtual Account 信息，
包括银行名称、账户号码等关键信息的完整性。

注意：此测试仅做只读验证（查看VA信息），不触发任何实际充值操作，
可安全在生产环境运行。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups
from pages.fiat_deposit_page import FiatDepositPage


@pytest.mark.critical_flow
@pytest.mark.prod_safe
@allure.feature("法币业务流程验证")
@allure.story("法币入金 - 查看银行VA信息")
class TestFiatDeposit:
    """法币入金页面测试套件（只读验证，生产安全）"""

    @allure.title("验证法币入金页面加载")
    @allure.description("验证法币入金页面能正常加载，关键元素可见")
    def test_fiat_deposit_page_loads(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证法币入金页面正常加载"""
        deposit_page = FiatDepositPage(authenticated_page, settings.base_url)

        with allure.step("导航到法币入金页面"):
            deposit_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证关键元素"):
            missing_elements = deposit_page.verify_critical_elements()

        if missing_elements:
            missing_info = "\n".join(
                f"- {elem.name}: selector='{elem.selector}'"
                for elem in missing_elements
            )
            allure.attach(
                missing_info,
                name="missing_elements",
                attachment_type=allure.attachment_type.TEXT,
            )
            screenshot = authenticated_page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="fiat_deposit_page_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        assert not missing_elements, (
            f"法币入金页面缺失 {len(missing_elements)} 个关键元素: "
            f"{', '.join(e.name for e in missing_elements)}"
        )

    @allure.title("查看银行VA信息")
    @allure.description(
        "验证法币入金页面能正确展示银行 Virtual Account 信息（只读操作，不触发充值）"
    )
    def test_view_bank_va_info(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证银行VA信息展示（只读，生产安全）

        仅查看VA信息是否正确展示，不触发任何充值操作。
        """
        deposit_page = FiatDepositPage(authenticated_page, settings.base_url)

        with allure.step("导航到法币入金页面"):
            deposit_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证VA信息已展示"):
            va_displayed = deposit_page.verify_va_info_displayed()
            assert va_displayed, "银行VA信息未正确展示"

        with allure.step("获取VA详细信息"):
            va_info = deposit_page.view_bank_va_info()
            allure.attach(
                f"银行名称: {va_info['bank_name']}\n"
                f"账户号码: {va_info['account_number']}",
                name="va_info_details",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("验证VA信息完整性"):
            assert va_info["bank_name"], "银行名称为空"
            assert va_info["account_number"], "账户号码为空"
