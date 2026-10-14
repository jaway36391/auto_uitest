"""Fixtures 模块 - 通用测试前置条件封装

提供登录态管理和环境初始化相关的辅助函数。
"""

from fixtures.auth import generate_totp_code, inject_auth_token, perform_full_login
from fixtures.environment import dismiss_initial_popups, set_locale_preferences

__all__ = [
    "generate_totp_code",
    "inject_auth_token",
    "perform_full_login",
    "dismiss_initial_popups",
    "set_locale_preferences",
]
