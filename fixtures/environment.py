"""环境初始化模块 - 封装环境准备相关的辅助函数

处理首次访问时的弹窗关闭、语言/地区偏好设置等环境初始化操作。
部分交易所首次访问时会显示合规 Notice 弹窗，需要点击 "I Understand" 关闭。
"""

import allure
from playwright.sync_api import Page


@allure.step("关闭初始弹窗/通知")
def dismiss_initial_popups(page: Page) -> None:
    """关闭首次访问时出现的弹窗和通知

    部分交易所在首次访问时会显示合规提示 Notice 弹窗，
    需要点击 "I Understand" 按钮将其关闭后才能正常操作页面。

    Args:
        page: Playwright Page 实例
    """
    # 合规提示 Notice 弹窗 - 点击 "I Understand" 关闭
    i_understand_button = page.locator(
        "button:has-text('I Understand'), "
        "[data-testid='notice-dismiss'], "
        "button:has-text('I understand')"
    ).first

    try:
        i_understand_button.wait_for(state="visible", timeout=5000)
        i_understand_button.click()
        # 等待弹窗消失
        i_understand_button.wait_for(state="hidden", timeout=3000)
    except Exception:
        # 弹窗可能不出现（非首次访问或已关闭），忽略即可
        pass

    # 处理其他可能的通知弹窗（如 cookie 同意等）
    cookie_dismiss = page.locator(
        "button:has-text('Accept'), "
        "button:has-text('Got it'), "
        "[data-testid='cookie-accept']"
    ).first

    try:
        cookie_dismiss.wait_for(state="visible", timeout=2000)
        cookie_dismiss.click()
    except Exception:
        pass


@allure.step("设置语言/地区偏好")
def set_locale_preferences(page: Page, locale: str = "en") -> None:
    """设置页面的语言和地区偏好

    通过 localStorage 注入语言偏好设置，避免每次测试都需要手动切换语言。
    支持的语言代码：en（英文）、zh-CN（简体中文）、zh-TW（繁体中文）等。

    Args:
        page: Playwright Page 实例
        locale: 语言代码，默认为 "en"（英文）
    """
    page.evaluate(
        """(locale) => {
            localStorage.setItem('locale', locale);
            localStorage.setItem('language', locale);
            localStorage.setItem('i18n_lang', locale);
        }""",
        locale,
    )
