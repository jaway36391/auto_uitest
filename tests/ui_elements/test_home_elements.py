"""首页 UI 元素存在性验证测试

使用 HomePage Page Object 验证首页所有关键 UI 元素是否可见。
失败时记录缺失元素的选择器信息并截图。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups
from pages.home_page import HomePage


@pytest.mark.ui_elements
@pytest.mark.prod_safe
@allure.feature("UI元素存在性验证")
@allure.story("首页元素验证")
class TestHomeElements:
    """首页关键 UI 元素验证测试套件"""

    @allure.title("验证首页关键元素可见")
    @allure.description("验证首页所有 CRITICAL_ELEMENTS 定义的关键 UI 元素均可见")
    def test_home_critical_elements(self, page: Page, settings: AppSettings) -> None:
        """验证首页所有关键 UI 元素存在且可见

        流程：
        1. 导航到首页
        2. 关闭初始弹窗
        3. 调用 verify_critical_elements() 验证所有关键元素
        4. 如有缺失元素，记录详情并截图
        """
        home_page = HomePage(page, settings.base_url)

        with allure.step("导航到首页"):
            home_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(page)

        with allure.step("验证关键元素"):
            missing_elements = home_page.verify_critical_elements()

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
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="home_page_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        assert not missing_elements, (
            f"首页缺失 {len(missing_elements)} 个关键元素: "
            f"{', '.join(e.name for e in missing_elements)}"
        )
