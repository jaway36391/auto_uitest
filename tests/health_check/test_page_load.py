"""页面加载健康检查测试

验证交易所各关键页面能够正常加载，包括：
- HTTP 响应状态码为 2xx
- 页面在超时时间内加载完成
- 页面包含特征性元素或标题

使用参数化测试覆盖多个关键页面。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups


# 定义需要检测的关键页面
KEY_PAGES = [
    {
        "name": "首页",
        "path": "/",
        "characteristic_selector": "header, a[href*='flash'], a[href*='market']",
    },
    {
        "name": "市场行情页",
        "path": "/en/markets",
        "characteristic_selector": "header, a[href*='market'], main, section",
    },
    {
        "name": "Flash交易页",
        "path": "/en/flash",
        "characteristic_selector": "header, a[href*='flash'], main, section",
    },
    {
        "name": "费率页",
        "path": "/en/fees",
        "characteristic_selector": "main, .content, .page-content, article, section",
    },
]


@pytest.mark.health_check
@pytest.mark.prod_safe
@allure.feature("页面可用性检测")
@allure.story("页面加载")
class TestPageLoad:
    """页面加载健康检查测试套件"""

    @pytest.mark.parametrize(
        "page_info",
        KEY_PAGES,
        ids=[p["name"] for p in KEY_PAGES],
    )
    @allure.title("验证页面加载 - {page_info[name]}")
    @allure.description("验证页面能在超时时间内成功加载，HTTP 状态码为 2xx，且包含特征性元素")
    def test_page_loads_successfully(
        self, page: Page, settings: AppSettings, page_info: dict
    ) -> None:
        """验证关键页面能够正常加载

        检查项：
        1. HTTP 响应状态码为 2xx
        2. 页面在超时时间内加载完成
        3. 页面包含特征性元素
        """
        url = f"{settings.base_url.rstrip('/')}{page_info['path']}"

        with allure.step(f"导航到页面: {url}"):
            response = page.goto(url, wait_until="domcontentloaded", timeout=settings.timeout)

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(page)

        with allure.step("验证 HTTP 响应状态码为 2xx"):
            assert response is not None, f"页面 {url} 未返回响应"
            assert response.ok, (
                f"页面 {url} 返回非 2xx 状态码: {response.status}"
            )

        with allure.step("验证特征性元素存在"):
            characteristic = page.locator(page_info["characteristic_selector"]).first
            characteristic.wait_for(state="attached", timeout=15000)
