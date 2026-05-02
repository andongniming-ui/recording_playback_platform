#!/usr/bin/env python3
"""验证所有修复是否生效"""
import os
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5173"
SCREENSHOT_DIR = "/tmp/fix_screenshots"
RESULTS = []
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def ok(msg): RESULTS.append(f"✅ {msg}"); print(f"  ✅ {msg}")
def fail(msg): RESULTS.append(f"❌ {msg}"); print(f"  ❌ {msg}")
def info(msg): print(f"  ℹ  {msg}")


def ss(page, name):
    page.screenshot(path=f"{SCREENSHOT_DIR}/{name}.png", full_page=True)


def login(page):
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin123")
    page.locator("button").filter(has_text="登录").click()
    page.wait_for_timeout(2000)
    return page.url


# ─── 测试 ISSUE-3: 登录后跳转到 /dashboard ──────────────────────────────────
def test_login_redirect(page):
    print("\n[ISSUE-3] 登录后应跳转到 /dashboard")
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    page.locator("input[type='text']").first.fill("admin")
    page.locator("input[type='password']").first.fill("admin123")
    page.locator("button").filter(has_text="登录").click()
    page.wait_for_timeout(2000)
    ss(page, "01_login_redirect")
    if "/dashboard" in page.url:
        ok("登录后跳转到 /dashboard")
    else:
        fail(f"登录后跳转到 {page.url}，期望 /dashboard")


# ─── 测试 ISSUE-4: 404 页面 ─────────────────────────────────────────────────
def test_404_page(page):
    print("\n[ISSUE-4] 访问不存在路由应显示 404 页面")
    page.goto(f"{BASE_URL}/this-page-does-not-exist-xyz")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    ss(page, "02_404_page")
    content = page.content()
    if "404" in content or "页面不存在" in content or "not found" in content.lower():
        ok("404 页面正常显示")
    else:
        fail(f"访问不存在路由未出现 404 页面，URL={page.url}")


# ─── 测试 BUG-1: 新增应用空表单应触发验证 ─────────────────────────────────────
def test_app_form_validation(page):
    print("\n[BUG-1] 新增应用空表单提交应触发验证")
    page.goto(f"{BASE_URL}/applications")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    # 记录当前应用数量
    rows_before = len(page.locator(".n-data-table-tbody .n-data-table-tr").all())
    info(f"修复前应用行数: {rows_before}")

    # 找新增按钮
    add_btn = page.locator(".n-button").filter(has_text="+").first
    if not add_btn.is_visible():
        add_btn = page.locator("button:has-text('新增应用')").first
    add_btn.click()
    page.wait_for_timeout(800)

    # 直接点保存（空表单）
    save_btn = page.locator(".n-modal button:has-text('保存')").first
    if save_btn.is_visible():
        save_btn.click()
        page.wait_for_timeout(1000)
        ss(page, "03_app_validation")

        # 检查弹框是否仍然打开（验证生效则不关闭）
        modal = page.locator(".n-modal").first
        if modal.is_visible():
            # 检查有无错误提示
            errors = page.locator(".n-form-item-feedback--error").all()
            if len(errors) > 0:
                ok(f"空表单触发验证，显示 {len(errors)} 个错误提示")
            else:
                fail("弹框未关闭但未显示错误提示（可能验证无提示）")
        else:
            # 弹框关闭了，说明提交成功了（验证未生效）
            rows_after = len(page.locator(".n-data-table-tbody .n-data-table-tr").all())
            fail(f"空表单仍可提交成功！应用行数 {rows_before} → {rows_after}")
            return

        # 关闭弹框
        page.locator(".n-modal .n-base-icon-close").first.click()
        page.wait_for_timeout(500)
    else:
        fail("保存按钮不可见")


