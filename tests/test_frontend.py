#!/usr/bin/env python3
"""
前端全面测试脚本 - 检查所有页面显示、空状态、弹框交互逻辑
"""
import json
import time
import os
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = "http://localhost:5173"
SCREENSHOT_DIR = "/tmp/test_screenshots"
ISSUES = []

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def log_issue(page_name: str, issue: str, severity: str = "BUG"):
    entry = f"[{severity}] {page_name}: {issue}"
    ISSUES.append(entry)
    print(entry)


def screenshot(page: Page, name: str):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  📸 {name}.png")
    return path


def wait_page_load(page: Page):
    page.wait_for_load_state("networkidle", timeout=10000)


def login(page: Page):
    """登录"""
    page.goto(f"{BASE_URL}/login")
    wait_page_load(page)
    screenshot(page, "01_login_page")

    # 检查登录表单是否存在
    username_input = page.locator("input[type='text'], input[placeholder*='用户名'], input[placeholder*='username']").first
    password_input = page.locator("input[type='password']").first

    if not username_input.is_visible():
        log_issue("Login", "用户名输入框不可见")
        return False
    if not password_input.is_visible():
        log_issue("Login", "密码输入框不可见")
        return False

    username_input.fill("admin")
    password_input.fill("admin123")
    screenshot(page, "01_login_filled")

    # 点击登录按钮
    login_btn = page.locator("button[type='submit'], button:has-text('登录'), button:has-text('Login')").first
    login_btn.click()

    try:
        page.wait_for_url(f"{BASE_URL}/dashboard", timeout=8000)
        print("  ✅ 登录成功，跳转到 dashboard")
        return True
    except:
        try:
            page.wait_for_url(f"{BASE_URL}/**", timeout=5000)
            print(f"  ✅ 登录成功，跳转到 {page.url}")
            return True
        except:
            screenshot(page, "01_login_failed")
            log_issue("Login", f"登录后未成功跳转，当前URL: {page.url}")
            return False


def test_dashboard(page: Page):
    """测试 Dashboard 页面"""
    print("\n=== Dashboard ===")
    page.goto(f"{BASE_URL}/dashboard")
    wait_page_load(page)
    screenshot(page, "02_dashboard")

    # 检查统计卡片
    stat_cards = page.locator(".n-statistic, .stat-card, [class*='statistic']").all()
    print(f"  统计卡片数量: {len(stat_cards)}")

    # 检查图表是否加载
    charts = page.locator("canvas").all()
    print(f"  图表数量: {len(charts)}")
    if len(charts) == 0:
        log_issue("Dashboard", "图表未渲染（canvas 元素不存在）", "WARN")

    # 检查快捷入口按钮
    nav_btns = page.locator(".n-button").all()
    print(f"  按钮数量: {len(nav_btns)}")

    # 检查近期任务表格
    tables = page.locator(".n-data-table").all()
    print(f"  表格数量: {len(tables)}")

    # 检查空数据时是否有合理展示（首次使用可能没有数据）
    try:
        empty_text = page.locator(".n-empty").first
        if empty_text.is_visible():
            screenshot(page, "02_dashboard_empty_state")
            print("  空状态已显示")
    except Exception:
        pass


