# Exchange UI Patrol

基于 Python + Playwright + pytest 的交易所 Web 页面巡检测试框架。

## 项目简介

Exchange UI Patrol 是一套轻量级的交易所 Web 页面自动化巡检框架，面向资深 QA 工程师，提供对交易所生产环境和测试环境的自动化可用性巡检能力。

### 核心功能

- **页面可用性检测**：自动检测页面加载状态、HTTP 响应码、JS 控制台错误
- **关键 UI 元素验证**：验证页面核心元素（导航栏、K线图、下单面板等）是否正常渲染
- **核心交易流程模拟**：模拟登录、现货下单、撤单等关键业务流程
- **测试报告生成**：基于 Allure 生成美观的 HTML 测试报告，含截图和步骤记录
- **告警通知**：巡检异常时通过企业微信/钉钉 Webhook 自动发送告警

### 技术栈

| 类别 | 技术 | 版本要求 |
|------|------|----------|
| 语言 | Python | ≥3.10 |
| 浏览器自动化 | Playwright | ≥1.40 |
| 测试框架 | pytest | ≥7.0 |
| 配置管理 | pydantic-settings | ≥2.0 |
| HTTP 客户端 | httpx | ≥0.25 |
| 测试报告 | allure-pytest | ≥2.13 |
| 两步验证 | pyotp | ≥2.9 |

## 快速开始

### 1. 安装依赖

```bash
# 使用 pip 安装（推荐 editable 模式）
pip install -e .

# 安装开发依赖（含 ruff、mypy）
pip install -e ".[dev]"
```

### 2. 安装浏览器

```bash
# 安装 Chromium 浏览器及系统依赖
playwright install --with-deps chromium
```

### 3. 配置环境

```bash
# 复制配置模板
cp config/environments/.env.example config/environments/.env.staging

# 编辑配置文件，填入实际的环境 URL 和测试账号
# 或通过环境变量注入（推荐用于 CI/CD）
```

### 4. 运行测试

```bash
# 运行全量巡检（默认 staging 环境）
pytest tests/

# 运行指定环境
pytest tests/ --env=production
```

## 目录结构

```
exchange-ui-patrol/
├── conftest.py                  # pytest 全局 fixtures（登录态、截图、通知）
├── pyproject.toml               # 项目元数据 + 依赖 + pytest 配置
├── README.md                    # 本文档
│
├── config/                      # 配置管理模块
│   ├── settings.py              # pydantic-settings 配置模型
│   └── environments/            # 环境配置文件
│       ├── .env.example         # 配置模板（含所有可配置项说明）
│       ├── .env.production      # 生产环境配置
│       └── .env.staging         # 测试环境配置
│
├── pages/                       # Page Object 层
│   ├── base_page.py             # BasePage 基类（导航、元素验证、控制台监听）
│   ├── home_page.py             # 首页 Page Object
│   ├── trade_page.py            # 交易页 Page Object
│   ├── asset_page.py            # 资产页 Page Object
│   ├── order_page.py            # 订单页 Page Object
│   ├── login_page.py            # 登录页 Page Object
│   └── markets_page.py         # 行情页 Page Object
│
├── tests/                       # 测试用例
│   ├── health_check/            # 页面可用性检测
│   │   ├── test_page_load.py    # 页面加载测试
│   │   └── test_console_errors.py  # 控制台错误检测
│   ├── ui_elements/             # UI 元素存在性验证
│   │   ├── test_home_elements.py
│   │   ├── test_trade_elements.py
│   │   └── test_asset_elements.py
│   ├── critical_flows/          # 关键业务流程验证
│   │   ├── test_login_flow.py
│   │   ├── test_spot_order.py
│   │   └── test_cancel_order.py
│   └── properties/              # 属性测试（Hypothesis）
│
├── fixtures/                    # 通用 fixtures
│   ├── auth.py                  # 登录态管理
│   └── environment.py           # 环境初始化
│
├── notifiers/                   # 告警通知模块
│   ├── base.py                  # 通知器基类 + TestResult 数据模型
│   ├── wecom.py                 # 企业微信通知器
│   └── dingtalk.py              # 钉钉通知器
│
├── utils/                       # 工具模块
│   ├── retry.py                 # 重试装饰器
│   └── timing.py                # 耗时记录
│
├── reports/                     # 报告输出目录（Allure 结果）
│
└── ci/                          # CI/CD 配置模板
    ├── github-actions.yml       # GitHub Actions 工作流
    └── gitlab-ci.yml            # GitLab CI 配置
```

