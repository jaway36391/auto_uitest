"""保存浏览器认证状态

使用方法：
    python3 scripts/save_auth_state.py

此脚本会打开一个有头浏览器窗口，你手动完成登录后，
按 Enter 键保存认证状态到 auth_state.json 文件。
后续测试可以直接加载此文件跳过登录流程。
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    print("=" * 60)
    print("认证状态保存工具")
    print("=" * 60)
    print()
    print("即将打开浏览器，请手动完成登录操作。")
    print("登录成功后，回到终端按 Enter 键保存认证状态。")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 导航到登录页
        page.goto("https://www.example.com/signin", wait_until="domcontentloaded")

        print("浏览器已打开，请完成登录...")
        print("登录成功后（看到账户页面），按 Enter 保存状态。")
        input("\n>>> 按 Enter 保存认证状态...")

        # 保存 storage state（包含 cookies + localStorage）
        state_path = Path("config/auth_state.json")
        state_path.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(state_path))

        # 额外保存 localStorage（storage_state 可能不包含）
        local_storage = page.evaluate("() => JSON.stringify(localStorage)")
        ls_path = Path("config/local_storage.json")
        ls_path.write_text(local_storage)

        print(f"\n✅ 认证状态已保存到: {state_path}")
        print(f"✅ localStorage 已保存到: {ls_path}")
        print(f"\n当前页面 URL: {page.url}")

        # 显示保存的 cookies 数量
        cookies = context.cookies()
        print(f"保存了 {len(cookies)} 个 cookies")
        for c in cookies[:10]:
            print(f"  - {c['name']}: {c['value'][:30]}...")

        browser.close()

    print("\n后续运行测试时将自动加载此认证状态。")


if __name__ == "__main__":
    main()
