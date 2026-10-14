"""资产页 UI 元素存在性验证测试

使用 AssetPage Page Object 验证资产页所有关键 UI 元素是否可见。
资产页需要登录态，使用 authenticated_page fixture。
失败时记录缺失元素的选择器信息并截图。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups
from pages.asset_page import AssetPage


@pytest.mark.ui_elements
@pytest.mark.prod_safe
@allure.feature("UI元素存在性验证")
@allure.story("资产页元素验证")
class TestAssetElements:
    """资产页关键 UI 元素验证测试套件"""

    @allure.title("验证资产页关键元素可见")
    @allure.description("验证资产页所有 CRITICAL_ELEMENTS 定义的关键 UI 元素均可见（需登录态）")
    def test_asset_critical_elements(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证资产页所有关键 UI 元素存在且可见

        前置条件：已通过 authenticated_page fixture 完成登录

        流程：
        1. 导航到资产页
        2. 关闭初始弹窗
        3. 调用 verify_critical_elements() 验证所有关键元素
        4. 如有缺失元素，记录详情并截图
        """
        asset_page = AssetPage(authenticated_page, settings.base_url)

        with allure.step("导航到资产页"):
            asset_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证关键元素"):
            missing_elements = asset_page.verify_critical_elements()

        if missing_elements:
            missing_info = "\n".join(
                f"- {elem.name}: selector='{elem.selector}' ({elem.description})"
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
                name="asset_page_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        assert not missing_elements, (
            f"资产页缺失 {len(missing_elements)} 个关键元素: "
            f"{', '.join(e.name for e in missing_elements)}"
        )