# ─── 测试 BUG-2: 新增用户空表单应触发验证 ─────────────────────────────────────
def test_user_form_validation(page):
    print("\n[BUG-2] 新增用户空表单提交应触发验证")
    page.goto(f"{BASE_URL}/users")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    rows_before = len(page.locator(".n-data-table-tbody .n-data-table-tr").all())
    info(f"修复前用户行数: {rows_before}")

    add_btn = page.locator("button:has-text('新增用户')").first
    add_btn.click()
    page.wait_for_timeout(800)

    # 清空用户名，直接点保存
    username_input = page.locator(".n-modal input[type='text']").first
    if username_input.is_visible():
        username_input.fill("")

    save_btn = page.locator(".n-modal button:has-text('保存')").first
    save_btn.click()
    page.wait_for_timeout(1000)
    ss(page, "04_user_validation")

    modal = page.locator(".n-modal").first
    if modal.is_visible():
        errors = page.locator(".n-form-item-feedback--error").all()
        if len(errors) > 0:
            ok(f"空用户名触发验证，显示 {len(errors)} 个错误提示")
        else:
            fail("弹框未关闭但未显示错误提示")
        page.locator(".n-modal .n-base-icon-close").first.click()
        page.wait_for_timeout(500)
    else:
        rows_after = len(page.locator(".n-data-table-tbody .n-data-table-tr").all())
        fail(f"空用户名仍可提交！用户行数 {rows_before} → {rows_after}")


# ─── 测试 Opt-6: Dashboard 饼图空状态 ────────────────────────────────────────
def test_dashboard_pie_empty(page):
    print("\n[Opt-6] Dashboard 饼图空状态")
    page.goto(f"{BASE_URL}/dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    ss(page, "05_dashboard_pie")

    empty = page.locator(".n-empty").first
    if empty.is_visible():
        ok("饼图区域空状态正常显示 n-empty")
    else:
        # 可能有数据，也正常
        charts = page.locator("canvas").all()
        if len(charts) >= 2:
            ok("有图表数据，无需空状态（正常）")
        else:
            fail("饼图区域既无数据也无空状态提示")


# ─── 测试 Opt-7: 应用名称列空值显示 ─────────────────────────────────────────
def test_app_name_fallback(page):
    print("\n[Opt-7] 应用名称为空时显示 '—'")
    page.goto(f"{BASE_URL}/applications")
    page.wait_for_load_state("networkidle")
    ss(page, "06_app_list_names")
    # 找名称列
    name_cells = page.locator(".n-data-table-td:nth-child(2) .n-button").all()
    info(f"名称列按钮数: {len(name_cells)}")
    empty_names = [c for c in name_cells if c.inner_text().strip() == ""]
    if len(empty_names) == 0:
        ok("应用名称列无空白（空值显示 '—' 或所有行都有名称）")
    else:
        fail(f"仍有 {len(empty_names)} 个应用名称显示为空白")


# ─── 测试 Opt-8: 未挂载数量为0时不显示红色 ──────────────────────────────────
def test_offline_count_color(page):
    print("\n[Opt-8] 未挂载数量为0时不显示红色")
    page.goto(f"{BASE_URL}/applications")
    page.wait_for_load_state("networkidle")
    # 找"未挂载"统计卡片中的 span 颜色
    offline_span = page.locator(".n-statistic").filter(has_text="未挂载").locator("span").first
    if offline_span.is_visible():
        color = offline_span.evaluate("el => el.style.color")
        info(f"未挂载数量 color: {color!r}")
        if "#d03050" in color or "rgb(208, 48, 80)" in color:
            # 检查实际值
            val_text = offline_span.inner_text().strip()
            if val_text == "0":
                fail("未挂载为 0 时仍显示红色")
            else:
                ok(f"未挂载为 {val_text}（非0），红色合理")
        else:
            ok("未挂载为 0 时颜色不是红色")
    else:
        info("未找到未挂载统计元素，跳过")


def main():
    print("=" * 55)
    print("修复验证测试")
    print("=" * 55)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        url = login(page)
        info(f"登录后URL: {url}")

        for fn in [
            test_login_redirect,
            test_404_page,
            test_app_form_validation,
            test_user_form_validation,
            test_dashboard_pie_empty,
            test_app_name_fallback,
            test_offline_count_color,
        ]:
            try:
                fn(page)
            except Exception as e:
                fail(f"{fn.__name__} 崩溃: {e}")

        browser.close()

    print("\n" + "=" * 55)
    passed = sum(1 for r in RESULTS if r.startswith("✅"))
    failed = sum(1 for r in RESULTS if r.startswith("❌"))
    print(f"结果: {passed} 通过 / {failed} 失败")
    for r in RESULTS:
        print(f"  {r}")


if __name__ == "__main__":
    main()