def test_applications(page: Page):
    """测试应用管理页面"""
    print("\n=== Applications ===")
    page.goto(f"{BASE_URL}/applications")
    wait_page_load(page)
    screenshot(page, "03_applications_list")

    # 检查统计卡片
    stat_area = page.locator(".n-grid, .n-statistic").first
    print(f"  统计区域可见: {stat_area.is_visible()}")

    # 检查应用列表表格
    table = page.locator(".n-data-table").first
    if not table.is_visible():
        log_issue("Applications", "应用列表表格不可见")

    # 检查空状态
    rows = page.locator(".n-data-table-tr:not(.n-data-table-tr--summary)").all()
    print(f"  表格行数: {len(rows)}")

    # === 测试新增应用弹框 ===
    add_btn = page.locator("button:has-text('新增'), button[class*='add'], .n-button:has(+.n-icon-add)").first
    # 尝试通过 + 按钮找
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button").filter(has_text="新增").first

    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "03_applications_add_modal")

        modal = page.locator(".n-modal, .n-dialog").first
        if modal.is_visible():
            print("  ✅ 新增应用弹框打开")

            # 检查弹框内必填项
            app_name_input = page.locator(".n-modal input[placeholder*='应用'], .n-modal input[placeholder*='名称']").first
            if app_name_input.is_visible():
                print("  ✅ 应用名称输入框存在")

            # 检查启动模式切换（SSH/Docker）
            mode_tabs = page.locator(".n-modal .n-radio-group, .n-modal .n-tabs").first
            if mode_tabs.is_visible():
                print("  ✅ 启动模式切换存在")

            # 尝试提交空表单（测试验证）
            confirm_btn = page.locator(".n-modal button:has-text('确定'), .n-modal button:has-text('保存'), .n-modal button:has-text('提交')").first
            if confirm_btn.is_visible():
                confirm_btn.click()
                page.wait_for_timeout(800)
                screenshot(page, "03_applications_add_validation")
                # 检查是否有错误提示
                error_msg = page.locator(".n-form-item-feedback--error, .n-form-feedback--error").first
                if error_msg.is_visible():
                    print("  ✅ 空表单验证生效")
                else:
                    log_issue("Applications", "新增应用表单空提交未触发验证提示", "WARN")

            # 关闭弹框
            close_btn = page.locator(".n-modal .n-base-icon-close, .n-modal button:has-text('取消')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)
        else:
            log_issue("Applications", "点击新增按钮后弹框未出现")
    else:
        log_issue("Applications", "新增应用按钮不存在", "WARN")


def test_recording(page: Page):
    """测试录制中心"""
    print("\n=== Recording ===")
    page.goto(f"{BASE_URL}/recording")
    wait_page_load(page)
    screenshot(page, "04_recording_list")

    # 检查页面基本元素
    table = page.locator(".n-data-table").first
    print(f"  会话表格可见: {table.is_visible()}")

    # 检查过滤区域
    filters = page.locator(".n-select, .n-date-picker, .n-input").all()
    print(f"  过滤控件数量: {len(filters)}")

    # === 测试新建会话弹框 ===
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button:has-text('新建'), button:has-text('新增')").first

    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "04_recording_new_session_modal")

        modal = page.locator(".n-modal, .n-dialog").first
        if modal.is_visible():
            print("  ✅ 新建会话弹框打开")

            # 检查应用下拉是否有选项（可能需要先有应用）
            app_select = page.locator(".n-modal .n-select").first
            if app_select.is_visible():
                app_select.click()
                page.wait_for_timeout(500)
                options = page.locator(".n-base-select-option").all()
                if len(options) == 0:
                    log_issue("Recording", "新建会话弹框中应用下拉无选项（需先创建应用）", "WARN")
                    screenshot(page, "04_recording_session_no_apps")
                else:
                    print(f"  应用选项数: {len(options)}")
                # 关闭下拉
                page.keyboard.press("Escape")

            # 关闭弹框
            close_btn = page.locator(".n-modal .n-base-icon-close, .n-modal button:has-text('取消')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)
        else:
            log_issue("Recording", "点击新建会话后弹框未出现")
    else:
        log_issue("Recording", "新建会话按钮不存在", "WARN")

    # 检查空状态
    try:
        empty = page.locator(".n-empty").first
        if empty.is_visible():
            print("  空状态正常显示")
    except Exception:
        pass


def test_testcases(page: Page):
    """测试 测试用例库"""
    print("\n=== TestCases ===")
    page.goto(f"{BASE_URL}/testcases")
    wait_page_load(page)
    screenshot(page, "05_testcases_list")

    # 检查操作按钮
    btns = page.locator(".n-button").all()
    btn_texts = [b.inner_text().strip() for b in btns if b.is_visible()]
    print(f"  可见按钮: {btn_texts}")

    # 检查导出按钮
    export_btn = page.locator("button:has-text('导出')").first
    if export_btn.is_visible():
        print("  ✅ 导出按钮存在")
    else:
        log_issue("TestCases", "导出按钮不存在", "WARN")

    # === 测试新增用例侧边栏 ===
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button:has-text('新增')").first

    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "05_testcases_add_drawer")

        drawer = page.locator(".n-drawer").first
        if drawer.is_visible():
            print("  ✅ 新增用例侧边栏打开")

            # 检查各标签页
            tabs = page.locator(".n-drawer .n-tabs-tab, .n-drawer .n-tab").all()
            print(f"  侧边栏标签页数: {len(tabs)}")

            for tab in tabs:
                if tab.is_visible():
                    tab_text = tab.inner_text().strip()
                    tab.click()
                    page.wait_for_timeout(500)
                    screenshot(page, f"05_testcases_tab_{tab_text}")
                    print(f"  切换到标签: {tab_text}")

            # 关闭侧边栏
            close_btn = page.locator(".n-drawer .n-base-icon-close").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)
        else:
            log_issue("TestCases", "点击新增后侧边栏未出现，可能打开了 Modal")
            modal = page.locator(".n-modal").first
            if modal.is_visible():
                screenshot(page, "05_testcases_add_modal")
                close_btn = page.locator(".n-modal .n-base-icon-close, button:has-text('取消')").first
                if close_btn.is_visible():
                    close_btn.click()


