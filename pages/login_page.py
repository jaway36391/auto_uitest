"""登录页面 Page Object - 示例交易所登录页面交互封装

本框架针对分步登录流程：
1. 输入邮箱 → 点击 Continue
2. 输入密码 → 点击 Submit
3. 输入 TOTP 验证码（如启用）

选择器基于通用交易所登录页 DOM 结构推断，可能需要根据实际页面调整。
"""

from typing import List

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage, CriticalElement


class LoginPage(BasePage):
    """示例交易所 登录页面 Page Object

    URL: https://www.example.com/en/signin
    功能：用户邮箱/密码分步登录 + TOTP 两步验证
    """

    URL_PATH: str = "/en/signin"
    PAGE_TITLE: str = ""
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector="input[placeholder='Enter your email address'], input[placeholder*='email' i]",
            name="邮箱输入框",
            description="用户登录邮箱输入字段",
        ),
        CriticalElement(
            selector="button[type='submit']",
            name="提交按钮",
            description="Continue/Submit 按钮",
        ),
    ]

    # --- 元素定位器（基于通用登录页 DOM 结构推断） ---
    _EMAIL_INPUT = "input[placeholder='Enter your email address'], input[placeholder*='email' i]"
    _PASSWORD_INPUT = "input[type='password'], input[placeholder*='password' i]"
    _SUBMIT_BUTTON = "button[type='submit']"
    _TOTP_INPUT = "input[placeholder*='code' i], input[placeholder*='verification' i], input[type='tel'], input[inputmode='numeric']"
    # 登录成功后的标识元素
    _USER_INDICATOR = "header a[href*='account'], header a[href*='wallet'], header a[href*='asset']"

    @allure.step("执行登录操作: 用户名={username}")
    def login(self, username: str, password: str) -> None:
        """执行分步登录流程

        登录分两步：
        1. 输入邮箱 → 点击提交
        2. 输入密码 → 点击提交

        Args:
            username: 用户邮箱地址
            password: 用户密码
        """
        # Step 1: 输入邮箱
        email_input = self.page.locator(self._EMAIL_INPUT).first
        email_input.wait_for(state="visible", timeout=15000)
        email_input.fill(username)
        self.page.locator(self._SUBMIT_BUTTON).first.click()
        self.page.wait_for_timeout(3000)

        # Step 2: 输入密码
        password_input = self.page.locator(self._PASSWORD_INPUT).first
        password_input.wait_for(state="visible", timeout=15000)
        password_input.fill(password)
        self.page.locator(self._SUBMIT_BUTTON).first.click()
        self.page.wait_for_timeout(3000)

    @allure.step("输入 TOTP 验证码")
    def enter_totp(self, totp_code: str) -> None:
        """输入 TOTP 两步验证码

        Args:
            totp_code: 6位 TOTP 动态验证码
        """
        totp_input = self.page.locator(self._TOTP_INPUT).first
        totp_input.wait_for(state="visible", timeout=15000)
        totp_input.fill(totp_code)
        # 部分实现输入6位后自动提交，否则点击提交按钮
        self.page.wait_for_timeout(2000)
        submit_btn = self.page.locator(self._SUBMIT_BUTTON).first
        if submit_btn.is_visible():
            submit_btn.click()
        self.page.wait_for_timeout(5000)

    @allure.step("验证登录状态")
    def is_logged_in(self) -> bool:
        """检测当前是否处于已登录状态

        Returns:
            True 表示已登录，False 表示未登录
        """
        try:
            # 检查是否有登录后才可见的导航链接（如 account/wallet/asset）
            user_indicator = self.page.locator(self._USER_INDICATOR).first
            user_indicator.wait_for(state="visible", timeout=15000)
            return True
        except Exception:
            # 备选：检查 URL 是否已离开登录页
            return "/signin" not in self.page.url
