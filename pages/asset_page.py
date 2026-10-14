"""资产页面 Page Object - 示例交易所钱包/资产页面交互封装

针对示例交易所 (www.example.com) 资产管理页面，定义关键 UI 元素和页面验证逻辑。
资产页面包含余额展示、充值/提现入口等核心功能。

注意：CSS 选择器基于通用交易所 UI 模式推断，可能需要根据实际页面 DOM 结构调整。
"""

from typing import List

from pages.base_page import BasePage, CriticalElement


class AssetPage(BasePage):
    """示例交易所 资产/钱包页面 Page Object

    URL: https://www.example.com/en/wallet 或类似路径
    功能：展示用户资产余额、充值/提现操作入口
    """

    URL_PATH: str = "/en/wallet"
    PAGE_TITLE: str = ""  # 资产页标题可能动态变化
    CRITICAL_ELEMENTS: List[CriticalElement] = [
        CriticalElement(
            selector=(
                "[data-testid='total-balance'], .total-balance, "
                ".balance-overview, .portfolio-value, .asset-total"
            ),
            name="总资产余额",
            description="用户总资产余额展示区域",
        ),
        CriticalElement(
            selector=(
                "[data-testid='asset-list'], .asset-list, "
                ".coin-list, .balance-table, table.assets"
            ),
            name="资产列表",
            description="各币种资产明细列表",
        ),
        CriticalElement(
            selector=(
                "[data-testid='deposit-button'], button.deposit, "
                "a[href*='deposit'], .deposit-btn"
            ),
            name="充值按钮",
            description="跳转到充值页面的操作按钮",
        ),
        CriticalElement(
            selector=(
                "[data-testid='withdraw-button'], button.withdraw, "
                "a[href*='withdraw'], .withdraw-btn"
            ),
            name="提现按钮",
            description="跳转到提现页面的操作按钮",
        ),
    ]
