"""Lark（飞书）Webhook 通知器

实现 Lark 机器人 Webhook 的富文本消息发送。
"""

from notifiers.base import BaseNotifier, TestResult


class LarkNotifier(BaseNotifier):
    """Lark（飞书）Webhook 通知器

    生成符合 Lark 机器人 Webhook 接口规范的富文本消息。
    消息包含环境名称、执行时间、通过/失败统计和失败用例列表。
    """

    def format_message(self, result: TestResult) -> dict:
        """格式化 Lark 富文本消息

        Args:
            result: 测试结果摘要

        Returns:
            符合 Lark Webhook 接口的消息字典
        """
        failed_list = "\n".join(
            f"  • {case}" for case in result.failed_cases[:10]
        )

        content = (
            f"🚨 交易所UI巡检告警\n\n"
            f"环境: {result.environment}\n"
            f"执行时间: {result.duration_seconds:.1f}s\n"
            f"结果: {result.passed}/{result.total} 通过, "
            f"{result.failed} 失败\n\n"
            f"失败用例:\n{failed_list}"
        )

        if result.report_url:
            content += f"\n\n查看完整报告: {result.report_url}"

        return {
            "msg_type": "text",
            "content": {"text": content},
        }
