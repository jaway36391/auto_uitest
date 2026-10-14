#!/bin/bash
# 保存目标交易所认证状态
#
# 使用方法：
# 1. 先关闭所有 Chrome 窗口
# 2. 运行此脚本: bash scripts/save_auth_state.sh
# 3. 在打开的 Chrome 中手动登录目标交易所
# 4. 登录成功后关闭浏览器窗口
#
# 脚本会使用你本地的 Chrome（不是 Playwright 的 Chromium），
# 这样可以正常显示 GUI 窗口。

echo "=== 认证状态保存工具 ==="
echo ""
echo "即将使用本地 Chrome 打开登录页..."
echo "请在浏览器中完成登录，然后关闭浏览器窗口。"
echo ""

# 使用 Playwright 的 channel 参数启动本地 Chrome
python3 -c "
from playwright.sync_api import sync_playwright
from pathlib import Path

with sync_playwright() as p:
    # 使用本地安装的 Chrome 而不是 Playwright 的 Chromium
    browser = p.chromium.launch(
        headless=False,
        channel='chrome',  # 使用本地 Chrome
    )
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.example.com/signin', wait_until='domcontentloaded')
    
    print()
    print('浏览器已打开！请完成登录操作。')
    print('登录成功后，回到终端按 Enter 键。')
    input('\n>>> 按 Enter 保存认证状态...')
    
    # 保存状态
    output = Path('config/auth_state.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(output))
    
    print(f'\n✅ 认证状态已保存到: {output}')
    print(f'当前 URL: {page.url}')
    
    cookies = context.cookies()
    print(f'保存了 {len(cookies)} 个 cookies')
    
    browser.close()
"

echo ""
echo "完成！现在可以运行测试了："
echo "  python3 -m pytest tests/critical_flows/test_fiat_deposit.py --env=production -v"
