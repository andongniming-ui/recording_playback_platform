# 测试用例详情页编辑能力设计

**日期**：2026-04-12  
**范围**：`frontend/src/views/testcases/detail.vue`（仅前端改动，无需后端变更）

---

## 背景

当前测试用例详情页（`/testcases/:id`）只展示数据，没有任何编辑入口。要修改状态或治理状态，用户必须退回列表页点击"编辑"按钮，操作路径过长。

---

## 目标

在详情页提供两种编辑能力：
1. **完整编辑**：通过侧边抽屉修改所有字段
2. **治理状态快捷切换**：在描述卡片内一键切换治理状态，无需打开抽屉

---

## 设计

### 1. 顶部"编辑"按钮

- 位置：现有按钮栏（刷新、来源录制、发起回放、克隆…）中插入"编辑"按钮
- 权限：仅 `admin` / `editor` 角色可见（与现有 `canEdit` 逻辑一致）
- 行为：点击后打开右侧抽屉（`n-drawer`）

### 2. 完整编辑抽屉

抽屉宽度 640px，表单字段：

| 字段 | 组件 | 说明 |
|------|------|------|
| 用例名称 | `n-input` | 必填 |
| 描述 | `n-input` (textarea) | 选填 |
| 状态 | `n-select` | 草稿 / 激活 / 已废弃 |
| 治理状态 | `n-select` | 原始 / 候选 / 已批准 / 已拒绝 / 已归档 |
| 交易码 | `n-input` | 选填 |
| 请求方法 | `n-select` | GET/POST/PUT/DELETE/PATCH |
| 请求 URI | `n-input` | 必填 |
| 请求 Headers | `n-input` (textarea, monospace) | JSON 格式 |
| 请求 Body | `n-input` (textarea, monospace) | JSON/XML/文本 |
| 断言规则 | `n-input` (textarea, monospace) | JSON 格式 |

**打开时**：用当前 `testCase` 数据预填所有字段。  
**保存时**：调用 `testCaseApi.update(caseId, payload)`，成功后关闭抽屉并重新调用 `loadPage()` 刷新数据。

### 3. 治理状态快捷切换

- 位置：`n-descriptions` 中"治理状态"行，当前值文字右侧
- 组件：`n-dropdown`，触发器为小号"切换"按钮
- 选项：所有五种治理状态（含当前状态，当前状态标为 disabled 或高亮提示）
- 权限：仅 `canEdit` 可见
- 行为：选择后调用 `testCaseApi.update(caseId, { governance_status: newStatus })`，成功后刷新页面数据，通过 `message.success` 提示

---

## 数据流

```
用户点击"编辑" → 打开抽屉（预填数据）
用户修改字段 → 点击"保存" → PUT /test-cases/:id → loadPage() 刷新

用户点击"切换"下拉 → 选择新状态 → PUT /test-cases/:id { governance_status } → loadPage() 刷新
```

---

## 不在范围内

- 后端 API 无需变更（`PUT /test-cases/:id` 已支持所有字段）
- 不修改列表页（`index.vue`）
- 不添加字段级校验（与列表页编辑行为保持一致）
