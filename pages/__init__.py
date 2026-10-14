"""页面对象层 - Page Object Model 实现

导出所有 Page Object 类，供测试用例和 fixtures 使用。
"""

from pages.asset_page import AssetPage
from pages.base_page import BasePage, CriticalElement
from pages.fiat_deposit_page import FiatDepositPage
from pages.fiat_withdraw_page import FiatWithdrawPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.markets_page import MarketsPage
from pages.order_page import OrderPage
from pages.trade_page import TradePage
from pages.transaction_history_page import TransactionHistoryPage

__all__ = [
    "AssetPage",
    "BasePage",
    "CriticalElement",
    "FiatDepositPage",
    "FiatWithdrawPage",
    "HomePage",
    "LoginPage",
    "MarketsPage",
    "OrderPage",
    "TradePage",
    "TransactionHistoryPage",
]