def test_replay(page: Page):
    """测试回放页面"""
    print("\n=== Replay ===")
    page.goto(f"{BASE_URL}/replay")
    wait_page_load(page)
    screenshot(page, "06_replay_page")

    # 检查回放配置区域
    app_select = page.locator(".n-select").first
    print(f"  应用下拉可见: {app_select.is_visible()}")

    # 检查开始回放按钮状态（无用例时应 disabled）
    start_btn = page.locator("button:has-text('开始回放'), button:has-text('发起回放')").first
    if start_btn.is_visible():
        is_disabled = start_btn.get_attribute("disabled") is not None or "disabled" in (start_btn.get_attribute("class") or "")
        print(f"  开始回放按钮 disabled: {is_disabled}")
        if not is_disabled:
            log_issue("Replay", "无用例选中时开始回放按钮未禁用", "BUG")
    else:
        log_issue("Replay", "开始回放按钮不存在", "WARN")

    # 检查高级配置折叠面板
    advanced_collapse = page.locator(".n-collapse, [class*='advanced']").first
    if advanced_collapse.is_visible():
        print("  ✅ 高级配置折叠区域存在")
        # 尝试展开
        collapse_header = page.locator(".n-collapse-item__header, .n-collapse-item-header").first
        if collapse_header.is_visible():
            collapse_header.click()
            page.wait_for_timeout(800)
            screenshot(page, "06_replay_advanced_expanded")
            print("  ✅ 高级配置已展开")

    # 检查历史任务表格
    tables = page.locator(".n-data-table").all()
    print(f"  表格数量: {len(tables)}")


def test_replay_history(page: Page):
    """测试回放历史"""
    print("\n=== Replay History ===")
    page.goto(f"{BASE_URL}/replay/history")
    wait_page_load(page)
    screenshot(page, "07_replay_history")

    table = page.locator(".n-data-table").first
    print(f"  历史表格可见: {table.is_visible()}")
    if not table.is_visible():
        log_issue("Replay History", "回放历史表格不可见")


def test_results(page: Page):
    """测试执行结果页面"""
    print("\n=== Results ===")
    page.goto(f"{BASE_URL}/results")
    wait_page_load(page)
    screenshot(page, "08_results_list")

    # 检查统计卡片
    stat_area = page.locator(".n-grid, .n-card").all()
    print(f"  卡片/区域数量: {len(stat_area)}")

    # 检查过滤器
    app_filter = page.locator(".n-select").first
    print(f"  应用过滤下拉可见: {app_filter.is_visible()}")

    # 检查刷新按钮
    refresh_btn = page.locator("button:has-text('刷新')").first
    if refresh_btn.is_visible():
        print("  ✅ 刷新按钮存在")


