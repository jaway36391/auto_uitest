"""配置管理模块 - 基于 pydantic-settings 的应用配置模型"""

from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """目标运行环境枚举"""

    PRODUCTION = "production"
    STAGING = "staging"


class AppSettings(BaseSettings):
    """应用全局配置

    通过环境变量（PATROL_ 前缀）或 .env 文件加载配置。
    支持多环境切换，默认使用 staging 环境。
    """

    # 基础配置
    env: Environment = Field(default=Environment.STAGING, description="目标环境")
    base_url: str = Field(default="https://www.example.com", description="目标环境基础URL")
    timeout: int = Field(default=30000, description="全局超时时间(ms)")
    headless: bool = Field(default=True, description="是否无头模式")
    slow_mo: int = Field(default=0, description="操作延迟(ms)，调试用")

    # 测试账号
    test_username: Optional[str] = Field(default=None, description="测试账号")
    test_password: Optional[str] = Field(default=None, description="测试密码")
    totp_secret: Optional[str] = Field(default=None, description="TOTP密钥（用于两步验证）")
    device_id: Optional[str] = Field(default=None, description="设备ID（用于设备认证）")
    auth_token: Optional[str] = Field(default=None, description="认证Token（用于API认证）")

    # 报告配置
    report_dir: str = Field(default="reports", description="报告输出目录")
    screenshot_on_failure: bool = Field(default=True, description="失败时截图")

    # 通知配置
    wecom_webhook_url: Optional[str] = Field(default=None, description="企业微信Webhook")
    dingtalk_webhook_url: Optional[str] = Field(default=None, description="钉钉Webhook")
    lark_webhook_url: Optional[str] = Field(default=None, description="Lark/飞书Webhook")
    alert_on_failure: bool = Field(default=True, description="失败时发送告警")

    model_config = {
        "env_file": ".env",
        "env_prefix": "PATROL_",
        "case_sensitive": False,
    }


def get_settings(env: Optional[str] = None) -> AppSettings:
    """根据环境名加载对应配置文件

    Args:
        env: 环境名称（如 "production"、"staging"）。
             如果为 None，则使用默认 .env 文件。

    Returns:
        加载了对应环境配置的 AppSettings 实例。
    """
    env_file = f"config/environments/.env.{env}" if env else ".env"
    return AppSettings(_env_file=env_file)
