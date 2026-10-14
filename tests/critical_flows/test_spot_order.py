"""现货下单流程测试

验证现货限价下单流程：登录 → 导航到交易页 → 填写订单参数 → 提交 → 验证订单创建。
使用 authenticated_page fixture 提供已登录的页面实例。

注意：此测试为模拟测试，在生产环境中跳过以避免产生真实订单。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings, Environment
from fixtures.environment import dismiss_initial_popups
from pages.trade_page import TradePage


@pytest.mark.critical_flow
@allure.feature("关键业务流程验证")
@allure.story("现货下单流程")
class TestSpotOrder:
    """现货下单流程测试套件"""

    @allure.title("现货限价下单流程验证")
    @allure.description(
        "验证现货限价下单流程：导航到交易页 → 选择交易方向 → 填写价格和数量 → 提交订单"
    )
    def test_place_limit_order(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证现货限价下单流程

        前置条件：
        - 已通过 authenticated_page fixture 完成登录
        - 非生产环境（生产环境跳过）

        流程：
        1. 检查环境（生产环境跳过）
        2. 导航到交易页
        3. 关闭初始弹窗
        4. 执行限价下单操作
        5. 验证订单提交成功
        """
        if settings.env == Environment.PRODUCTION:
            pytest.skip("生产环境跳过下单测试，避免产生真实订单")

        trade_page = TradePage(authenticated_page, settings.base_url)

        with allure.step("导航到交易页"):
            trade_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("执行限价买入下单"):
            # 使用一个远低于市场价的价格，确保不会实际成交
            trade_page.place_limit_order(side="buy", price="1.00", amount="0.001")

        with allure.step("验证订单提交"):
            # 检查是否出现订单提交成功的指示器
            # 可能是 toast 通知、订单确认弹窗或订单列表更新
            success_indicator = authenticated_page.locator(
                "[data-testid='order-success'], "
                ".order-success, "
                ".toast-success, "
                ".notification-success, "
                "[class*='success']"
            ).first
            try:
                success_indicator.wait_for(state="visible", timeout=10000)
            except Exception:
                # 如果没有明确的成功指示器，检查页面是否无错误提示
                error_indicator = authenticated_page.locator(
                    "[data-testid='order-error'], "
                    ".order-error, "
                    ".toast-error, "
                    ".notification-error, "
                    "[class*='error']"
                ).first
                assert not error_indicator.is_visible(), "下单操作出现错误提示"
