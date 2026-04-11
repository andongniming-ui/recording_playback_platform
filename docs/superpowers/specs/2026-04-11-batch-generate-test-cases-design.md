# 批量生成测试用例 设计文档

**日期：** 2026-04-11  
**功能：** 录制中心样本治理视图 — 批量生成测试用例  

---

## 背景

录制中心的样本治理视图（样本 Group 视图）目前每行仅有一个"生成用例"按钮，只能逐条针对代表样本生成测试用例。当一次录制会话产生多个交易码时，用户需要手动逐行点击，效率低下。本功能在治理视图中新增批量生成能力。

---

## 目标

- 用户可在治理视图中勾选多行（多个交易码分组）
- 填写统一前缀后，一次性对所有选中分组的代表样本生成测试用例
- 生成前自动检测冲突（该录制是否已有对应用例），并告知用户
- 生成后展示汇总结果弹窗

---

## 整体数据流

```
用户勾选若干行（分组）
        ↓
点击"批量生成用例"按钮（无勾选时禁用）
        ↓
弹出 Modal：填写用例名称前缀
        ↓
点"检测冲突" → POST /test-cases/batch-check
  后端一次查询 TestCase.source_recording_id IN (ids)
  返回每条冲突状态
        ↓
Modal 内展示检测结果：可生成 X 条 / 已有用例将跳过 Y 条
用户点"确认生成"
        ↓
POST /test-cases/batch-from-recordings
  仅传无冲突的 recording_ids + prefix
  后端逐条生成，返回结构化结果列表
        ↓
结果汇总弹窗（成功/跳过/失败）
可点击"前往测试用例库"
```

---

## 后端设计

### 接口 1：冲突检测

```
POST /api/v1/test-cases/batch-check
权限：require_viewer
```

**请求体：**
```json
{
  "recording_ids": [1, 2, 3]
}
```

**响应：**
```json
[
  {
    "recording_id": 1,
    "transaction_code": "OPEN_ACCOUNT",
    "has_existing": false
  },
  {
    "recording_id": 2,
    "transaction_code": "CLOSE_ACCOUNT",
    "has_existing": true,
    "existing_case_id": 42,
    "existing_case_name": "POST /api/bank/service"
  }
]
```

**实现要点：**
- 一次 `SELECT` 查询 `TestCase WHERE source_recording_id IN (recording_ids)`
- 同时查 `Recording` 获取 `transaction_code`（用于展示）
- 文件：`backend/api/v1/test_cases.py`

---

### 接口 2：批量生成

```
POST /api/v1/test-cases/batch-from-recordings
权限：require_editor
```

**请求体：**
```json
{
  "recording_ids": [1, 3, 5],
  "prefix": "银行服务"
}
```

**响应：**
```json
{
  "total": 3,
  "created": 2,
  "failed": 1,
  "results": [
    { "recording_id": 1, "status": "created", "test_case_id": 101, "name": "银行服务 - OPEN_ACCOUNT" },
    { "recording_id": 3, "status": "created", "test_case_id": 102, "name": "银行服务 - FREEZE_ACCOUNT" },
    { "recording_id": 5, "status": "failed", "error": "Recording not found" }
  ]
}
```

**用例命名规则：**
- 有交易码：`{prefix} - {transaction_code}`
- 无交易码：`{prefix} - {method} {uri}`（兜底）

**实现要点：**
- 复用现有 `_fill_governance_fields` 逻辑（scene_key、governance_status、transaction_code 自动填充）
- 逐条生成，每条独立 try/except，单条失败不影响其他条
- 每条成功后立即 `commit`（逐条提交），避免单条异常导致回滚全部
- 文件：`backend/api/v1/test_cases.py`

---

### Schema 新增

文件：`backend/schemas/test_case.py`

```python
class BatchCheckRequest(BaseModel):
    recording_ids: list[int]

class BatchCheckItem(BaseModel):
    recording_id: int
    transaction_code: str | None
    has_existing: bool
    existing_case_id: int | None = None
    existing_case_name: str | None = None

class BatchFromRecordingsRequest(BaseModel):
    recording_ids: list[int]
    prefix: str

class BatchResultItem(BaseModel):
    recording_id: int
    status: str   # "created" | "failed"
    test_case_id: int | None = None
    name: str | None = None
    error: str | None = None

class BatchFromRecordingsResponse(BaseModel):
    total: int
    created: int
    failed: int
    results: list[BatchResultItem]
```

---

## 前端设计

### 文件改动

| 文件 | 改动内容 |
|------|----------|
| `frontend/src/views/recording/index.vue` | 治理表格加复选框、批量 UI、弹窗逻辑 |
| `frontend/src/api/testcases.ts` | 新增 `batchCheck`、`batchFromRecordings` 方法 |

### 表格改动

- `n-data-table` 增加 `row-key="representative_recording_id"`
- 增加 `v-model:checked-row-keys="selectedRecordingIds"`
- 操作区新增"批量生成用例"按钮，`:disabled="selectedRecordingIds.length === 0"`

### 弹窗交互流程

**步骤 1 — 前缀输入：**
```
┌─────────────────────────────────┐
│ 批量生成测试用例                  │
│ 已选 N 个分组                    │
│ 用例名称前缀: [_____________]    │
│         [取消]  [检测冲突 →]    │
└─────────────────────────────────┘
```

**步骤 2 — 冲突检测结果（在同一 Modal 内切换视图）：**
```
┌─────────────────────────────────┐
│ 冲突检测结果                     │
│ ✅ 5 条可生成                    │
│ ⚠️ 1 条已有用例（CLOSE_ACCOUNT） │
│    将自动跳过                    │
│         [返回]  [确认生成 →]    │
└─────────────────────────────────┘
```

**步骤 3 — 结果汇总弹窗（新 Modal）：**
```
┌─────────────────────────────────┐
│ 生成完成                         │
│ ✅ 成功 5 条                     │
│ ⏭️ 跳过 1 条（已有用例）         │
│ ❌ 失败 0 条                     │
│    [关闭]  [前往测试用例库 →]   │
└─────────────────────────────────┘
```

若有失败条目，结果弹窗中展示失败详情列表（recording_id + error 信息）。

---

## 边界与错误处理

| 场景 | 处理方式 |
|------|----------|
| 未勾选行点击批量按钮 | 按钮禁用，不可触发 |
| 前缀为空 | 前端校验，提示"请填写前缀" |
| 检测时 recording 已被删除 | batch-check 返回该条 `has_existing: false`，生成时 batch-from-recordings 该条返回 `status: "failed"` |
| 全部为冲突（无可生成） | 步骤 2 提示"所有选中分组均已有对应用例，无需重复生成"，隐藏确认按钮 |
| 网络错误 | 弹窗内显示错误信息，不关闭弹窗 |

---

## 不在本次范围内

- 批量生成后自动加入 Suite
- 生成用例的 governance_status 自定义（沿用录制的原始状态）
- 分页跨页全选