def test_suites(page: Page):
    """测试测试套件页面"""
    print("\n=== Suites ===")
    page.goto(f"{BASE_URL}/suites")
    wait_page_load(page)
    screenshot(page, "09_suites_list")

    # 检查基本元素
    table = page.locator(".n-data-table").first
    print(f"  套件表格可见: {table.is_visible()}")

    # 新增套件
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "09_suites_add_modal")

        modal_or_drawer = page.locator(".n-modal, .n-drawer").first
        if modal_or_drawer.is_visible():
            print("  ✅ 新增套件弹框/侧边栏打开")
            close_btn = page.locator(".n-modal .n-base-icon-close, .n-drawer .n-base-icon-close, button:has-text('取消')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)
        else:
            log_issue("Suites", "点击新增后没有打开弹框或侧边栏")
    else:
        log_issue("Suites", "新增套件按钮不存在", "WARN")


def test_schedule(page: Page):
    """测试定时任务页面"""
    print("\n=== Schedule ===")
    page.goto(f"{BASE_URL}/schedule")
    wait_page_load(page)
    screenshot(page, "10_schedule_page")

    table = page.locator(".n-data-table").first
    print(f"  定时任务表格可见: {table.is_visible()}")

    # 新增任务
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button:has-text('新增'), button:has-text('添加')").first

    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "10_schedule_add_modal")
        modal = page.locator(".n-modal, .n-drawer").first
        if modal.is_visible():
            print("  ✅ 新增定时任务弹框打开")
            close_btn = page.locator(".n-modal .n-base-icon-close, .n-drawer .n-base-icon-close, button:has-text('取消')").first
            if close_btn.is_visible():
                close_btn.click()
        else:
            log_issue("Schedule", "点击新增后弹框未出现")


def test_compare(page: Page):
    """测试差异对比页面"""
    print("\n=== Compare ===")
    page.goto(f"{BASE_URL}/compare")
    wait_page_load(page)
    screenshot(page, "11_compare_page")

    # 检查对比选择区域
    selects = page.locator(".n-select").all()
    print(f"  下拉选择控件数量: {len(selects)}")
    if len(selects) < 2:
        log_issue("Compare", f"对比页面下拉选择控件过少，仅有 {len(selects)} 个", "WARN")


def test_settings(page: Page):
    """测试系统设置页面"""
    print("\n=== Settings ===")
    page.goto(f"{BASE_URL}/settings")
    wait_page_load(page)
    screenshot(page, "12_settings_page")

    # 检查配置说明区域
    config_doc = page.locator(".n-card, .n-collapse").first
    print(f"  配置说明区域可见: {config_doc.is_visible()}")

    # 检查脱敏规则表格
    table = page.locator(".n-data-table").first
    print(f"  脱敏规则表格可见: {table.is_visible()}")

    # 新增脱敏规则
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button:has-text('新增')").first

    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "12_settings_add_rule_modal")
        modal = page.locator(".n-modal").first
        if modal.is_visible():
            print("  ✅ 新增脱敏规则弹框打开")
            close_btn = page.locator(".n-modal .n-base-icon-close, button:has-text('取消')").first
            if close_btn.is_visible():
                close_btn.click()
        else:
            log_issue("Settings", "点击新增脱敏规则后弹框未出现")


def test_ci(page: Page):
    """测试 CI/CD 页面"""
    print("\n=== CI/CD ===")
    page.goto(f"{BASE_URL}/ci")
    wait_page_load(page)
    screenshot(page, "13_ci_page")

    # 检查页面基本内容
    content = page.locator(".n-card, .n-layout-content").first
    print(f"  页面内容区可见: {content.is_visible()}")


