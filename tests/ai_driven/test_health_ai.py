"""页面健康检查 AI 驱动测试

使用 browser-use + LLM 自动验证页面可用性，
无需硬编码选择器，AI 自主判断页面是否正常加载。
"""

import allure
import pytest

from ai_agent.agent import PatrolResult, run_patrol_task


# 需要巡检的页面列表
PATROL_PAGES = [
    {
        "name": "首页",
        "url": "https://www.example.com/en",
        "checks": "确认页面有导航栏、有交易相关链接（如 Flash Trade、Markets）、无错误页面",
    },
    {
        "name": "市场行情页",
        "url": "https://www.example.com/en/markets",
        "checks": "确认页面展示了加密货币行情列表（币种名称、价格数据）、有搜索或筛选功能",
    },
    {
        "name": "Flash交易页",
        "url": "https://www.example.com/en/flash",
        "checks": "确认页面有交易相关元素（如币种选择、价格展示、交易按钮）",
    },
    {
        "name": "费率页",
        "url": "https://www.example.com/en/fees",
        "checks": "确认页面展示了费率信息（如交易费率表格或说明文字）",
    },
]


@pytest.mark.ai_driven
@pytest.mark.prod_safe
@allure.feature("页面健康检查 - AI 驱动")
class TestHealthAI:
    """页面健康检查 AI 驱动测试套件"""

    @pytest.mark.parametrize(
        "page_info",
        PATROL_PAGES,
        ids=[p["name"] for p in PATROL_PAGES],
    )
    @allure.title("AI 健康检查: {page_info[name]}")
    @pytest.mark.asyncio
    async def test_page_health(self, page_info: dict) -> None:
        """AI 驱动的页面健康检查"""
        result: PatrolResult = await run_patrol_task(
            task=(
                f"1. 导航到 {page_info['url']}\n"
                f"2. 等待页面完全加载\n"
                f"3. 验证页面正常展示（非错误页、非空白页）\n"
                f"4. {page_info['checks']}\n"
                f"5. 如果页面有弹窗（如 'I Understand' 按钮），先关闭它\n"
                f"6. 返回页面健康状态总结：页面是否正常可用"
            ),
        )

        allure.attach(
            f"页面: {page_info['name']}\n"
            f"URL: {page_info['url']}\n"
            f"结果: {'✅ 正常' if result.success else '❌ 异常'}\n"
            f"摘要: {result.summary}",
            name="health_check_result",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert result.success, f"页面 {page_info['name']} 健康检查失败: {result.error}"
