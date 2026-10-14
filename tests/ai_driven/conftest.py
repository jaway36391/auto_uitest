"""AI 驱动测试的 fixtures

提供带认证 cookies 的 Playwright 浏览器上下文给 browser-use Agent。
"""

import json
from pathlib import Path

import pytest
from playwright.async_api import async_playwright, BrowserContext


@pytest.fixture
async def ai_context() -> BrowserContext:
    """提供带认证 cookies 的异步浏览器上下文

    browser-use 使用异步 Playwright，因此这里提供异步上下文。
    从 config/auth_state.json 加载 cookies 注入。
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # 加载认证 cookies
        auth_state_path = Path("config/auth_state.json")
        if auth_state_path.exists():
            state = json.loads(auth_state_path.read_text())
            cookies = state.get("cookies", [])
            if cookies:
                await context.add_cookies(cookies)

        yield context

        await context.close()
        await browser.close()
