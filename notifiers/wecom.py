"""企业微信 Webhook 通知器

实现企业微信机器人 Webhook 的 markdown 格式消息发送。
"""

from notifiers.base import BaseNotifier, TestResult


class WeComNotifier(BaseNotifier):
    """企业微信 Webhook 通知器

    生成符合企业微信机器人 Webhook 接口规范的 markdown 消息。
    消息包含环境名称、执行时间、通过/失败统计和失败用例列表。
    """

    def format_message(self, result: TestResult) -> dict:
        """格式化企业微信 markdown 消息

        Args:
            result: 测试结果摘要

        Returns:
            符合企业微信 Webhook 接口的消息字典
        """
        failed_list = "\n".join(
            f"  - {case}" for case in result.failed_cases[:10]
        )

        content = (
            f"## 🚨 交易所UI巡检告警\n\n"
            f"**环境**: {result.environment}\n"
            f"**执行时间**: {result.duration_seconds:.1f}s\n"
            f"**结果**: {result.passed}/{result.total} 通过, "
            f"**{result.failed} 失败**\n\n"
            f"**失败用例**:\n{failed_list}\n"
        )

        if result.report_url:
            content += f"\n[查看完整报告]({result.report_url})"

        return {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }
