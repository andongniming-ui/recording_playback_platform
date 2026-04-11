# 回放高级配置功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 arex-recorder 回放功能中补全忽略字段、差异规则、断言规则、请求头转换等高级配置，对齐 arex-platform 的能力。

**Architecture:** 后端补全 4 个缺失字段（`ignore_fields`、`delay_ms`、`repeat_count`、`header_transforms`），executor 读取并应用；前端回放表单拆分为"基础配置"+"高级配置"两段，用 n-collapse 折叠分组。

**Tech Stack:** Python/FastAPI/SQLAlchemy（后端），Vue3/NaiveUI（前端），SQLite（ALTER TABLE 迁移）

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/models/replay.py` | 修改 | 新增 4 个 SQLAlchemy 列 |
| `backend/schemas/replay.py` | 修改 | `ReplayJobCreate`/`ReplayJobOut` 新增字段 |
| `backend/main.py` | 修改 | `_migrate_db()` 追加 4 条 ALTER TABLE |
| `backend/api/v1/replays.py` | 修改 | `create_replay_job` 写入新字段 |
| `backend/core/replay_executor.py` | 修改 | 应用 ignore_fields/delay_ms/repeat_count/header_transforms |
| `backend/tests/test_replay.py` | 修改 | 新增字段测试 |
| `frontend/src/views/replay/index.vue` | 修改 | 添加高级配置折叠面板及所有控件 |

---

## Task 1：后端 Model 新增 4 列

**Files:**
- Modify: `backend/models/replay.py`

- [ ] **Step 1: 在 `ReplayJob` 末尾添加 4 个新列**

在 `backend/models/replay.py` 中，在 `retry_count` 列之后追加：

```python
    # 高级回放配置
    ignore_fields: Mapped[str | None] = mapped_column(Text)          # JSON list of field names
    delay_ms: Mapped[int] = mapped_column(Integer, default=0)        # ms between requests
    repeat_count: Mapped[int] = mapped_column(Integer, default=1)    # repeat each recording N times
    header_transforms: Mapped[str | None] = mapped_column(Text)      # JSON list of {type,key,value}
```

- [ ] **Step 2: 验证文件语法无误**

```bash
cd /home/test/arex-recorder/backend && python3 -c "from models.replay import ReplayJob, ReplayResult; print('OK')"
```

预期输出：`OK`

- [ ] **Step 3: 提交**

```bash
cd /home/test/arex-recorder && git add backend/models/replay.py && git commit -m "feat: add ignore_fields, delay_ms, repeat_count, header_transforms to ReplayJob model"
```

---

## Task 2：Schema 新增字段

**Files:**
- Modify: `backend/schemas/replay.py`

- [ ] **Step 1: 在 `ReplayJobCreate` 中添加字段**

在 `backend/schemas/replay.py` 的 `ReplayJobCreate` 类末尾，`smart_noise_reduction` 字段之后追加：

```python
    ignore_fields: Optional[List[str]] = None      # 忽略字段名列表，diff 时跳过
    delay_ms: int = 0                              # 请求间隔（毫秒）
    repeat_count: int = 1                          # 每条录制重复回放次数
    header_transforms: Optional[str] = None        # JSON，请求头转换规则列表
```

- [ ] **Step 2: 在 `ReplayJobOut` 中添加相同字段**

在 `ReplayJobOut` 类末尾追加：

```python
    ignore_fields: Optional[List[str]] = None
    delay_ms: int = 0
    repeat_count: int = 1
    header_transforms: Optional[str] = None
```

- [ ] **Step 3: 验证 schema 可导入**

```bash
cd /home/test/arex-recorder/backend && python3 -c "from schemas.replay import ReplayJobCreate, ReplayJobOut; print('OK')"
```

预期输出：`OK`

- [ ] **Step 4: 提交**

```bash
cd /home/test/arex-recorder && git add backend/schemas/replay.py && git commit -m "feat: add replay advanced fields to ReplayJobCreate and ReplayJobOut schemas"
```

---

## Task 3：数据库迁移

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: 在 `_migrate_db()` 的 `migrations` 列表末尾追加 4 条**

在 `backend/main.py` 的 `_migrate_db` 函数中，`migrations` 列表末尾追加：

```python
        "ALTER TABLE replay_job ADD COLUMN ignore_fields TEXT",
        "ALTER TABLE replay_job ADD COLUMN delay_ms INTEGER DEFAULT 0",
        "ALTER TABLE replay_job ADD COLUMN repeat_count INTEGER DEFAULT 1",
        "ALTER TABLE replay_job ADD COLUMN header_transforms TEXT",
```

- [ ] **Step 2: 验证语法**

```bash
cd /home/test/arex-recorder/backend && python3 -c "import main; print('OK')"
```

预期输出：`OK`

- [ ] **Step 3: 提交**

```bash
cd /home/test/arex-recorder && git add backend/main.py && git commit -m "feat: migrate replay_job table with 4 new columns"
```

---

## Task 4：API 写入新字段

**Files:**
- Modify: `backend/api/v1/replays.py`

- [ ] **Step 1: 在 `create_replay_job` 的 `ReplayJob(...)` 构造中追加字段**

找到 `backend/api/v1/replays.py` 中创建 `job = ReplayJob(...)` 的代码块（约第 60-75 行），在 `retry_count=body.retry_count,` 之后追加：

```python
        ignore_fields=json.dumps(body.ignore_fields) if body.ignore_fields else None,
        delay_ms=body.delay_ms,
        repeat_count=body.repeat_count,
        header_transforms=body.header_transforms,
```

- [ ] **Step 2: 验证导入正常**

```bash
cd /home/test/arex-recorder/backend && python3 -c "from api.v1 import replays; print('OK')"
```

预期输出：`OK`

- [ ] **Step 3: 提交**

```bash
cd /home/test/arex-recorder && git add backend/api/v1/replays.py && git commit -m "feat: write ignore_fields, delay_ms, repeat_count, header_transforms to ReplayJob on create"
```

---

## Task 5：Executor 应用新字段

**Files:**
- Modify: `backend/core/replay_executor.py`

这是改动最多的文件，分 4 个小步骤。

- [ ] **Step 1: 在 `run_replay_job` 中读取 `ignore_fields` 并合并到 `base_ignore_fields`**

在 `replay_executor.py` 的 `run_replay_job` 函数里，找到这段代码（约 154-160 行）：

```python
    base_ignore_fields = _load_json_value(
        app.default_ignore_fields if app else None,
        f"application {resolved_application_id} default_ignore_fields",
        default=[],
    )
    if not isinstance(base_ignore_fields, list):
        base_ignore_fields = []
```

在该段**之后**追加：

```python
    # 合并 job 级 ignore_fields
    job_ignore_fields = _load_json_value(
        job.ignore_fields, f"replay job {job_id} ignore_fields", default=[]
    )
    if isinstance(job_ignore_fields, list):
        base_ignore_fields.extend(job_ignore_fields)
```

- [ ] **Step 2: 在 `run_replay_job` 中读取 `repeat_count`，将 case_ids 列表乘以 N**

找到（约 183-184 行）：

```python
    semaphore = asyncio.Semaphore(job.concurrency)
```

在这行**之前**追加：

```python
    # 流量放大：将每条 case 重复回放 repeat_count 次
    job_repeat_count = max(1, job.repeat_count or 1)
    if job_repeat_count > 1:
        case_ids = case_ids * job_repeat_count

```

同时，`job.total` 已在前面设置为 `len(case_ids)`（这是原始 case 数），需要在乘法之后更新 total。找到：

```python
        job.status = "RUNNING"
        job.total = len(case_ids)
        job.started_at = datetime.now(timezone.utc)
        await db.commit()
```

将这段改为（注意：此时 `case_ids` 还未被乘，`job.total` 要在乘法后更新，需在 DB commit 之后再更新一次）。实际上更简单的做法是：在 `job.status = "RUNNING"` 这块里**不改**，而是在乘法之后用一个新的 DB 会话更新 `job.total`：

```python
    # 流量放大：将每条 case 重复回放 repeat_count 次
    job_repeat_count = max(1, job.repeat_count or 1)
    if job_repeat_count > 1:
        case_ids = case_ids * job_repeat_count
        # 更新 total 为实际执行数
        async with database.async_session_factory() as db:
            job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            job_row = job_result.scalar_one_or_none()
            if job_row:
                job_row.total = len(case_ids)
                await db.commit()

```

- [ ] **Step 3: 在 `_run_one` 中添加 `delay_ms` 和 `header_transforms` 参数，并应用**

找到 `_run_one` 函数定义（约 192 行），在其最开头 `async with semaphore:` 之前添加 sleep：

```python
    async def _run_one(case_id: int):
        nonlocal done_count, passed, failed, errored
        # 请求间隔（在信号量外等待，避免阻塞并发槽）
        if job.delay_ms and job.delay_ms > 0:
            await asyncio.sleep(job.delay_ms / 1000.0)
        case = case_map.get(case_id)
        async with semaphore:
```

在 `_execute_single` 的两处调用（首次调用和重试调用）中，各追加参数：

```python
                header_transforms=_load_json_value(job.header_transforms, f"replay job {job_id} header_transforms", default=[]),
```

即两处 `_execute_single(...)` 调用都需要加这一行。

- [ ] **Step 4: 在 `_execute_single` 函数签名中添加 `header_transforms` 参数，并在 headers 构建后应用**

函数签名（约 293 行）末尾追加参数：

```python
    header_transforms=None,
```

在 `headers` 构建完成后（约 358 行，`host`/`content-length` 过滤之后），追加转换逻辑：

```python
    # 应用 header_transforms
    if header_transforms:
        for transform in header_transforms:
            t_type = transform.get("type", "")
            t_key = transform.get("key", "")
            t_value = transform.get("value", "")
            if not t_key:
                continue
            if t_type == "remove":
                headers.pop(t_key, None)
            elif t_type in ("replace", "add"):
                headers[t_key] = t_value
```

- [ ] **Step 5: 验证语法**

```bash
cd /home/test/arex-recorder/backend && python3 -c "from core.replay_executor import run_replay_job; print('OK')"
```

预期输出：`OK`

- [ ] **Step 6: 提交**

```bash
cd /home/test/arex-recorder && git add backend/core/replay_executor.py && git commit -m "feat: apply ignore_fields, delay_ms, repeat_count, header_transforms in replay executor"
```

---

## Task 6：后端测试

**Files:**
- Modify: `backend/tests/test_replay.py`

- [ ] **Step 1: 新增 `ignore_fields` 字段测试**

在 `test_replay.py` 末尾追加：

```python
def test_create_replay_job_with_ignore_fields(client, admin_headers, tc_payload):
    """ignore_fields 能通过 API 保存并回显。"""
    tc = _create_test_case(client, admin_headers, tc_payload)
    resp = _create_replay_job(
        client, admin_headers, [tc["id"]],
        ignore_fields=["timestamp", "request_id"],
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["ignore_fields"] == ["timestamp", "request_id"]


def test_create_replay_job_with_delay_ms(client, admin_headers, tc_payload):
    """delay_ms 能通过 API 保存并回显。"""
    tc = _create_test_case(client, admin_headers, tc_payload)
    resp = _create_replay_job(
        client, admin_headers, [tc["id"]],
        delay_ms=100,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["delay_ms"] == 100


def test_create_replay_job_with_repeat_count(client, admin_headers, tc_payload):
    """repeat_count 能通过 API 保存并回显。"""
    tc = _create_test_case(client, admin_headers, tc_payload)
    resp = _create_replay_job(
        client, admin_headers, [tc["id"]],
        repeat_count=3,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["repeat_count"] == 3


def test_create_replay_job_with_header_transforms(client, admin_headers, tc_payload):
    """header_transforms 能通过 API 保存并回显。"""
    import json as _json
    tc = _create_test_case(client, admin_headers, tc_payload)
    transforms = _json.dumps([{"type": "replace", "key": "Content-Type", "value": "application/json"}])
    resp = _create_replay_job(
        client, admin_headers, [tc["id"]],
        header_transforms=transforms,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["header_transforms"] == transforms
```

- [ ] **Step 2: 运行新增测试确认全部通过**

```bash
cd /home/test/arex-recorder/backend && python3 -m pytest tests/test_replay.py::test_create_replay_job_with_ignore_fields tests/test_replay.py::test_create_replay_job_with_delay_ms tests/test_replay.py::test_create_replay_job_with_repeat_count tests/test_replay.py::test_create_replay_job_with_header_transforms -v
```

预期：4 个测试全部 PASS。

- [ ] **Step 3: 运行全量测试确认无回归**

```bash
cd /home/test/arex-recorder/backend && python3 -m pytest tests/ -x -q 2>&1 | tail -20
```

预期：所有已有测试通过，failed=0。

- [ ] **Step 4: 提交**

```bash
cd /home/test/arex-recorder && git add backend/tests/test_replay.py && git commit -m "test: add tests for replay advanced fields (ignore_fields, delay_ms, repeat_count, header_transforms)"
```

---

## Task 7：前端回放表单改造

**Files:**
- Modify: `frontend/src/views/replay/index.vue`

这是改动最大的文件，完整替换表单部分。

- [ ] **Step 1: 更新 `launchForm` ref 的类型和默认值**

在 `<script setup>` 中，将 `launchForm` 的定义替换为：

```typescript
const launchForm = ref({
  name: '',
  application_id: null as number | null,
  case_ids: [] as number[],
  concurrency: 5,
  timeout_ms: 5000,
  // 高级配置
  ignore_fields: [] as string[],
  smart_noise_reduction: false,
  diff_rules: [] as { type: string; path: string; tolerance?: number; pattern?: string }[],
  assertions: [] as { type: string; path?: string; value?: string; pattern?: string }[],
  header_transforms: [] as { type: 'replace' | 'add' | 'remove'; key: string; value?: string }[],
  perf_threshold_ms: null as number | null,
  delay_ms: 0,
  repeat_count: 1,
  retry_count: 0,
  target_host: '',
  webhook_url: '',
  notify_type: null as string | null,
})
```

- [ ] **Step 2: 添加辅助函数和常量（在 `launchForm` 之后）**

```typescript
const diffRuleTypeOptions = [
  { label: '忽略字段', value: 'ignore' },
  { label: '数值容差', value: 'numeric_tolerance' },
  { label: '正则匹配', value: 'regex_match' },
  { label: '仅比较类型', value: 'type_only' },
]

const assertionTypeOptions = [
  { label: 'HTTP 状态码等于', value: 'status_code_eq' },
  { label: '响应体不为空', value: 'response_not_empty' },
  { label: 'JSON 字段等于', value: 'json_path_eq' },
  { label: 'JSON 字段包含', value: 'json_path_contains' },
  { label: 'JSON 字段存在', value: 'json_path_exists' },
  { label: 'JSON 字段匹配正则', value: 'json_path_regex' },
  { label: '差异分数不超过', value: 'diff_score_lte' },
]

const headerTransformTypeOptions = [
  { label: '替换', value: 'replace' },
  { label: '添加', value: 'add' },
  { label: '删除', value: 'remove' },
]

const notifyTypeOptions = [
  { label: '钉钉', value: 'dingtalk' },
  { label: '企业微信', value: 'wecom' },
  { label: '通用 JSON', value: 'generic' },
]

const headerPresets = [
  { label: 'Content-Type: XML',  type: 'replace' as const, key: 'Content-Type', value: 'application/xml' },
  { label: 'Content-Type: JSON', type: 'replace' as const, key: 'Content-Type', value: 'application/json' },
  { label: 'Accept: JSON',       type: 'replace' as const, key: 'Accept',       value: 'application/json' },
  { label: '移除 Cookie',        type: 'remove'  as const, key: 'Cookie',       value: '' },
  { label: '移除 Authorization', type: 'remove'  as const, key: 'Authorization',value: '' },
]

function addDiffRule() {
  launchForm.value.diff_rules.push({ type: 'ignore', path: '' })
}
function removeDiffRule(i: number) {
  launchForm.value.diff_rules.splice(i, 1)
}
function addAssertion() {
  launchForm.value.assertions.push({ type: 'response_not_empty' })
}
function removeAssertion(i: number) {
  launchForm.value.assertions.splice(i, 1)
}
function addHeaderTransform() {
  launchForm.value.header_transforms.push({ type: 'replace', key: '', value: '' })
}
function removeHeaderTransform(i: number) {
  launchForm.value.header_transforms.splice(i, 1)
}
function applyHeaderPreset(preset: typeof headerPresets[0]) {
  const existing = launchForm.value.header_transforms.find(
    t => t.key === preset.key && t.type === preset.type,
  )
  if (existing) {
    existing.value = preset.value
  } else {
    launchForm.value.header_transforms.push({ type: preset.type, key: preset.key, value: preset.value })
  }
}
function needsAssertionPath(type: string) {
  return ['json_path_eq', 'json_path_contains', 'json_path_exists', 'json_path_regex'].includes(type)
}
function needsAssertionValue(type: string) {
  return ['status_code_eq', 'json_path_eq', 'json_path_contains', 'diff_score_lte'].includes(type)
}
```

- [ ] **Step 3: 更新 `launchReplay` 函数，序列化新字段**

将 `launchReplay` 函数中构建 payload 的部分替换为：

```typescript
async function launchReplay() {
  launching.value = true
  try {
    const f = launchForm.value
    const payload: Record<string, any> = {
      name: f.name || undefined,
      application_id: f.application_id || undefined,
      case_ids: f.case_ids,
      concurrency: f.concurrency,
      timeout_ms: f.timeout_ms,
    }
    if (f.ignore_fields.length) payload.ignore_fields = f.ignore_fields
    if (f.smart_noise_reduction) payload.smart_noise_reduction = true
    if (f.diff_rules.length) payload.diff_rules = JSON.stringify(f.diff_rules)
    if (f.assertions.length) payload.assertions = JSON.stringify(f.assertions)
    if (f.header_transforms.length) payload.header_transforms = JSON.stringify(f.header_transforms)
    if (f.perf_threshold_ms) payload.perf_threshold_ms = f.perf_threshold_ms
    if (f.delay_ms > 0) payload.delay_ms = f.delay_ms
    if (f.repeat_count > 1) payload.repeat_count = f.repeat_count
    if (f.retry_count > 0) payload.retry_count = f.retry_count
    if (f.target_host) payload.target_host = f.target_host
    if (f.webhook_url) payload.webhook_url = f.webhook_url
    if (f.notify_type) payload.notify_type = f.notify_type

    const res = await replayApi.create(payload)
    message.success(`回放任务 #${res.data.id} 已启动`)
    f.case_ids = []
    f.name = ''
    await loadJobs()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '启动回放任务失败')
  } finally {
    launching.value = false
  }
}
```

- [ ] **Step 4: 更新 import 列表，加入 NaiveUI 新组件**

将 `<script setup>` 顶部的 import 替换为：

```typescript
import { h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NCard, NCollapse, NCollapseItem, NDataTable, NDynamicTags,
  NDrawer, NDrawerContent, NForm, NFormItem, NInput, NInputNumber,
  NSelect, NSpace, NSwitch, NTag, NText, useMessage,
} from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import { formatDateTime } from '@/utils/format'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'
```

- [ ] **Step 5: 替换 `<template>` 中的表单区域**

将模板中 `<n-card v-if="canEdit" title="发起回放">` 内的整个 `<n-form>` 块替换为以下内容：

```html
      <n-form :model="launchForm" label-placement="left" label-width="120px">
        <!-- ── 基础配置 ── -->
        <n-form-item label="所属应用">
          <n-select
            v-model:value="launchForm.application_id"
            :options="appOptions"
            clearable
            placeholder="当所选用例都属于同一应用时可留空"
            style="width: 320px"
          />
        </n-form-item>
        <n-form-item label="测试用例">
          <n-select
            v-model:value="launchForm.case_ids"
            multiple
            filterable
            :options="caseOptions"
            placeholder="请选择一个或多个测试用例"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="并发数">
          <n-input-number v-model:value="launchForm.concurrency" :min="1" :max="50" />
        </n-form-item>
        <n-form-item label="超时时间(ms)">
          <n-input-number v-model:value="launchForm.timeout_ms" :min="500" :max="60000" :step="500" />
        </n-form-item>
        <n-form-item label="任务名称">
          <n-input v-model:value="launchForm.name" placeholder="可选，便于识别" style="width: 320px" />
        </n-form-item>

        <!-- ── 高级配置（折叠） ── -->
        <n-collapse style="margin-bottom: 12px">
          <n-collapse-item title="高级配置" name="advanced">
            <!-- 忽略字段 -->
            <n-form-item label="忽略字段">
              <n-space vertical style="width:100%">
                <n-dynamic-tags v-model:value="launchForm.ignore_fields" />
                <n-text depth="3" style="font-size:12px">回放 diff 时跳过这些字段（如 timestamp、request_id）</n-text>
              </n-space>
            </n-form-item>

            <!-- 智能降噪 -->
            <n-form-item label="智能降噪">
              <n-space align="center">
                <n-switch v-model:value="launchForm.smart_noise_reduction" />
                <n-text depth="3" style="font-size:13px">自动忽略 30+ 常见动态字段（时间戳、UUID、Token 等）</n-text>
              </n-space>
            </n-form-item>

            <!-- 差异规则 -->
            <n-form-item label="差异规则">
              <n-space vertical style="width:100%">
                <n-space
                  v-for="(rule, i) in launchForm.diff_rules"
                  :key="i"
                  align="center"
                  wrap
                  style="background:#fafafa;padding:6px 10px;border-radius:4px;border:1px solid #e8e8e8"
                >
                  <n-select v-model:value="rule.type" :options="diffRuleTypeOptions" style="width:150px" />
                  <n-input v-model:value="rule.path" placeholder="字段路径，如 data.price" style="width:200px" />
                  <n-input-number
                    v-if="rule.type === 'numeric_tolerance'"
                    v-model:value="rule.tolerance"
                    :step="0.01" :min="0"
                    placeholder="容差"
                    style="width:100px"
                  />
                  <n-input
                    v-if="rule.type === 'regex_match'"
                    v-model:value="rule.pattern"
                    placeholder="正则表达式"
                    style="width:160px"
                  />
                  <n-button size="small" type="error" circle @click="removeDiffRule(i)">×</n-button>
                </n-space>
                <n-button size="small" dashed @click="addDiffRule">+ 添加差异规则</n-button>
                <n-text depth="3" style="font-size:12px">ignore=忽略字段　numeric_tolerance=数值容差　regex_match=正则匹配　type_only=仅比较类型</n-text>
              </n-space>
            </n-form-item>

            <!-- 断言规则 -->
            <n-form-item label="断言规则">
              <n-space vertical style="width:100%">
                <n-space
                  v-for="(rule, i) in launchForm.assertions"
                  :key="i"
                  align="center"
                  wrap
                  style="background:#fafafa;padding:6px 10px;border-radius:4px;border:1px solid #e8e8e8"
                >
                  <n-select v-model:value="rule.type" :options="assertionTypeOptions" style="width:200px" />
                  <n-input
                    v-if="needsAssertionPath(rule.type)"
                    v-model:value="rule.path"
                    placeholder="JSON 路径，如 code"
                    style="width:150px"
                  />
                  <n-input
                    v-if="needsAssertionValue(rule.type)"
                    v-model:value="rule.value"
                    :placeholder="rule.type === 'status_code_eq' ? '如 200' : '期望值'"
                    style="width:130px"
                  />
                  <n-input
                    v-if="rule.type === 'json_path_regex'"
                    v-model:value="rule.pattern"
                    placeholder="正则表达式"
                    style="width:150px"
                  />
                  <n-button size="small" type="error" circle @click="removeAssertion(i)">×</n-button>
                </n-space>
                <n-button size="small" dashed @click="addAssertion">+ 添加断言规则</n-button>
                <n-text depth="3" style="font-size:12px">断言失败时结果标记为 FAIL（即使响应体与录制一致）</n-text>
              </n-space>
            </n-form-item>

            <!-- 请求头转换 -->
            <n-form-item label="请求头转换">
              <n-space vertical style="width:100%">
                <n-space size="small" style="flex-wrap:wrap">
                  <n-tag
                    v-for="preset in headerPresets"
                    :key="preset.label"
                    size="small"
                    type="info"
                    style="cursor:pointer"
                    @click="applyHeaderPreset(preset)"
                  >
                    {{ preset.label }}
                  </n-tag>
                </n-space>
                <n-space
                  v-for="(t, i) in launchForm.header_transforms"
                  :key="i"
                  align="center"
                  wrap
                  style="background:#fafafa;padding:6px 10px;border-radius:4px;border:1px solid #e8e8e8"
                >
                  <n-select v-model:value="t.type" :options="headerTransformTypeOptions" style="width:90px" />
                  <n-input v-model:value="t.key" placeholder="Header 名" style="width:180px" />
                  <n-input
                    v-if="t.type !== 'remove'"
                    v-model:value="t.value"
                    placeholder="值"
                    style="width:220px"
                  />
                  <n-button size="small" type="error" circle @click="removeHeaderTransform(i)">×</n-button>
                </n-space>
                <n-button size="small" dashed @click="addHeaderTransform">+ 自定义请求头</n-button>
              </n-space>
            </n-form-item>

            <!-- 性能阈值 -->
            <n-form-item label="性能阈值(ms)">
              <n-input-number
                v-model:value="launchForm.perf_threshold_ms"
                :min="0"
                clearable
                placeholder="超过此耗时标记为性能失败，留空不启用"
                style="width:260px"
              />
            </n-form-item>

            <!-- 请求间隔 -->
            <n-form-item label="请求间隔(ms)">
              <n-input-number v-model:value="launchForm.delay_ms" :min="0" style="width:160px" />
            </n-form-item>

            <!-- 流量放大 -->
            <n-form-item label="流量放大">
              <n-space align="center">
                <n-input-number v-model:value="launchForm.repeat_count" :min="1" :max="100" style="width:100px" />
                <n-text depth="3" style="font-size:13px">每条录制重复回放 N 次</n-text>
              </n-space>
            </n-form-item>

            <!-- 失败重试 -->
            <n-form-item label="失败重试">
              <n-space align="center">
                <n-input-number v-model:value="launchForm.retry_count" :min="0" :max="5" style="width:100px" />
                <n-text depth="3" style="font-size:13px">失败时自动重试 N 次</n-text>
              </n-space>
            </n-form-item>

            <!-- Host 覆盖 -->
            <n-form-item label="Host 覆盖">
              <n-input v-model:value="launchForm.target_host" placeholder="留空使用应用配置的地址" style="width:320px" />
            </n-form-item>

            <!-- Webhook -->
            <n-form-item label="Webhook URL">
              <n-input v-model:value="launchForm.webhook_url" placeholder="回放完成后 POST 通知，留空不回调" style="width:320px" />
            </n-form-item>
            <n-form-item label="通知类型">
              <n-select
                v-model:value="launchForm.notify_type"
                :options="notifyTypeOptions"
                clearable
                placeholder="选择通知格式"
                style="width:200px"
              />
            </n-form-item>
          </n-collapse-item>
        </n-collapse>

        <n-form-item>
          <n-button
            type="primary"
            :loading="launching"
            :disabled="launchForm.case_ids.length === 0"
            @click="launchReplay"
          >
            开始回放
          </n-button>
        </n-form-item>
      </n-form>
```

- [ ] **Step 6: 在浏览器中验证表单正常展示**

确认：
- "高级配置"折叠面板可以展开/收起
- 忽略字段可以输入标签
- 差异规则、断言规则、请求头转换可以动态添加/删除
- 预设标签点击后会自动填入请求头转换列表
- 点击"开始回放"按钮（选择用例后）不报前端错误

- [ ] **Step 7: 提交**

```bash
cd /home/test/arex-recorder && git add frontend/src/views/replay/index.vue && git commit -m "feat: add advanced replay options form (ignore_fields, diff_rules, assertions, header_transforms, etc.)"
```

---

## 自审检查结果

**Spec coverage:**
- ✅ 后端 4 个缺失字段 → Task 1-4
- ✅ ignore_fields 传给 compute_diff → Task 5 Step 1
- ✅ delay_ms 请求间隔 → Task 5 Step 3
- ✅ repeat_count 流量放大 → Task 5 Step 2
- ✅ header_transforms 请求头转换 → Task 5 Steps 3-4
- ✅ 数据库迁移 → Task 3
- ✅ 前端表单基础配置（不变）→ Task 7
- ✅ 前端高级配置折叠面板 → Task 7
- ✅ 忽略字段 n-dynamic-tags → Task 7
- ✅ 智能降噪开关 → Task 7
- ✅ 差异规则动态列表 → Task 7
- ✅ 断言规则动态列表 → Task 7
- ✅ 请求头转换+预设 → Task 7
- ✅ 性能阈值、请求间隔、流量放大、失败重试 → Task 7
- ✅ Host 覆盖、Webhook → Task 7
- ✅ 后端测试 → Task 6

**Placeholder scan:** 无 TBD/TODO。

**Type consistency:** `launchForm.diff_rules` 中 `path` 字段在 `addDiffRule` 初始化为空字符串，与模板中 `v-model:value="rule.path"` 一致。`header_transforms` 中 `value` 为可选，模板中仅在 `type !== 'remove'` 时显示，一致。
