"""钉钉 Webhook 通知器

实现钉钉机器人 Webhook 的 markdown 格式消息发送。
"""

from notifiers.base import BaseNotifier, TestResult


class DingTalkNotifier(BaseNotifier):
    """钉钉 Webhook 通知器

    生成符合钉钉机器人 Webhook 接口规范的 markdown 消息。
    消息包含环境名称、执行时间、通过/失败统计和失败用例列表。
    """

    def format_message(self, result: TestResult) -> dict:
        """格式化钉钉 markdown 消息

        Args:
            result: 测试结果摘要

        Returns:
            符合钉钉 Webhook 接口的消息字典
        """
        failed_list = "\n".join(
            f"  - {case}" for case in result.failed_cases[:10]
        )

        text = (
            f"## 🚨 交易所UI巡检告警\n\n"
            f"**环境**: {result.environment}\n\n"
            f"**执行时间**: {result.duration_seconds:.1f}s\n\n"
            f"**结果**: {result.passed}/{result.total} 通过, "
            f"**{result.failed} 失败**\n\n"
            f"**失败用例**:\n\n{failed_list}\n"
        )

        if result.report_url:
            text += f"\n[查看完整报告]({result.report_url})"

        return {
            "msgtype": "markdown",
            "markdown": {
                "title": "🚨 交易所UI巡检告警",
                "text": text,
            },
        }
