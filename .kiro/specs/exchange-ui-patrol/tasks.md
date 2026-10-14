# Implementation Plan: Exchange UI Patrol

## Overview

基于 Python + Playwright + pytest 的交易所 Web 页面巡检测试框架实现计划。按照模块依赖关系从基础设施层开始，逐步构建配置管理、Page Object 层、测试用例层、通知告警层，最终完成 CI/CD 集成。

## Tasks

- [x] 1. 项目初始化与基础设施搭建
  - [x] 1.1 创建项目目录结构和依赖配置
    - 创建 `pyproject.toml`，定义项目元数据和依赖（playwright, pytest, pytest-playwright, pydantic-settings, httpx, allure-pytest, hypothesis, ruff, mypy）
    - 创建完整的目录结构：config/, pages/, tests/, fixtures/, notifiers/, utils/, reports/, ci/
    - 创建各目录的 `__init__.py` 文件
    - 创建 `pytest.ini` 或在 pyproject.toml 中配置 pytest markers（health_check, ui_elements, critical_flow, smoke, prod_safe）
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 1.2 创建环境配置模板文件
    - 创建 `config/environments/.env.example` 配置模板，列出所有可配置项
    - 创建 `config/environments/.env.production` 和 `.env.staging` 环境配置文件
    - 创建 `.gitignore` 排除 reports/、.env（非模板）、__pycache__ 等
    - _Requirements: 2.1, 2.5_

- [x] 2. 配置管理模块实现
  - [x] 2.1 实现 pydantic-settings 配置模型
    - 创建 `config/settings.py`，定义 `Environment` 枚举和 `AppSettings` 类
    - 实现字段：env, base_url, timeout, headless, slow_mo, test_username, test_password, report_dir, screenshot_on_failure, wecom_webhook_url, dingtalk_webhook_url, alert_on_failure
    - 配置 `model_config` 支持 `PATROL_` 前缀环境变量和 .env 文件加载
    - 实现 `get_settings(env)` 工厂函数，根据环境名加载对应 .env 文件
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 2.2 编写属性测试 - 配置序列化往返一致性
    - **Property 1: Configuration round-trip serialization**
    - 使用 Hypothesis 生成任意有效 AppSettings 字段值，验证 model_dump() → 重建实例后字段一致
    - **Validates: Requirements 2.3**

  - [ ]* 2.3 编写属性测试 - 环境变量覆盖优先级
    - **Property 2: Environment resolution with override**
    - 使用 Hypothesis 生成任意配置字段和 PATROL_ 前缀环境变量值，验证环境变量优先于 .env 文件默认值
    - **Validates: Requirements 2.2, 2.5, 8.3**

- [x] 3. Page Object 基类与工具模块
  - [x] 3.1 实现 BasePage 基类
    - 创建 `pages/base_page.py`，定义 `CriticalElement` 数据类和 `BasePage` 类
    - 实现 `navigate()` 方法，使用 `page.goto()` 导航到页面
    - 实现 `verify_page_loaded()` 方法，断言 URL 和标题
    - 实现 `verify_critical_elements()` 方法，遍历 CRITICAL_ELEMENTS 验证可见性，返回缺失元素列表
    - 实现 `setup_console_listener()` 和 `get_console_errors()` 方法，捕获控制台错误
    - 使用 `@allure.step` 装饰器为关键方法添加步骤记录
    - _Requirements: 1.2, 3.2, 3.4, 4.1, 4.2, 4.4_

  - [ ]* 3.2 编写属性测试 - 控制台错误捕获完整性
    - **Property 3: Console error capture completeness**
    - 使用 Hypothesis 生成任意控制台消息序列（含 error 和非 error 类型），验证 get_console_errors() 仅返回 error 类型消息且内容完整
    - **Validates: Requirements 3.4**

  - [ ]* 3.3 编写属性测试 - 关键元素验证正确性
    - **Property 4: Critical element verification correctness**
    - 使用 Hypothesis 生成任意 CriticalElement 列表和可见/不可见子集，验证 verify_critical_elements() 返回恰好不可见的元素集合
    - **Validates: Requirements 4.1, 4.3, 4.5**

  - [x] 3.4 实现工具模块
    - 创建 `utils/retry.py`，实现可配置的重试装饰器（max_attempts, delay, exceptions 参数）
    - 创建 `utils/timing.py`，实现耗时记录工具函数
    - _Requirements: 5.6_