def test_users(page: Page):
    """测试用户管理页面"""
    print("\n=== Users ===")
    page.goto(f"{BASE_URL}/users")
    wait_page_load(page)
    screenshot(page, "14_users_list")

    # 检查用户表格
    table = page.locator(".n-data-table").first
    print(f"  用户表格可见: {table.is_visible()}")

    rows = page.locator(".n-data-table-tbody .n-data-table-tr").all()
    print(f"  用户行数: {len(rows)}")

    # === 测试新增用户弹框 ===
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button:has-text('新增')").first

    if add_btn.is_visible():
        add_btn.click()
        page.wait_for_timeout(1000)
        screenshot(page, "14_users_add_modal")

        modal = page.locator(".n-modal").first
        if modal.is_visible():
            print("  ✅ 新增用户弹框打开")

            # 检查字段
            inputs = page.locator(".n-modal input").all()
            print(f"  弹框输入框数量: {len(inputs)}")
            if len(inputs) < 2:
                log_issue("Users", "新增用户弹框输入框不足（期望至少用户名+密码）", "WARN")

            # 测试角色下拉
            role_select = page.locator(".n-modal .n-select").first
            if role_select.is_visible():
                role_select.click()
                page.wait_for_timeout(500)
                options = page.locator(".n-base-select-option").all()
                print(f"  角色选项: {[o.inner_text().strip() for o in options]}")
                page.keyboard.press("Escape")

            # 测试空提交验证
            confirm_btn = page.locator(".n-modal button:has-text('确定'), .n-modal button:has-text('保存')").first
            if confirm_btn.is_visible():
                confirm_btn.click()
                page.wait_for_timeout(800)
                screenshot(page, "14_users_add_validation")
                error = page.locator(".n-form-item-feedback--error").first
                if error.is_visible():
                    print("  ✅ 空提交验证生效")
                else:
                    log_issue("Users", "新增用户空提交未触发验证", "WARN")

            close_btn = page.locator(".n-modal .n-base-icon-close, button:has-text('取消')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)
        else:
            log_issue("Users", "点击新增用户后弹框未出现")

    # === 测试编辑用户（如果有用户行） ===
    if len(rows) > 0:
        edit_btn = page.locator(".n-data-table-tbody .n-button:has-text('编辑')").first
        if edit_btn.is_visible():
            edit_btn.click()
            page.wait_for_timeout(1000)
            screenshot(page, "14_users_edit_modal")
            modal = page.locator(".n-modal").first
            if modal.is_visible():
                print("  ✅ 编辑用户弹框打开")
                # 验证密码字段为空（不回填）
                pwd_input = page.locator(".n-modal input[type='password']").first
                if pwd_input.is_visible():
                    pwd_value = pwd_input.input_value()
                    if pwd_value == "":
                        print("  ✅ 编辑用户时密码字段为空（正确行为）")
                    else:
                        log_issue("Users", "编辑用户时密码字段预填了值（安全问题）", "BUG")
                close_btn = page.locator(".n-modal .n-base-icon-close, button:has-text('取消')").first
                if close_btn.is_visible():
                    close_btn.click()


def test_nav_sidebar(page: Page):
    """测试侧边导航栏"""
    print("\n=== Navigation Sidebar ===")
    page.goto(f"{BASE_URL}/dashboard")
    wait_page_load(page)

    # 检查导航菜单项
    nav_items = page.locator(".n-menu-item, .n-layout-sider .n-menu-item-content").all()
    print(f"  导航菜单项数量: {len(nav_items)}")
    if len(nav_items) == 0:
        log_issue("Navigation", "侧边导航栏菜单项为空", "BUG")

    # 检查 Logo/标题
    logo = page.locator(".n-layout-sider img, .n-layout-sider .logo, header .logo").first
    print(f"  Logo 可见: {logo.is_visible()}")

    # 测试折叠侧边栏（如果支持）
    collapse_trigger = page.locator("[class*='collapse-trigger'], .n-layout-sider__collapse-trigger").first
    if collapse_trigger.is_visible():
        collapse_trigger.click()
        page.wait_for_timeout(500)
        screenshot(page, "00_nav_collapsed")
        collapse_trigger.click()
        page.wait_for_timeout(500)


def test_404_page(page: Page):
    """测试404页面"""
    print("\n=== 404 Page ===")
    page.goto(f"{BASE_URL}/nonexistent-page-xyz")
    page.wait_for_timeout(2000)
    screenshot(page, "15_404_page")

    # 检查是否有404处理
    url = page.url
    content = page.content()
    if "404" in content or "not found" in content.lower() or url != f"{BASE_URL}/nonexistent-page-xyz":
        print("  ✅ 404/重定向处理存在")
    else:
        log_issue("404", "访问不存在路由未出现404提示也未重定向", "WARN")


def test_application_detail_empty(page: Page):
    """测试应用详情页（无数据状态）"""
    print("\n=== Application Detail (empty) ===")
    # 用一个不存在的ID测试错误处理
    page.goto(f"{BASE_URL}/applications/99999")
    wait_page_load(page)
    screenshot(page, "03b_application_detail_notfound")

    content = page.content()
    if "404" in content or "not found" in content.lower() or "不存在" in content:
        print("  ✅ 应用不存在时有适当错误提示")
    else:
        log_issue("Application Detail", "访问不存在的应用ID没有错误提示，页面可能空白", "WARN")


def test_login_validation(page: Page):
    """测试登录页面表单验证"""
    print("\n=== Login Validation ===")
    page.goto(f"{BASE_URL}/login")
    wait_page_load(page)

    # 测试空用户名
    username_input = page.locator("input[type='text'], input[placeholder*='用户名']").first
    password_input = page.locator("input[type='password']").first
    login_btn = page.locator("button[type='submit'], button:has-text('登录')").first

    # 只填密码，不填用户名
    if password_input.is_visible():
        password_input.fill("somepassword")
        login_btn.click()
        page.wait_for_timeout(800)
        screenshot(page, "01b_login_empty_username")
        error = page.locator(".n-form-item-feedback--error, .n-input--error").first
        if error.is_visible():
            print("  ✅ 用户名为空时有验证提示")
        else:
            log_issue("Login", "用户名为空提交登录时无验证提示", "WARN")

    # 测试错误密码
    if username_input.is_visible() and password_input.is_visible():
        username_input.fill("admin")
        password_input.fill("wrongpassword")
        login_btn.click()
        page.wait_for_timeout(2000)
        screenshot(page, "01c_login_wrong_password")
        error = page.locator(".n-alert, .n-message, text=密码错误, text=用户名或密码错误").first
        if error.is_visible():
            print("  ✅ 错误密码有提示")
        else:
            log_issue("Login", "输入错误密码后无错误提示", "WARN")


def check_console_errors(page: Page, page_name: str):
    """检查页面 console 错误"""
    errors = []
    page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
    return errors


def main():
    print("=" * 60)
    print("前端测试开始")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )

        # 收集 console 错误
        console_errors = []
        page = context.new_page()
        page.on("console", lambda msg: console_errors.append(f"[{msg.type.upper()}] {msg.text}") if msg.type in ["error", "warn"] else None)
        page.on("pageerror", lambda err: console_errors.append(f"[PAGE_ERROR] {err}"))

        # 1. 登录
        logged_in = login(page)
        if not logged_in:
            print("\n❌ 无法登录，测试终止")
            browser.close()
            return

        # 2. 测试各页面（每个独立try/except防止单个失败中断所有测试）
        tests = [
            test_login_validation,
            test_nav_sidebar,
            test_dashboard,
            test_applications,
            test_application_detail_empty,
            test_recording,
            test_testcases,
            test_replay,
            test_replay_history,
            test_results,
            test_suites,
            test_schedule,
            test_compare,
            test_settings,
            test_ci,
            test_users,
            test_404_page,
        ]
        for test_fn in tests:
            try:
                test_fn(page)
            except Exception as e:
                fn_name = test_fn.__name__
                log_issue(fn_name, f"测试函数崩溃: {e}", "BUG")
                print(f"  ⚠️  {fn_name} 崩溃: {e}")
                try:
                    screenshot(page, f"crash_{fn_name}")
                except Exception:
                    pass

        browser.close()

    # 输出测试报告
    print("\n" + "=" * 60)
    print("测试完成 - 问题汇总")
    print("=" * 60)

    if ISSUES:
        bugs = [i for i in ISSUES if "[BUG]" in i]
        warns = [i for i in ISSUES if "[WARN]" in i]
        print(f"\n🔴 BUG ({len(bugs)} 个):")
        for b in bugs:
            print(f"  {b}")
        print(f"\n🟡 WARN ({len(warns)} 个):")
        for w in warns:
            print(f"  {w}")
    else:
        print("✅ 未发现明显问题")

    if console_errors:
        print(f"\n🔧 Console 错误/警告 ({len(console_errors)} 条):")
        for e in console_errors[:20]:
            print(f"  {e}")

    print(f"\n📂 截图保存于: {SCREENSHOT_DIR}")
    print(f"总截图数: {len(os.listdir(SCREENSHOT_DIR))}")

    # 写入报告文件
    with open("/tmp/test_report.txt", "w") as f:
        f.write("前端测试报告\n" + "=" * 60 + "\n\n")
        f.write("问题清单:\n")
        for issue in ISSUES:
            f.write(f"  {issue}\n")
        f.write("\nConsole错误:\n")
        for e in console_errors[:30]:
            f.write(f"  {e}\n")


if __name__ == "__main__":
    main()
