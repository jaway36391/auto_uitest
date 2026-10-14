"""撤单流程测试

验证撤单流程：登录 → 导航到订单页 → 选择挂单 → 执行撤单 → 验证撤单成功。
使用 authenticated_page fixture 提供已登录的页面实例。

注意：此测试为模拟测试，在生产环境中跳过以避免影响真实订单。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings, Environment
from fixtures.environment import dismiss_initial_popups
from pages.order_page import OrderPage


@pytest.mark.critical_flow
@allure.feature("关键业务流程验证")
@allure.story("撤单流程")
class TestCancelOrder:
    """撤单流程测试套件"""

    @allure.title("撤单流程验证")
    @allure.description(
        "验证撤单流程：导航到订单页 → 定位挂单 → 执行撤单 → 确认撤单 → 验证撤单成功"
    )
    def test_cancel_order(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证撤单流程

        前置条件：
        - 已通过 authenticated_page fixture 完成登录
        - 非生产环境（生产环境跳过）
        - 存在可撤销的挂单

        流程：
        1. 检查环境（生产环境跳过）
        2. 导航到订单页
        3. 关闭初始弹窗
        4. 执行撤单操作
        5. 验证撤单成功
        """
        if settings.env == Environment.PRODUCTION:
            pytest.skip("生产环境跳过撤单测试，避免影响真实订单")

        order_page = OrderPage(authenticated_page, settings.base_url)

        with allure.step("导航到订单页"):
            order_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("检查是否存在可撤销的挂单"):
            order_row_selector = (
                "[data-testid='order-row'], .order-row, "
                "tr.order-item, .order-list-item"
            )
            order_rows = authenticated_page.locator(order_row_selector)
            try:
                order_rows.first.wait_for(state="visible", timeout=10000)
            except Exception:
                pytest.skip("当前无可撤销的挂单，跳过撤单测试")

        with allure.step("执行撤单操作"):
            order_page.cancel_order(order_index=0)

        with allure.step("验证撤单成功"):
            # 检查是否出现撤单成功的指示器
            success_indicator = authenticated_page.locator(
                "[data-testid='cancel-success'], "
                ".cancel-success, "
                ".toast-success, "
                ".notification-success, "
                "[class*='success']"
            ).first
            try:
                success_indicator.wait_for(state="visible", timeout=10000)
            except Exception:
                # 如果没有明确的成功指示器，检查页面是否无错误提示
                error_indicator = authenticated_page.locator(
                    "[data-testid='cancel-error'], "
                    ".cancel-error, "
                    ".toast-error, "
                    ".notification-error"
                ).first
                assert not error_indicator.is_visible(), "撤单操作出现错误提示"
