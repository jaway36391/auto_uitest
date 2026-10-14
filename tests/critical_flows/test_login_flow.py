"""登录流程测试

验证完整的登录流程：导航到登录页 → 输入凭证 → 提交 → TOTP 验证 → 验证登录成功。
记录流程执行耗时。
"""

import time

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.auth import generate_totp_code
from fixtures.environment import dismiss_initial_popups
from pages.login_page import LoginPage


@pytest.mark.critical_flow
@allure.feature("关键业务流程验证")
@allure.story("登录流程")
class TestLoginFlow:
    """登录流程测试套件"""

    @allure.title("完整登录流程验证")
    @allure.description(
        "验证完整登录流程：导航到登录页 → 输入邮箱密码 → 提交 → TOTP 验证 → 确认登录成功"
    )
    def test_full_login_flow(self, page: Page, settings: AppSettings) -> None:
        """验证完整的用户登录流程

        前置条件：
        - 配置了有效的测试账号（test_username, test_password）
        - 如启用 TOTP，需配置 totp_secret

        流程：
        1. 导航到登录页
        2. 关闭初始弹窗
        3. 输入邮箱和密码
        4. 提交登录表单
        5. 输入 TOTP 验证码（如配置）
        6. 验证登录成功
        7. 记录流程执行耗时
        """
        if not settings.test_username or not settings.test_password:
            pytest.skip("测试账号未配置，跳过登录流程测试")

        login_page = LoginPage(page, settings.base_url)
        flow_start = time.time()

        with allure.step("导航到登录页"):
            login_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(page)

        with allure.step("输入邮箱和密码并提交"):
            login_page.login(settings.test_username, settings.test_password)

        with allure.step("完成 TOTP 两步验证"):
            if settings.totp_secret:
                totp_code = generate_totp_code(settings.totp_secret)
                login_page.enter_totp(totp_code)
            else:
                allure.attach(
                    "未配置 TOTP 密钥，跳过两步验证",
                    name="totp_info",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step("验证登录成功"):
            assert login_page.is_logged_in(), "登录流程完成后未检测到已登录状态"

        flow_duration = time.time() - flow_start
        allure.attach(
            f"登录流程总耗时: {flow_duration:.2f}s",
            name="flow_duration",
            attachment_type=allure.attachment_type.TEXT,
        )
