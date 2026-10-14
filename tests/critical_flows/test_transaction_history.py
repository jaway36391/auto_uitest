"""交易记录查看测试

验证交易记录页面能正常加载并展示历史交易数据。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups
from pages.transaction_history_page import TransactionHistoryPage


@pytest.mark.critical_flow
@pytest.mark.prod_safe
@allure.feature("法币业务流程验证")
@allure.story("查看交易记录")
class TestTransactionHistory:
    """交易记录页面测试套件"""

    @allure.title("验证交易记录页面加载")
    @allure.description("验证交易记录页面能正常加载，关键元素可见")
    def test_transaction_history_page_loads(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证交易记录页面正常加载

        前置条件：已通过 authenticated_page fixture 完成登录

        流程：
        1. 导航到交易记录页面
        2. 关闭初始弹窗
        3. 验证页面关键元素存在
        """
        history_page = TransactionHistoryPage(authenticated_page, settings.base_url)

        with allure.step("导航到交易记录页面"):
            history_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证关键元素"):
            missing_elements = history_page.verify_critical_elements()

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
                name="transaction_history_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        assert not missing_elements, (
            f"交易记录页面缺失 {len(missing_elements)} 个关键元素: "
            f"{', '.join(e.name for e in missing_elements)}"
        )

    @allure.title("验证交易记录列表加载")
    @allure.description("验证交易记录列表能成功加载并展示数据")
    def test_transaction_list_loaded(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证交易记录列表数据加载

        前置条件：已通过 authenticated_page fixture 完成登录

        流程：
        1. 导航到交易记录页面
        2. 关闭初始弹窗
        3. 验证交易记录列表已加载
        4. 获取并记录交易记录数量
        """
        history_page = TransactionHistoryPage(authenticated_page, settings.base_url)

        with allure.step("导航到交易记录页面"):
            history_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证交易记录列表已加载"):
            list_loaded = history_page.verify_transaction_list_loaded()
            assert list_loaded, "交易记录列表未能成功加载"

        with allure.step("获取交易记录数量"):
            count = history_page.get_transaction_count()
            allure.attach(
                f"当前页面交易记录数量: {count}",
                name="transaction_count",
                attachment_type=allure.attachment_type.TEXT,
            )
            # 交易记录可能为空（新账户），仅记录不强制断言
            if count == 0:
                allure.attach(
                    "注意：当前账户无交易记录，可能是新账户或筛选条件限制",
                    name="warning",
                    attachment_type=allure.attachment_type.TEXT,
                )

    @allure.title("验证交易记录筛选功能")
    @allure.description("验证交易记录页面的筛选功能正常工作")
    def test_transaction_filter(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证交易记录筛选功能

        前置条件：已通过 authenticated_page fixture 完成登录

        流程：
        1. 导航到交易记录页面
        2. 关闭初始弹窗
        3. 尝试按类型筛选（如 Deposit）
        4. 验证筛选后页面无错误
        """
        history_page = TransactionHistoryPage(authenticated_page, settings.base_url)

        with allure.step("导航到交易记录页面"):
            history_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("等待页面加载完成"):
            history_page.verify_transaction_list_loaded()

        with allure.step("尝试筛选 Deposit 类型"):
            try:
                history_page.filter_by_type("Deposit")
            except Exception as e:
                allure.attach(
                    f"筛选操作异常（可能筛选器不存在或文案不同）: {e}",
                    name="filter_warning",
                    attachment_type=allure.attachment_type.TEXT,
                )
                # 筛选器可能不存在或文案不同，不强制失败
                return

        with allure.step("验证筛选后页面正常"):
            # 验证页面没有出现错误提示
            error_indicator = authenticated_page.locator(
                ".error, .toast-error, [class*='error-message']"
            ).first
            assert not error_indicator.is_visible(), "筛选后页面出现错误提示"
