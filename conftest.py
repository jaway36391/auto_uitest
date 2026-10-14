"""全局 pytest 配置与 fixtures

提供环境配置加载、登录态管理、测试计时、失败截图等通用 fixtures。
通过 --env 命令行参数切换目标环境。
测试会话结束后根据配置发送告警通知。
"""

import logging
import time
from typing import Generator

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings, get_settings
from fixtures.auth import perform_full_login
from notifiers.base import TestResult
from notifiers.dingtalk import DingTalkNotifier
from notifiers.lark import LarkNotifier
from notifiers.wecom import WeComNotifier

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    """添加自定义命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="目标环境: production, staging",
    )


@pytest.fixture(scope="session")
def settings(request: pytest.FixtureRequest) -> AppSettings:
    """加载环境配置（session 级别，整个测试会话共享）"""
    env = request.config.getoption("--env")
    return get_settings(env)


@pytest.fixture(scope="session")
def base_url(settings: AppSettings) -> str:
    """提供基础 URL，覆盖 pytest-playwright 的 base_url fixture"""
    return settings.base_url


@pytest.fixture
def authenticated_page(page: Page, settings: AppSettings) -> Page:
    """提供已登录的页面实例

    通过 cookie 注入 + 非无头模式绕过 Cloudflare 检测。
    需要在 .env 中设置 PATROL_HEADLESS=false。
    """
    from pathlib import Path
    from fixtures.environment import dismiss_initial_popups
    import json

    auth_state_path = Path("config/auth_state.json")
    if not auth_state_path.exists():
        pytest.skip("认证状态文件不存在，跳过需要登录的测试")

    state = json.loads(auth_state_path.read_text())
    cookies = state.get("cookies", [])
    if not cookies:
        pytest.skip("认证 cookies 为空，跳过需要登录的测试")

    # 注入 cookies
    page.context.add_cookies(cookies)

    # 直接导航到需要认证的页面（让 Cloudflare 签发 __cf_bm）
    page.goto(settings.base_url + "/en", wait_until="domcontentloaded", timeout=settings.timeout)
    page.wait_for_timeout(3000)
    dismiss_initial_popups(page)
    return page


@pytest.fixture(autouse=True)
def test_timing(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """记录每个测试的执行耗时（autouse，自动应用于所有测试）"""
    start = time.time()
    yield
    duration = time.time() - start
    request.node.user_properties.append(("duration", f"{duration:.3f}s"))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """测试失败时自动截图并附加到 Allure 报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page: Page | None = item.funcargs.get("page") or item.funcargs.get("authenticated_page")
        if page and not page.is_closed():
            try:
                screenshot = page.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name=f"failure_screenshot_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                # 截图失败不应影响测试报告流程
                pass


# ---- 测试结果收集与告警通知 ----

# 用于收集测试会话中的结果
_session_start_time: float = 0.0
_test_results: dict = {}


def pytest_sessionstart(session: pytest.Session) -> None:
    """记录测试会话开始时间"""
    global _session_start_time
    _session_start_time = time.time()


@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """收集每个测试用例的执行结果（仅记录 call 阶段）"""
    if report.when == "call":
        _test_results[report.nodeid] = report


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """测试会话结束后发送告警通知

    仅在以下条件同时满足时发送通知：
    1. alert_on_failure 配置为 True
    2. 存在失败的测试用例
    3. 至少配置了一个 webhook URL
    """
    env_name = session.config.getoption("--env", default="staging")
    settings = get_settings(env_name)

    if not settings.alert_on_failure:
        return

    # 收集失败用例
    failed_cases = [
        nodeid for nodeid, report in _test_results.items()
        if report.failed
    ]

    if not failed_cases:
        return

    total = len(_test_results)
    failed = len(failed_cases)
    passed = total - failed
    duration = time.time() - _session_start_time

    test_result = TestResult(
        environment=settings.env.value,
        total=total,
        passed=passed,
        failed=failed,
        duration_seconds=duration,
        failed_cases=failed_cases,
    )

    # 发送到已配置的通知渠道
    if settings.wecom_webhook_url:
        notifier = WeComNotifier(settings.wecom_webhook_url)
        try:
            notifier.send(test_result)
        finally:
            notifier.close()

    if settings.dingtalk_webhook_url:
        notifier = DingTalkNotifier(settings.dingtalk_webhook_url)
        try:
            notifier.send(test_result)
        finally:
            notifier.close()

    if settings.lark_webhook_url:
        notifier = LarkNotifier(settings.lark_webhook_url)
        try:
            notifier.send(test_result)
        finally:
            notifier.close()