## 配置说明

### 环境变量

所有配置项使用 `PATROL_` 前缀，支持通过环境变量或 `.env` 文件加载：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PATROL_ENV` | 目标环境 (staging/production) | staging |
| `PATROL_BASE_URL` | 目标环境基础 URL | - |
| `PATROL_TIMEOUT` | 全局超时时间 (ms) | 30000 |
| `PATROL_HEADLESS` | 无头模式 | true |
| `PATROL_SLOW_MO` | 操作延迟 (ms)，调试用 | 0 |
| `PATROL_TEST_USERNAME` | 测试账号用户名 | - |
| `PATROL_TEST_PASSWORD` | 测试账号密码 | - |
| `PATROL_TOTP_SECRET` | TOTP 密钥（两步验证） | - |
| `PATROL_DEVICE_ID` | 设备 ID | - |
| `PATROL_AUTH_TOKEN` | 认证 Token | - |
| `PATROL_WECOM_WEBHOOK_URL` | 企业微信 Webhook URL | - |
| `PATROL_DINGTALK_WEBHOOK_URL` | 钉钉 Webhook URL | - |
| `PATROL_ALERT_ON_FAILURE` | 失败时发送告警 | true |
| `PATROL_SCREENSHOT_ON_FAILURE` | 失败时截图 | true |

### .env 文件

框架通过 `--env` 参数决定加载哪个配置文件：

```bash
# --env=staging  → 加载 config/environments/.env.staging
# --env=production → 加载 config/environments/.env.production
```

敏感信息（账号密码、Webhook URL 等）建议通过环境变量注入，不要提交到代码仓库。

## 执行命令

### 全量巡检

```bash
# 测试环境全量巡检
pytest tests/ --env=staging

# 生产环境全量巡检
pytest tests/ --env=production
```

### 按模块执行

```bash
# 仅健康检查（页面可用性）
pytest tests/health_check/ --env=staging

# 仅 UI 元素验证
pytest tests/ui_elements/ --env=staging

# 仅关键流程验证
pytest tests/critical_flows/ --env=staging
```

### 按标记执行

```bash
# 仅执行健康检查标记的用例
pytest tests/ -m health_check --env=staging

# 仅执行可安全在生产环境运行的用例
pytest tests/ -m prod_safe --env=production

# 冒烟测试（快速验证）
pytest tests/ -m smoke --env=staging

# 组合标记
pytest tests/ -m "health_check or ui_elements" --env=staging
```

### 调试模式

```bash
# 有头模式（显示浏览器窗口）
PATROL_HEADLESS=false pytest tests/ --env=staging

# 慢速模式（每步操作间隔 500ms）
PATROL_SLOW_MO=500 pytest tests/ --env=staging

# 指定单个测试文件
pytest tests/critical_flows/test_login_flow.py --env=staging -v
```

## 报告查看

### 生成 Allure 报告

测试执行时会自动将结果输出到 `reports/allure-results/` 目录（已在 pyproject.toml 中配置）。

```bash
# 运行测试（结果自动输出到 reports/allure-results/）
pytest tests/ --env=staging

# 启动 Allure 报告服务查看结果
allure serve reports/allure-results