- [x] 4. Checkpoint - 确保基础模块测试通过
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 5. 具体 Page Object 实现
  - [x] 5.1 实现 LoginPage
    - 创建 `pages/login_page.py`，定义登录页面的 URL_PATH、CRITICAL_ELEMENTS
    - 实现 `login(username, password)` 方法，填写表单并提交
    - 实现 `is_logged_in()` 方法，验证登录成功状态
    - _Requirements: 5.4, 1.2_

  - [x] 5.2 实现 HomePage
    - 创建 `pages/home_page.py`，定义首页的 URL_PATH、PAGE_TITLE、CRITICAL_ELEMENTS（导航栏、公告区域、行情列表等）
    - _Requirements: 3.5, 4.4, 1.2_

  - [x] 5.3 实现 TradePage
    - 创建 `pages/trade_page.py`，定义交易页的 CRITICAL_ELEMENTS（K线图、下单表单、订单簿、最新成交）
    - 实现 `place_limit_order(side, price, amount)` 方法
    - 实现 `get_current_price()` 方法
    - _Requirements: 3.5, 4.4, 5.5, 1.2_

  - [x] 5.4 实现 AssetPage 和 OrderPage
    - 创建 `pages/asset_page.py`，定义资产页的 CRITICAL_ELEMENTS（余额显示、充提按钮等）
    - 创建 `pages/order_page.py`，定义订单页的 CRITICAL_ELEMENTS（订单列表、筛选器等）
    - 实现 OrderPage 的 `cancel_order()` 方法
    - _Requirements: 3.5, 4.4, 5.5, 1.2_

- [x] 6. Fixtures 与 conftest 实现
  - [x] 6.1 实现全局 conftest.py
    - 创建根目录 `conftest.py`，添加 `--env` 命令行参数
    - 实现 `settings` session-scoped fixture，加载环境配置
    - 实现 `base_url` session-scoped fixture，提供基础 URL
    - 实现 `authenticated_page` fixture，提供已登录的页面实例
    - 实现 `test_timing` autouse fixture，记录每个测试的执行耗时
    - 实现 `pytest_runtest_makereport` hook，失败时自动截图并附加到 Allure 报告
    - _Requirements: 1.5, 2.2, 2.4, 5.4, 6.3_

  - [x] 6.2 实现 fixtures 模块
    - 创建 `fixtures/auth.py`，封装登录态管理逻辑
    - 创建 `fixtures/environment.py`，封装环境初始化逻辑
    - _Requirements: 1.5, 5.4_

- [x] 7. 告警通知模块实现
  - [x] 7.1 实现通知器基类
    - 创建 `notifiers/base.py`，定义 `TestResult` 数据类和 `BaseNotifier` 抽象基类
    - 实现 `send()` 方法：调用 format_message() 后 POST 到 webhook_url，异常时仅记录日志不抛出
    - 实现 `close()` 方法释放 httpx 客户端资源
    - _Requirements: 7.5_

  - [x] 7.2 实现企业微信通知器
    - 创建 `notifiers/wecom.py`，继承 BaseNotifier
    - 实现 `format_message()` 方法，生成 markdown 格式消息体（包含环境、失败数、用例列表、耗时）
    - _Requirements: 7.2, 7.3_

  - [x] 7.3 实现钉钉通知器
    - 创建 `notifiers/dingtalk.py`，继承 BaseNotifier
    - 实现 `format_message()` 方法，生成钉钉 markdown 消息体
    - _Requirements: 7.6_

  - [x] 7.4 实现通知分发逻辑
    - 在 `conftest.py` 的 `pytest_sessionfinish` hook 中实现通知分发
    - 根据配置的 webhook URL 决定发送到哪些渠道
    - 仅在存在失败用例时发送通知
    - _Requirements: 7.1, 7.4_

  - [ ]* 7.5 编写属性测试 - 企业微信消息内容完整性
    - **Property 5: Alert message content completeness - WeChat**
    - 使用 Hypothesis 生成任意 TestResult 实例，验证 format_message() 输出包含环境名、失败数、用例名、耗时
    - **Validates: Requirements 7.2, 7.3**

  - [ ]* 7.6 编写属性测试 - 钉钉消息内容完整性
    - **Property 6: Alert message content completeness - DingTalk**
    - 使用 Hypothesis 生成任意 TestResult 实例，验证 format_message() 输出包含环境名、失败数、用例名、耗时
    - **Validates: Requirements 7.6**

  - [ ]* 7.7 编写属性测试 - 通知器错误恢复能力
    - **Property 7: Notifier error resilience**
    - 使用 Hypothesis 生成任意 HTTP 错误响应（4xx, 5xx, 超时, DNS 失败），验证 send() 返回 False 且不抛出异常
    - **Validates: Requirements 7.5**

  - [ ]* 7.8 编写属性测试 - 通知分发逻辑正确性
    - **Property 8: Notification dispatch logic**
    - 使用 Hypothesis 生成任意 webhook URL 配置组合和 TestResult，验证仅向已配置渠道发送且零失败时不发送
    - **Validates: Requirements 7.1, 7.4**

