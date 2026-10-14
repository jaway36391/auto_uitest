"""从已登录的 Chrome 浏览器导出目标站点 cookies

使用方法：
    1. 确保你已在 Chrome 中登录了 www.example.com
    2. 完全关闭 Chrome（重要！Chrome 运行时数据库会被锁定）
    3. 运行: python3 scripts/export_cookies_from_chrome.py
    
这会从 Chrome 的 cookie 数据库中提取 example.com 的 cookies，
保存为 Playwright 可用的 storage state 格式。
"""

import json
import sqlite3
import shutil
import tempfile
from pathlib import Path


def get_chrome_cookies_db_path() -> Path:
    """获取 macOS 上 Chrome 的 Cookies 数据库路径"""
    return Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"


def export_cookies():
    db_path = get_chrome_cookies_db_path()
    
    if not db_path.exists():
        print(f"❌ Chrome Cookies 数据库不存在: {db_path}")
        print("请确认 Chrome 已安装且使用过。")
        return

    # 复制数据库到临时文件（避免锁定问题）
    tmp_dir = tempfile.mkdtemp()
    tmp_db = Path(tmp_dir) / "Cookies"
    shutil.copy2(db_path, tmp_db)

    conn = sqlite3.connect(str(tmp_db))
    cursor = conn.cursor()

    # 查询 example.com 相关的 cookies
    cursor.execute("""
        SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
        FROM cookies 
        WHERE host_key LIKE '%example.com%'
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ 未找到 example.com 的 cookies。")
        print("请确认：")
        print("  1. 你已在 Chrome 中登录了 www.example.com")
        print("  2. Chrome 已完全关闭后再运行此脚本")
        return

    # 转换为 Playwright storage state 格式
    cookies = []
    for name, value, domain, path, expires, secure, httponly in rows:
        if not value:  # Chrome 80+ 加密了 cookies，value 可能为空
            continue
        cookies.append({
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
            "expires": expires / 1000000 - 11644473600 if expires > 0 else -1,
            "httpOnly": bool(httponly),
            "secure": bool(secure),
            "sameSite": "Lax",
        })

    state = {
        "cookies": cookies,
        "origins": []
    }

    output_path = Path("config/auth_state.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, indent=2))

    print(f"✅ 导出了 {len(cookies)} 个 example.com cookies")
    print(f"✅ 保存到: {output_path}")
    for c in cookies[:10]:
        print(f"   - {c['name']}: {c['value'][:30]}...")

    # 清理临时文件
    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    export_cookies()
