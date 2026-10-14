"""法币模块 AI 驱动测试

使用 browser-use + LLM 以自然语言描述测试步骤，
AI Agent 自动执行浏览器操作并验证结果。

无需维护 CSS 选择器，测试用例用中文描述即可。
"""

import allure
import pytest

from ai_agent.agent import PatrolResult, run_patrol_task


@pytest.mark.ai_driven
@pytest.mark.prod_safe
@allure.feature("法币业务 - AI 驱动测试")
class TestFiatAI:
    """法币模块 AI 驱动测试套件"""

    @allure.title("AI: 法币入金页面 - 查看银行VA信息")
    @allure.description("使用 AI Agent 导航到法币入金页面，查看并验证银行VA信息展示")
    @pytest.mark.asyncio
    async def test_view_bank_va_info(self, ai_context) -> None:
        """验证法币入金页面银行VA信息展示"""
        result: PatrolResult = await run_patrol_task(
            task=(
                "1. 导航到 https://www.example.com/en/account/deposit/fiat\n"
                "2. 等待页面加载完成\n"
                "3. 确认页面显示了 'Fiat Deposit' 标题\n"
                "4. 确认页面显示了 'USD' 或 'US Dollar' 币种选项\n"
                "5. 确认页面有 'Next' 按钮\n"
                "6. 点击 'Next' 按钮\n"
                "7. 查看是否展示了银行账户信息（如银行名称、账户号码）\n"
                "8. 返回页面上展示的银行VA信息内容摘要"
            ),
            browser_context=ai_context,
        )

        _attach_result(result)
        assert result.success, f"AI 巡检失败: {result.error}"

    @allure.title("AI: 法币出金页面 - 验证银行卡管理入口")
    @allure.description("使用 AI Agent 导航到法币出金页面，验证新增银行卡入口可用")
    @pytest.mark.asyncio
    async def test_withdraw_bank_card_entry(self, ai_context) -> None:
        """验证法币出金页面银行卡管理入口"""
        result: PatrolResult = await run_patrol_task(
            task=(
                "1. 导航到 https://www.example.com/en/account/withdraw/fiat\n"
                "2. 等待页面加载完成\n"
                "3. 确认页面显示了 'Fiat Withdraw' 或提现相关标题\n"
                "4. 查找并确认页面有 '新增银行卡' 或 'Add' 银行卡的按钮\n"
                "5. 确认银行卡列表区域存在（可能有已绑定的卡或空状态提示）\n"
                "6. 返回页面上展示的出金相关元素摘要（不要点击提交任何操作）"
            ),
            browser_context=ai_context,
        )

        _attach_result(result)
        assert result.success, f"AI 巡检失败: {result.error}"

    @allure.title("AI: 交易记录页面 - 查看历史记录")
    @allure.description("使用 AI Agent 导航到交易记录页面，验证历史记录列表展示")
    @pytest.mark.asyncio
    async def test_transaction_history(self, ai_context) -> None:
        """验证交易记录页面展示"""
        result: PatrolResult = await run_patrol_task(
            task=(
                "1. 导航到 https://www.example.com/en/asset/deposit_withdraw_records\n"
                "2. 等待页面加载完成\n"
                "3. 确认页面显示了交易记录相关标题（如 'Records', 'History' 等）\n"
                "4. 确认页面有交易记录列表或空状态提示\n"
                "5. 如果有筛选器/标签页，确认它们可见\n"
                "6. 返回页面上展示的交易记录概要信息"
            ),
            browser_context=ai_context,
        )

        _attach_result(result)
        assert result.success, f"AI 巡检失败: {result.error}"


def _attach_result(result: PatrolResult) -> None:
    """将 AI 执行结果附加到 Allure 报告"""
    allure.attach(
        f"任务: {result.task}\n\n"
        f"成功: {result.success}\n"
        f"步骤数: {result.steps_taken}\n"
        f"摘要: {result.summary}\n"
        f"错误: {result.error or '无'}",
        name="ai_patrol_result",
        attachment_type=allure.attachment_type.TEXT,
    )