- [x] 8. Checkpoint - 确保通知模块测试通过
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 9. 测试用例实现 - 页面可用性检测
  - [x] 9.1 实现页面加载测试
    - 创建 `tests/health_check/test_page_load.py`
    - 为每个关键页面（首页、交易页、资产页、订单页）编写加载测试
    - 断言页面在超时时间内加载完成、HTTP 状态码为 2xx、页面标题/特征元素存在
    - 使用 `@pytest.mark.health_check` 和 `@pytest.mark.prod_safe` 标记
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [x] 9.2 实现控制台错误检测测试
    - 创建 `tests/health_check/test_console_errors.py`
    - 在页面导航前设置控制台监听，加载后检查是否有 JS 错误
    - 将控制台错误记录到 Allure 报告
    - _Requirements: 3.4_

- [x] 10. 测试用例实现 - UI 元素存在性验证
  - [x] 10.1 实现首页元素验证测试
    - 创建 `tests/ui_elements/test_home_elements.py`
    - 验证首页所有 CRITICAL_ELEMENTS 可见
    - 失败时记录缺失元素选择器并截图
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 10.2 实现交易页元素验证测试
    - 创建 `tests/ui_elements/test_trade_elements.py`
    - 验证交易页 K线图、下单表单、订单簿、最新成交等关键元素
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 10.3 实现资产页元素验证测试
    - 创建 `tests/ui_elements/test_asset_elements.py`
    - 验证资产页余额显示、充提按钮等关键元素
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 11. 测试用例实现 - 关键流程验证
  - [x] 11.1 实现登录流程测试
    - 创建 `tests/critical_flows/test_login_flow.py`
    - 模拟完整登录流程：导航到登录页 → 输入凭证 → 提交 → 验证登录成功
    - 记录流程执行耗时
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6_

  - [x] 11.2 实现现货下单流程测试
    - 创建 `tests/critical_flows/test_spot_order.py`
    - 模拟下单流程：登录 → 导航到交易页 → 填写订单参数 → 提交 → 验证订单创建
    - 使用 `authenticated_page` fixture
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 5.6_

  - [x] 11.3 实现撤单流程测试
    - 创建 `tests/critical_flows/test_cancel_order.py`
    - 模拟撤单流程：登录 → 导航到订单页 → 选择订单 → 执行撤单 → 验证撤单成功
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 5.6_

- [x] 12. Checkpoint - 确保所有测试用例结构正确
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 13. 报告与 CI/CD 集成
  - [x] 13.1 配置 Allure 报告集成
    - 在 `conftest.py` 中确保 Allure 步骤、截图、附件正确集成
    - 配置 `pytest.ini` 中的 `--alluredir` 默认输出路径
    - 创建 `reports/.gitkeep` 保留报告目录
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 13.2 创建 CI/CD 配置模板
    - 创建 `ci/github-actions.yml`，配置定时触发（cron）、手动触发、环境变量注入、Playwright 安装、测试执行、报告归档
    - 创建 `ci/gitlab-ci.yml`，提供 GitLab CI 等效配置
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 13.3 创建 README 文档
    - 编写 `README.md`，包含：项目简介、快速开始、目录结构说明、配置说明、执行命令、扩展指南
    - _Requirements: 1.6_

- [x] 14. 最终 Checkpoint - 确保所有模块集成正确
  - 确保所有测试通过，如有问题请向用户确认。

## Notes

- 标记 `*` 的子任务为可选属性测试任务，可跳过以加速 MVP 交付
- 每个任务引用了具体的需求条款以确保可追溯性
- Checkpoint 任务确保增量验证，避免问题累积
- 属性测试使用 Hypothesis 库验证通用正确性属性
- 单元测试验证具体示例和边界条件
- 实现顺序遵循依赖关系：配置 → 基类 → 具体实现 → 测试用例 → 集成