# 或生成静态 HTML 报告
allure generate reports/allure-results -o reports/allure-report --clean
```

### 报告内容

Allure 报告包含：
- 测试执行概览（通过率、耗时、环境信息）
- 每个用例的详细步骤记录（基于 `@allure.step` 装饰器）
- 失败用例的页面截图（自动捕获）
- 控制台错误日志附件

## 告警通知配置

### 企业微信

1. 在企业微信群中添加群机器人，获取 Webhook URL
2. 配置环境变量：

```bash
export PATROL_WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
```

### 钉钉

1. 在钉钉群中添加自定义机器人，获取 Webhook URL
2. 配置环境变量：

```bash
export PATROL_DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
```

### 通知触发条件

- 仅在存在失败用例时发送告警
- `PATROL_ALERT_ON_FAILURE=true` 时启用（默认启用）
- 支持同时配置多个通知渠道

### 通知内容

告警消息包含：
- 环境名称（staging/production）
- 失败用例数量和总用例数
- 失败用例列表（最多显示 10 条）
- 测试执行总耗时

## 扩展指南

### 添加新页面

1. 在 `pages/` 目录创建新的 Page Object 文件：

```python
from pages.base_page import BasePage, CriticalElement


class NewPage(BasePage):
    """新页面 Page Object"""

    URL_PATH = "/new-page"
    PAGE_TITLE = "页面标题"

    CRITICAL_ELEMENTS = [
        CriticalElement(
            selector="[data-testid='element-1']",
            name="元素名称",
            description="元素描述"
        ),
    ]

    # 添加页面特有的交互方法
    def do_something(self) -> None:
        self.page.locator("[data-testid='button']").click()
```

2. 在 `tests/` 对应目录创建测试用例：

```python
import pytest
from pages.new_page import NewPage


@pytest.mark.health_check
@pytest.mark.prod_safe
class TestNewPage:
    def test_page_loads(self, page, base_url):
        new_page = NewPage(page, base_url)
        new_page.navigate()
        new_page.verify_page_loaded()

    def test_critical_elements(self, page, base_url):
        new_page = NewPage(page, base_url)
        new_page.navigate()
        missing = new_page.verify_critical_elements()
        assert not missing, f"缺失元素: {[e.name for e in missing]}"
```

### 添加新测试用例

1. 确定测试类型（health_check / ui_elements / critical_flow）
2. 在对应目录创建测试文件，使用 `test_` 前缀
3. 添加适当的 pytest 标记
4. 使用已有的 fixtures（`page`、`base_url`、`authenticated_page`、`settings`）

### 添加新通知渠道

1. 在 `notifiers/` 目录创建新的通知器，继承 `BaseNotifier`：

```python
from notifiers.base import BaseNotifier, TestResult


class NewNotifier(BaseNotifier):
    def format_message(self, result: TestResult) -> dict:
        # 实现消息格式化逻辑
        return {"key": "value"}
```

2. 在 `conftest.py` 的 `pytest_sessionfinish` 中注册新通知器

## CI/CD 集成

### GitHub Actions

将 `ci/github-actions.yml` 复制到 `.github/workflows/patrol.yml`：

```bash
cp ci/github-actions.yml .github/workflows/patrol.yml
```

在 GitHub 仓库 Settings → Secrets and variables → Actions 中配置：
- `PATROL_TEST_USERNAME`
- `PATROL_TEST_PASSWORD`
- `PATROL_TOTP_SECRET`
- `PATROL_DEVICE_ID`
- `PATROL_AUTH_TOKEN`
- `PATROL_WECOM_WEBHOOK_URL`

工作流将每 30 分钟自动执行巡检，也可在 Actions 页面手动触发并选择目标环境。

### GitLab CI

将 `ci/gitlab-ci.yml` 内容合并到项目根目录的 `.gitlab-ci.yml`：

```bash
cp ci/gitlab-ci.yml .gitlab-ci.yml
```

在 GitLab 项目 Settings → CI/CD → Variables 中配置相同的环境变量。

在 CI/CD → Schedules 中创建定时任务（建议每 30 分钟）。

### 报告归档

CI/CD 执行完成后，Allure 结果会作为 artifact 上传，保留 30 天。可通过以下方式查看：
- GitHub Actions：在 workflow run 页面下载 artifact
- GitLab CI：在 pipeline 页面查看 artifacts

## 目标交易所

本框架默认配置针对 [www.example.com](https://www.example.com) 交易所。如需适配其他交易所，修改以下内容：

1. 更新 `config/environments/` 中的 `PATROL_BASE_URL`
2. 调整 `pages/` 中各 Page Object 的元素选择器
3. 根据目标交易所的登录流程修改 `fixtures/auth.py`

## License

MIT
