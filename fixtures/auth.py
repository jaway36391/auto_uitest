"""登录态管理模块 - 封装认证相关的辅助函数

提供 TOTP 验证码生成、完整登录流程执行、以及通过浏览器存储注入认证 Token 等功能。
"""

import allure
import pyotp
from playwright.sync_api import Page

from config.settings import AppSettings
from pages.login_page import LoginPage


@allure.step("生成 TOTP 验证码")
def generate_totp_code(totp_secret: str) -> str:
    """根据 TOTP 密钥生成当前时间窗口的 6 位验证码

    Args:
        totp_secret: Base32 编码的 TOTP 密钥

    Returns:
        6 位数字验证码字符串
    """
    totp = pyotp.TOTP(totp_secret)
    return totp.now()


@allure.step("执行完整登录流程")
def perform_full_login(page: Page, settings: AppSettings) -> None:
    """执行完整的登录流程：邮箱密码 + TOTP 两步验证

    流程步骤：
    1. 导航到登录页面
    2. 填写邮箱和密码并提交
    3. 如果配置了 TOTP 密钥，生成验证码并完成两步验证

    Args:
        page: Playwright Page 实例
        settings: 应用配置（包含账号、密码、TOTP 密钥等）

    Raises:
        ValueError: 当测试账号或密码未配置时抛出
    """
    if not settings.test_username or not settings.test_password:
        raise ValueError("测试账号或密码未配置，请检查环境配置文件")

    login_page = LoginPage(page, settings.base_url)
    login_page.navigate()

    # 输入邮箱和密码
    login_page.login(settings.test_username, settings.test_password)

    # 如果配置了 TOTP 密钥，完成两步验证
    if settings.totp_secret:
        totp_code = generate_totp_code(settings.totp_secret)
        login_page.enter_totp(totp_code)

    # 等待登录完成
    page.wait_for_load_state("networkidle")


@allure.step("通过浏览器存储注入认证 Token")
def inject_auth_token(page: Page, settings: AppSettings) -> None:
    """通过 localStorage 注入认证 Token 实现快速认证

    适用于跳过登录 UI 流程，直接注入已有的认证 Token 到浏览器存储中。
    需要先导航到目标域名下的任意页面，才能操作该域名的 localStorage。

    Args:
        page: Playwright Page 实例
        settings: 应用配置（包含 auth_token）

    Raises:
        ValueError: 当 auth_token 未配置时抛出
    """
    if not settings.auth_token:
        raise ValueError("auth_token 未配置，无法注入认证状态")

    # 先导航到目标域名（确保 localStorage 可用）
    page.goto(settings.base_url, wait_until="domcontentloaded")

    # 注入 token 到 localStorage
    page.evaluate(
        """(token) => {
            localStorage.setItem('auth_token', token);
            localStorage.setItem('access_token', token);
        }""",
        settings.auth_token,
    )

    # 注入 token 到 cookie（部分系统通过 cookie 验证）
    page.context.add_cookies([
        {
            "name": "auth_token",
            "value": settings.auth_token,
            "domain": page.url.split("//")[1].split("/")[0],
            "path": "/",
        }
    ])

    # 刷新页面使 token 生效
    page.reload(wait_until="domcontentloaded")
