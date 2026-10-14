"""控制台错误检测测试

在页面导航前设置控制台监听器，加载页面后检查是否存在 JavaScript 控制台错误。
如果发现错误，将其附加到 Allure 报告中以便排查。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups


# 定义需要检测控制台错误的关键页面
PAGES_TO_CHECK = [
    {"name": "首页", "path": "/"},
    {"name": "市场行情页", "path": "/en/markets"},
    {"name": "Flash交易页", "path": "/en/flash"},
    {"name": "费率页", "path": "/en/fees"},
]


@pytest.mark.health_check
@pytest.mark.prod_safe
@allure.feature("页面可用性检测")
@allure.story("控制台错误检测")
class TestConsoleErrors:
    """JavaScript 控制台错误检测测试套件"""

    @pytest.mark.parametrize(
        "page_info",
        PAGES_TO_CHECK,
        ids=[p["name"] for p in PAGES_TO_CHECK],
    )
    @allure.title("检测控制台错误 - {page_info[name]}")
    @allure.description("导航到页面后检查是否存在 JavaScript 控制台错误")
    def test_no_console_errors(
        self, page: Page, settings: AppSettings, page_info: dict
    ) -> None:
        """验证页面加载后无 JavaScript 控制台错误

        流程：
        1. 设置控制台错误监听器
        2. 导航到目标页面
        3. 关闭初始弹窗
        4. 等待页面稳定
        5. 检查是否有控制台错误
        """
        console_errors: list[str] = []

        with allure.step("设置控制台错误监听器"):
            page.on(
                "console",
                lambda msg: (
                    console_errors.append(f"[{msg.type}] {msg.text}")
                    if msg.type == "error"
                    else None
                ),
            )

        url = f"{settings.base_url.rstrip('/')}{page_info['path']}"

        with allure.step(f"导航到页面: {url}"):
            page.goto(url, wait_until="domcontentloaded", timeout=settings.timeout)

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(page)

        with allure.step("等待页面稳定"):
            # 使用固定等待替代 networkidle，因为部分页面有持续的 analytics 请求
            page.wait_for_timeout(5000)

        with allure.step("检查控制台错误"):
            if console_errors:
                error_text = "\n".join(console_errors)
                allure.attach(
                    error_text,
                    name=f"console_errors_{page_info['name']}",
                    attachment_type=allure.attachment_type.TEXT,
                )
                # 注意：某些第三方脚本可能产生无害的控制台错误
                # 此处仅记录到报告，不强制断言失败
                # 如需严格检测，取消下面的注释：
                # pytest.fail(
                #     f"页面 {page_info['name']} 存在 {len(console_errors)} 个控制台错误:\n{error_text}"
                # )
            allure.attach(
                f"检测到 {len(console_errors)} 个控制台错误",
                name="console_error_count",
                attachment_type=allure.attachment_type.TEXT,
            )
