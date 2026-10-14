"""法币出金 - 银行卡管理页面验证测试

验证法币出金页面的银行卡管理功能的 UI 可用性：
- 页面加载正常
- 新增银行卡按钮可见可点击（仅验证表单弹出，不提交）
- 银行卡列表正常展示
- 删除按钮可见（仅验证确认弹窗弹出，不执行删除）

注意：生产环境不执行真实的新增/删除操作，仅验证 UI 元素和交互入口可用。
出入金依赖外部网银，不做真实资金操作。
"""

import allure
import pytest
from playwright.sync_api import Page

from config.settings import AppSettings
from fixtures.environment import dismiss_initial_popups
from pages.fiat_withdraw_page import FiatWithdrawPage


@pytest.mark.critical_flow
@pytest.mark.prod_safe
@allure.feature("法币业务流程验证")
@allure.story("法币出金 - 银行卡管理")
class TestFiatWithdraw:
    """法币出金页面银行卡管理测试套件（UI验证，不执行真实操作）"""

    @allure.title("验证法币出金页面加载")
    @allure.description("验证法币出金页面能正常加载，关键元素可见")
    def test_fiat_withdraw_page_loads(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证法币出金页面正常加载"""
        withdraw_page = FiatWithdrawPage(authenticated_page, settings.base_url)

        with allure.step("导航到法币出金页面"):
            withdraw_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证关键元素"):
            missing_elements = withdraw_page.verify_critical_elements()

        if missing_elements:
            missing_info = "\n".join(
                f"- {elem.name}: selector='{elem.selector}'"
                for elem in missing_elements
            )
            allure.attach(
                missing_info,
                name="missing_elements",
                attachment_type=allure.attachment_type.TEXT,
            )
            screenshot = authenticated_page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="fiat_withdraw_page_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

        assert not missing_elements, (
            f"法币出金页面缺失 {len(missing_elements)} 个关键元素: "
            f"{', '.join(e.name for e in missing_elements)}"
        )

    @allure.title("验证新增银行卡入口可用")
    @allure.description(
        "验证新增银行卡按钮可见可点击，表单能正常弹出。"
        "仅验证 UI 交互入口，不提交表单，不产生真实数据。"
    )
    def test_add_bank_card_entry_available(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证新增银行卡入口可用（不提交，不产生真实数据）

        流程：
        1. 导航到法币出金页面
        2. 验证"新增银行卡"按钮可见
        3. 点击按钮，验证表单/弹窗弹出
        4. 不填写任何信息，不提交
        """
        withdraw_page = FiatWithdrawPage(authenticated_page, settings.base_url)

        with allure.step("导航到法币出金页面"):
            withdraw_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("验证新增银行卡按钮可见"):
            add_btn = authenticated_page.locator(withdraw_page._ADD_BANK_BUTTON).first
            add_btn.wait_for(state="visible", timeout=10000)
            assert add_btn.is_visible(), "新增银行卡按钮不可见"

        with allure.step("点击新增银行卡按钮，验证表单弹出"):
            add_btn.click()
            # 验证表单/弹窗出现（检查输入框是否可见）
            form_indicator = authenticated_page.locator(
                f"{withdraw_page._BANK_NAME_INPUT}, "
                f"{withdraw_page._ACCOUNT_NUMBER_INPUT}, "
                "form, .modal, .dialog, [class*='form'], [class*='modal']"
            ).first
            try:
                form_indicator.wait_for(state="visible", timeout=10000)
                allure.attach(
                    "新增银行卡表单已成功弹出",
                    name="form_status",
                    attachment_type=allure.attachment_type.TEXT,
                )
            except Exception:
                # 截图记录当前状态
                screenshot = authenticated_page.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name="after_click_add_bank",
                    attachment_type=allure.attachment_type.PNG,
                )
                pytest.fail("点击新增银行卡按钮后，表单未弹出")

    @allure.title("验证银行卡列表展示")
    @allure.description("验证已绑定的银行卡列表能正常展示")
    def test_bank_card_list_displayed(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证银行卡列表展示（只读查看）"""
        withdraw_page = FiatWithdrawPage(authenticated_page, settings.base_url)

        with allure.step("导航到法币出金页面"):
            withdraw_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("获取银行卡列表"):
            card_count = withdraw_page.get_bank_card_count()
            allure.attach(
                f"当前已绑定银行卡数量: {card_count}",
                name="bank_card_count",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("验证银行卡列表区域可见"):
            bank_list = authenticated_page.locator(
                "[data-testid='bank-card-list'], .bank-card-list, "
                ".bank-accounts, .saved-banks, [class*='bank-list']"
            ).first
            try:
                bank_list.wait_for(state="visible", timeout=10000)
            except Exception:
                # 可能没有绑定银行卡，列表为空但区域应该存在
                empty_state = authenticated_page.locator(
                    "[class*='empty'], .no-data, .empty-state"
                ).first
                if not empty_state.is_visible():
                    pytest.fail("银行卡列表区域不可见且无空状态提示")

    @allure.title("验证删除银行卡按钮可见")
    @allure.description(
        "验证银行卡列表中的删除按钮可见。仅验证按钮存在，不执行删除操作。"
    )
    def test_delete_bank_card_button_visible(
        self, authenticated_page: Page, settings: AppSettings
    ) -> None:
        """验证删除银行卡按钮可见（不执行删除）"""
        withdraw_page = FiatWithdrawPage(authenticated_page, settings.base_url)

        with allure.step("导航到法币出金页面"):
            withdraw_page.navigate()

        with allure.step("关闭初始弹窗"):
            dismiss_initial_popups(authenticated_page)

        with allure.step("检查是否存在银行卡"):
            card_count = withdraw_page.get_bank_card_count()
            if card_count == 0:
                pytest.skip("当前无绑定银行卡，跳过删除按钮验证")

        with allure.step("验证删除按钮可见"):
            # 检查第一张银行卡的删除按钮
            bank_cards = authenticated_page.locator(withdraw_page._BANK_CARD_ITEM)
            first_card = bank_cards.first
            delete_btn = first_card.locator(withdraw_page._DELETE_BANK_BUTTON).first

            assert delete_btn.is_visible(), "银行卡删除按钮不可见"
            allure.attach(
                "删除按钮可见，验证通过（未执行实际删除）",
                name="delete_button_status",
                attachment_type=allure.attachment_type.TEXT,
            )
