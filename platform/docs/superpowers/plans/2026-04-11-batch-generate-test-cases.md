# 批量生成测试用例 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在录制中心样本治理视图中，支持勾选多行分组后批量生成测试用例，并在生成前检测冲突、生成后展示汇总结果。

**Architecture:** 新增两个后端接口（`POST /test-cases/batch-check` 和 `POST /test-cases/batch-from-recordings`），前端治理视图表格增加复选框列，通过两步 Modal（前缀输入 → 冲突检测结果 → 确认生成 → 结果弹窗）完成交互。

**Tech Stack:** Python/FastAPI + SQLAlchemy（后端），Vue 3 + Naive UI（前端），pytest（后端测试）

---

## 文件改动一览

| 文件 | 类型 | 内容 |
|------|------|------|
| `backend/schemas/test_case.py` | 修改 | 新增 5 个 Pydantic Schema 类 |
| `backend/api/v1/test_cases.py` | 修改 | 新增 2 个 API 路由 |
| `backend/tests/test_test_cases.py` | 修改 | 新增 5 个测试函数 + 1 个 seeding helper |
| `frontend/src/api/testcases.ts` | 修改 | 新增 2 个 API 方法 |
| `frontend/src/views/recording/index.vue` | 修改 | 复选框、批量按钮、批量 Modal、结果 Modal |

---

## Task 1：新增后端 Schema

**Files:**
- Modify: `backend/schemas/test_case.py`

- [ ] **Step 1：在 `backend/schemas/test_case.py` 末尾追加以下 Schema 类**

  打开 `backend/schemas/test_case.py`，在 `AddToSuiteRequest` 之后追加：

  ```python
  class BatchCheckRequest(BaseModel):
      recording_ids: list[int]


  class BatchCheckItem(BaseModel):
      recording_id: int
      transaction_code: Optional[str]
      has_existing: bool
      existing_case_id: Optional[int] = None
      existing_case_name: Optional[str] = None


  class BatchFromRecordingsRequest(BaseModel):
      recording_ids: list[int]
      prefix: str


  class BatchResultItem(BaseModel):
      recording_id: int
      status: str  # "created" | "failed"
      test_case_id: Optional[int] = None
      name: Optional[str] = None
      error: Optional[str] = None


  class BatchFromRecordingsResponse(BaseModel):
      total: int
      created: int
      failed: int
      results: list[BatchResultItem]
  ```

- [ ] **Step 2：验证 Schema 文件语法正确**

  ```bash
  cd /home/test/arex-recorder/backend
  python3 -c "from schemas.test_case import BatchCheckRequest, BatchCheckItem, BatchFromRecordingsRequest, BatchResultItem, BatchFromRecordingsResponse; print('OK')"
  ```

  期望输出：`OK`

- [ ] **Step 3：Commit**

  ```bash
  git add backend/schemas/test_case.py
  git commit -m "feat: add batch check/generate schemas for test cases"
  ```

---

## Task 2：新增后端接口 `batch-check`（TDD）

**Files:**
- Modify: `backend/api/v1/test_cases.py`
- Test: `backend/tests/test_test_cases.py`

- [ ] **Step 1：在测试文件中添加 seeding helper 和 batch-check 测试**

  打开 `backend/tests/test_test_cases.py`，在文件顶部 import 区域后（`TC_PAYLOAD` 定义之前）插入：

  ```python
  import asyncio
  from sqlalchemy import select as sa_select
  from models.recording import Recording
  import database as _db_module


  def _seed_recordings(app_id: int, transaction_codes: list):
      """Seed Recording rows and return their IDs."""
      async def _run():
          ids = []
          async with _db_module.async_session_factory() as session:
              for i, code in enumerate(transaction_codes):
                  row = Recording(
                      application_id=app_id,
                      request_method="POST",
                      request_uri="/api/service",
                      request_body=f"<req><service_id>{code or 'UNKNOWN'}</service_id></req>",
                      response_status=200,
                      response_body="<response><code>0000</code></response>",
                      transaction_code=code,
                      scene_key=f"{code or 'UNKNOWN'}|POST|/api/service|success" if code else None,
                      dedupe_hash=f"batch-hash-{i}",
                      governance_status="candidate",
                  )
                  session.add(row)
              await session.commit()
              result = await session.execute(
                  sa_select(Recording).where(Recording.application_id == app_id)
              )
              ids = [r.id for r in result.scalars().all()]
          return ids
      return asyncio.get_event_loop().run_until_complete(_run())
  ```

  然后在文件末尾追加：

  ```python
  # ---------------------------------------------------------------------------
  # Batch check
  # ---------------------------------------------------------------------------

  def test_batch_check_no_conflicts(client, admin_headers, created_app):
      rec_ids = _seed_recordings(created_app["id"], ["OPEN_ACCOUNT", "CLOSE_ACCOUNT"])

      resp = client.post(
          "/api/v1/test-cases/batch-check",
          json={"recording_ids": rec_ids},
          headers=admin_headers,
      )
      assert resp.status_code == 200
      items = resp.json()
      assert len(items) == 2
      assert all(not item["has_existing"] for item in items)
      codes = {item["transaction_code"] for item in items}
      assert codes == {"OPEN_ACCOUNT", "CLOSE_ACCOUNT"}


  def test_batch_check_detects_conflict(client, admin_headers, created_app):
      rec_ids = _seed_recordings(created_app["id"], ["FREEZE_ACCOUNT", "UNFREEZE_ACCOUNT"])

      # Create a test case from rec_ids[0] to create conflict
      client.post(
          "/api/v1/test-cases/from-recording",
          json={"recording_id": rec_ids[0]},
          headers=admin_headers,
      )

      resp = client.post(
          "/api/v1/test-cases/batch-check",
          json={"recording_ids": rec_ids},
          headers=admin_headers,
      )
      assert resp.status_code == 200
      by_id = {item["recording_id"]: item for item in resp.json()}

      assert by_id[rec_ids[0]]["has_existing"] is True
      assert by_id[rec_ids[0]]["existing_case_id"] is not None
      assert by_id[rec_ids[1]]["has_existing"] is False
  ```

- [ ] **Step 2：运行测试，确认 FAIL**

  ```bash
  cd /home/test/arex-recorder/backend
  python3 -m pytest tests/test_test_cases.py::test_batch_check_no_conflicts tests/test_test_cases.py::test_batch_check_detects_conflict -v 2>&1 | tail -10
  ```

  期望：两个测试均 FAIL（接口尚未实现，404）

- [ ] **Step 3：在 `backend/api/v1/test_cases.py` 中新增 `batch-check` 路由**

  在现有 `from schemas.test_case import (` 导入列表中追加新 schema 名：

  ```python
  from schemas.test_case import (
      TestCaseCreate, TestCaseUpdate, TestCaseOut,
      TestCaseFromRecording, AddToSuiteRequest,
      BatchCheckRequest, BatchCheckItem,
      BatchFromRecordingsRequest, BatchResultItem, BatchFromRecordingsResponse,
  )
  ```

  然后在 `@router.get("/export")` 路由之前插入以下新路由：

  ```python
  @router.post("/batch-check", response_model=list[BatchCheckItem])
  async def batch_check(
      body: BatchCheckRequest,
      db: AsyncSession = Depends(get_db),
      _=Depends(require_viewer),
  ):
      """Check which recordings already have a test case (by source_recording_id)."""
      if not body.recording_ids:
          return []

      # Fetch recordings
      rec_result = await db.execute(
          select(Recording).where(Recording.id.in_(body.recording_ids))
      )
      recordings = {r.id: r for r in rec_result.scalars().all()}

      # Fetch existing test cases that reference these recordings
      tc_result = await db.execute(
          select(TestCase).where(TestCase.source_recording_id.in_(body.recording_ids))
      )
      existing_by_rec: dict[int, TestCase] = {}
      for tc in tc_result.scalars().all():
          if tc.source_recording_id not in existing_by_rec:
              existing_by_rec[tc.source_recording_id] = tc

      items = []
      for rec_id in body.recording_ids:
          rec = recordings.get(rec_id)
          existing = existing_by_rec.get(rec_id)
          items.append(BatchCheckItem(
              recording_id=rec_id,
              transaction_code=rec.transaction_code if rec else None,
              has_existing=existing is not None,
              existing_case_id=existing.id if existing else None,
              existing_case_name=existing.name if existing else None,
          ))
      return items
  ```

- [ ] **Step 4：运行测试，确认 PASS**

  ```bash
  cd /home/test/arex-recorder/backend
  python3 -m pytest tests/test_test_cases.py::test_batch_check_no_conflicts tests/test_test_cases.py::test_batch_check_detects_conflict -v 2>&1 | tail -10
  ```

  期望：`2 passed`

- [ ] **Step 5：运行全量测试，确认无回归**

  ```bash
  python3 -m pytest tests/test_test_cases.py -q 2>&1 | tail -5
  ```

  期望：所有测试 passed，0 failed

- [ ] **Step 6：Commit**

  ```bash
  git add backend/api/v1/test_cases.py backend/tests/test_test_cases.py
  git commit -m "feat: add batch-check endpoint for test case conflict detection"
  ```

---

## Task 3：新增后端接口 `batch-from-recordings`（TDD）

**Files:**
- Modify: `backend/api/v1/test_cases.py`
- Test: `backend/tests/test_test_cases.py`

- [ ] **Step 1：在测试文件末尾追加 batch-from-recordings 测试**

  ```python
  # ---------------------------------------------------------------------------
  # Batch from recordings
  # ---------------------------------------------------------------------------

  def test_batch_from_recordings_creates_cases(client, admin_headers, created_app):
      rec_ids = _seed_recordings(created_app["id"], ["OPEN_ACCOUNT", "CLOSE_ACCOUNT"])

      resp = client.post(
          "/api/v1/test-cases/batch-from-recordings",
          json={"recording_ids": rec_ids, "prefix": "银行"},
          headers=admin_headers,
      )
      assert resp.status_code == 200
      body = resp.json()
      assert body["total"] == 2
      assert body["created"] == 2
      assert body["failed"] == 0
      names = {r["name"] for r in body["results"]}
      assert "银行 - OPEN_ACCOUNT" in names
      assert "银行 - CLOSE_ACCOUNT" in names
      assert all(r["status"] == "created" for r in body["results"])


  def test_batch_from_recordings_fallback_name_when_no_transaction_code(client, admin_headers, created_app):
      rec_ids = _seed_recordings(created_app["id"], [None])  # no transaction code

      resp = client.post(
          "/api/v1/test-cases/batch-from-recordings",
          json={"recording_ids": rec_ids, "prefix": "前缀"},
          headers=admin_headers,
      )
      assert resp.status_code == 200
      body = resp.json()
      assert body["created"] == 1
      name = body["results"][0]["name"]
      assert name.startswith("前缀 - POST")


  def test_batch_from_recordings_handles_missing_recording(client, admin_headers):
      resp = client.post(
          "/api/v1/test-cases/batch-from-recordings",
          json={"recording_ids": [99999], "prefix": "test"},
          headers=admin_headers,
      )
      assert resp.status_code == 200
      body = resp.json()
      assert body["total"] == 1
      assert body["failed"] == 1
      assert body["results"][0]["status"] == "failed"
      assert "not found" in body["results"][0]["error"].lower()
  ```

- [ ] **Step 2：运行测试，确认 FAIL**

  ```bash
  cd /home/test/arex-recorder/backend
  python3 -m pytest tests/test_test_cases.py::test_batch_from_recordings_creates_cases tests/test_test_cases.py::test_batch_from_recordings_fallback_name_when_no_transaction_code tests/test_test_cases.py::test_batch_from_recordings_handles_missing_recording -v 2>&1 | tail -10
  ```

  期望：3 个测试均 FAIL（接口不存在，404）

- [ ] **Step 3：在 `backend/api/v1/test_cases.py` 中新增 `batch-from-recordings` 路由**

  在 `batch-check` 路由之后（`@router.get("/export")` 之前）插入：

  ```python
  @router.post("/batch-from-recordings", response_model=BatchFromRecordingsResponse)
  async def batch_from_recordings(
      body: BatchFromRecordingsRequest,
      db: AsyncSession = Depends(get_db),
      _=Depends(require_editor),
  ):
      """Batch create test cases from a list of recording IDs with a shared name prefix."""
      results: list[BatchResultItem] = []
      created_count = 0
      failed_count = 0

      for rec_id in body.recording_ids:
          try:
              rec_result = await db.execute(select(Recording).where(Recording.id == rec_id))
              recording = rec_result.scalar_one_or_none()
              if not recording:
                  results.append(BatchResultItem(
                      recording_id=rec_id,
                      status="failed",
                      error="Recording not found",
                  ))
                  failed_count += 1
                  continue

              # Build name: prefix + transaction_code or fallback to method + uri
              suffix = recording.transaction_code or f"{recording.request_method} {recording.request_uri}"
              name = f"{body.prefix} - {suffix}"

              tc = TestCase(**_fill_governance_fields({
                  "name": name,
                  "application_id": recording.application_id,
                  "source_recording_id": recording.id,
                  "request_method": recording.request_method,
                  "request_uri": recording.request_uri,
                  "request_headers": recording.request_headers,
                  "request_body": recording.request_body,
                  "expected_status": recording.response_status,
                  "expected_response": recording.response_body,
                  "transaction_code": recording.transaction_code,
                  "scene_key": recording.scene_key,
                  "governance_status": recording.governance_status or "candidate",
                  "status": "active",
              }))
              db.add(tc)
              await db.commit()
              await db.refresh(tc)

              results.append(BatchResultItem(
                  recording_id=rec_id,
                  status="created",
                  test_case_id=tc.id,
                  name=tc.name,
              ))
              created_count += 1

          except Exception as exc:
              await db.rollback()
              results.append(BatchResultItem(
                  recording_id=rec_id,
                  status="failed",
                  error=str(exc),
              ))
              failed_count += 1

      return BatchFromRecordingsResponse(
          total=len(body.recording_ids),
          created=created_count,
          failed=failed_count,
          results=results,
      )
  ```

- [ ] **Step 4：运行测试，确认 PASS**

  ```bash
  cd /home/test/arex-recorder/backend
  python3 -m pytest tests/test_test_cases.py::test_batch_from_recordings_creates_cases tests/test_test_cases.py::test_batch_from_recordings_fallback_name_when_no_transaction_code tests/test_test_cases.py::test_batch_from_recordings_handles_missing_recording -v 2>&1 | tail -10
  ```

  期望：`3 passed`

- [ ] **Step 5：运行全量测试，确认无回归**

  ```bash
  python3 -m pytest tests/test_test_cases.py -q 2>&1 | tail -5
  ```

  期望：所有测试 passed

- [ ] **Step 6：Commit**

  ```bash
  git add backend/api/v1/test_cases.py backend/tests/test_test_cases.py
  git commit -m "feat: add batch-from-recordings endpoint to create test cases in bulk"
  ```

---

## Task 4：前端 API 方法

**Files:**
- Modify: `frontend/src/api/testcases.ts`

- [ ] **Step 1：在 `frontend/src/api/testcases.ts` 中新增两个方法**

  当前文件末尾是 `addToSuite`，在 `}` 闭合前追加：

  ```typescript
  import api from './index'

  export const testCaseApi = {
    list: (params?: any) => api.get('/test-cases', { params }),
    create: (data: any) => api.post('/test-cases', data),
    get: (id: number) => api.get(`/test-cases/${id}`),
    update: (id: number, data: any) => api.put(`/test-cases/${id}`, data),
    delete: (id: number) => api.delete(`/test-cases/${id}`),
    fromRecording: (data: any) => api.post('/test-cases/from-recording', data),
    clone: (id: number) => api.post(`/test-cases/${id}/clone`),
    exportCases: (params?: any) => api.get('/test-cases/export', { params }),
    addToSuite: (id: number, data: any) => api.post(`/test-cases/${id}/add-to-suite`, data),
    batchCheck: (data: { recording_ids: number[] }) =>
      api.post('/test-cases/batch-check', data),
    batchFromRecordings: (data: { recording_ids: number[]; prefix: string }) =>
      api.post('/test-cases/batch-from-recordings', data),
  }
  ```

  注意：这是整个文件的完整内容，直接覆盖即可。

- [ ] **Step 2：Commit**

  ```bash
  git add frontend/src/api/testcases.ts
  git commit -m "feat: add batchCheck and batchFromRecordings API methods"
  ```

---

## Task 5：前端视图改造

**Files:**
- Modify: `frontend/src/views/recording/index.vue`

### Step 1：新增响应式状态变量

- [ ] 在 `<script setup>` 区域找到 `const showConvertModal = ref(false)` 这行，在其之后插入以下新变量：

  ```typescript
  // 批量生成用例
  const selectedRecordingIds = ref<(string | number)[]>([])
  const showBatchModal = ref(false)
  const batchStep = ref<'prefix' | 'check'>('prefix')
  const batchPrefix = ref('')
  const batchChecking = ref(false)
  const batchCheckItems = ref<Array<{
    recording_id: number
    transaction_code: string | null
    has_existing: boolean
    existing_case_id: number | null
    existing_case_name: string | null
  }>>([])
  const batchGenerating = ref(false)
  const showBatchResultModal = ref(false)
  const batchResult = ref<{
    total: number
    created: number
    failed: number
    skipped: number
    results: Array<{ recording_id: number; status: string; name?: string; error?: string }>
  } | null>(null)
  ```

### Step 2：修改治理视图表格配置

- [ ] 找到 `const groupColumns: DataTableColumns<RecordingGroupRow> = [` 这行，在数组最前面插入 selection 列：

  ```typescript
  const groupColumns: DataTableColumns<RecordingGroupRow> = [
    { type: 'selection' },
    // ... 其余列保持不变
  ```

- [ ] 找到 `<n-data-table` 中渲染治理分组表格的标签（带 `:columns="groupColumns"` 的那个），添加 `row-key` 和 `v-model:checked-row-keys`：

  ```vue
  <n-data-table
    :columns="groupColumns"
    :data="recordingGroups"
    :loading="groupsLoading"
    :pagination="{ pageSize: 8 }"
    :row-key="(row: RecordingGroupRow) => row.representative_recording_id"
    v-model:checked-row-keys="selectedRecordingIds"
  />
  ```

### Step 3：在治理视图卡片 header 增加批量按钮

- [ ] 找到 `<template #header-extra>` 内的 `<n-space>` 块（治理视图卡片的右上角操作区），在 `</n-space>` 关闭前追加批量按钮：

  ```vue
  <template #header-extra>
    <n-space>
      <n-select ... />
      <n-input ... />
      <n-button @click="loadRecordingGroups">查询</n-button>
      <n-button
        v-if="canEdit"
        type="primary"
        :disabled="selectedRecordingIds.length === 0"
        @click="openBatchModal"
      >
        批量生成用例 {{ selectedRecordingIds.length > 0 ? `(${selectedRecordingIds.length})` : '' }}
      </n-button>
    </n-space>
  </template>
  ```

### Step 4：在 `<template>` 末尾插入批量 Modal

- [ ] 在 `</template>` 闭合标签前，紧接 `showConvertModal` 的 `</n-modal>` 之后，插入以下两个 Modal：

  ```vue
  <!-- 批量生成用例 Modal（两步：前缀输入 → 冲突检测结果） -->
  <n-modal
    v-model:show="showBatchModal"
    :title="batchStep === 'prefix' ? '批量生成测试用例' : '冲突检测结果'"
    preset="card"
    style="width: 480px"
    :closable="!batchGenerating"
    :mask-closable="!batchGenerating"
  >
    <!-- Step 1: 前缀输入 -->
    <template v-if="batchStep === 'prefix'">
      <n-space vertical>
        <span>已选 {{ selectedRecordingIds.length }} 个分组</span>
        <n-form label-placement="left" label-width="100px">
          <n-form-item label="用例名称前缀">
            <n-input
              v-model:value="batchPrefix"
              placeholder="如：银行服务"
              @keyup.enter="doBatchCheck"
            />
          </n-form-item>
        </n-form>
      </n-space>
    </template>

    <!-- Step 2: 冲突检测结果 -->
    <template v-else>
      <n-space vertical>
        <n-alert
          v-if="batchCheckItems.filter(i => !i.has_existing).length > 0"
          type="success"
          :show-icon="true"
        >
          {{ batchCheckItems.filter(i => !i.has_existing).length }} 条可生成
        </n-alert>
        <n-alert
          v-if="batchCheckItems.filter(i => i.has_existing).length > 0"
          type="warning"
          :show-icon="true"
        >
          {{ batchCheckItems.filter(i => i.has_existing).length }} 条已有用例（{{
            batchCheckItems.filter(i => i.has_existing).map(i => i.transaction_code || `#${i.recording_id}`).join('、')
          }}），将自动跳过
        </n-alert>
        <n-alert
          v-if="batchCheckItems.filter(i => !i.has_existing).length === 0"
          type="info"
        >
          所有选中分组均已有对应用例，无需重复生成
        </n-alert>
      </n-space>
    </template>

    <template #footer>
      <n-space justify="end">
        <template v-if="batchStep === 'prefix'">
          <n-button @click="showBatchModal = false">取消</n-button>
          <n-button type="primary" :loading="batchChecking" @click="doBatchCheck">
            检测冲突 →
          </n-button>
        </template>
        <template v-else>
          <n-button @click="batchStep = 'prefix'">返回</n-button>
          <n-button
            v-if="batchCheckItems.filter(i => !i.has_existing).length > 0"
            type="primary"
            :loading="batchGenerating"
            @click="doBatchGenerate"
          >
            确认生成 →
          </n-button>
        </template>
      </n-space>
    </template>
  </n-modal>

  <!-- 批量生成结果 Modal -->
  <n-modal
    v-model:show="showBatchResultModal"
    title="生成完成"
    preset="card"
    style="width: 420px"
  >
    <n-space vertical v-if="batchResult">
      <n-alert type="success" :show-icon="true">成功 {{ batchResult.created }} 条</n-alert>
      <n-alert v-if="batchResult.skipped > 0" type="warning" :show-icon="true">
        跳过 {{ batchResult.skipped }} 条（已有用例）
      </n-alert>
      <n-alert v-if="batchResult.failed > 0" type="error" :show-icon="true">
        失败 {{ batchResult.failed }} 条
        <ul style="margin: 4px 0 0; padding-left: 16px; font-size: 12px">
          <li v-for="r in batchResult.results.filter(x => x.status === 'failed')" :key="r.recording_id">
            录制 #{{ r.recording_id }}：{{ r.error }}
          </li>
        </ul>
      </n-alert>
    </n-space>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showBatchResultModal = false">关闭</n-button>
        <n-button type="primary" @click="() => { showBatchResultModal = false; router.push('/test-cases') }">
          前往测试用例库 →
        </n-button>
      </n-space>
    </template>
  </n-modal>
  ```

### Step 5：添加批量操作函数

- [ ] 在 `doConvert` 函数之后插入以下三个函数：

  ```typescript
  function openBatchModal() {
    batchPrefix.value = ''
    batchStep.value = 'prefix'
    batchCheckItems.value = []
    showBatchModal.value = true
  }

  async function doBatchCheck() {
    if (!batchPrefix.value.trim()) {
      message.warning('请填写用例名称前缀')
      return
    }
    batchChecking.value = true
    try {
      const ids = selectedRecordingIds.value.map(Number)
      const res = await testCaseApi.batchCheck({ recording_ids: ids })
      batchCheckItems.value = res.data
      batchStep.value = 'check'
    } catch (error: any) {
      message.error(error.response?.data?.detail || '冲突检测失败')
    } finally {
      batchChecking.value = false
    }
  }

  async function doBatchGenerate() {
    const toGenerate = batchCheckItems.value
      .filter(i => !i.has_existing)
      .map(i => i.recording_id)
    const skippedCount = batchCheckItems.value.filter(i => i.has_existing).length

    batchGenerating.value = true
    try {
      const res = await testCaseApi.batchFromRecordings({
        recording_ids: toGenerate,
        prefix: batchPrefix.value.trim(),
      })
      batchResult.value = {
        ...res.data,
        skipped: skippedCount,
      }
      showBatchModal.value = false
      showBatchResultModal.value = true
      selectedRecordingIds.value = []
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量生成失败')
    } finally {
      batchGenerating.value = false
    }
  }
  ```

### Step 6：导入新 Naive UI 组件

- [ ] 找到 `<script setup>` 中的 `import { ... } from 'naive-ui'` 这行，确认 `NAlert` 已包含在内，若没有则添加：

  ```typescript
  import {
    NAlert, NButton, NCard, NDataTable, NDatePicker,
    NDrawer, NDrawerContent, NH2, NForm, NFormItem,
    NInput, NModal, NPopconfirm, NSpace, NSelect, NTag,
    useMessage,
  } from 'naive-ui'
  ```

- [ ] **Step 7：Commit**

  ```bash
  git add frontend/src/views/recording/index.vue frontend/src/api/testcases.ts
  git commit -m "feat: add batch generate test cases UI to governance view"
  ```

---

## Task 6：自测验证（你完成后必须执行）

**Files:** 无新改动，仅验证

- [ ] **Step 1：运行后端全量测试**

  ```bash
  cd /home/test/arex-recorder/backend
  python3 -m pytest tests/ -q 2>&1 | tail -10
  ```

  期望：0 failed。若有失败，阅读错误信息修复后重新运行。

- [ ] **Step 2：启动前端开发服务器**

  ```bash
  cd /home/test/arex-recorder/frontend
  npm run dev &
  ```

  等待输出 `Local: http://localhost:xxxx` 后继续。

- [ ] **Step 3：验证后端接口可访问**

  ```bash
  # 需要先有 token，用 admin 登录获取
  TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -d "username=admin&password=admin123" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

  curl -s -X POST http://localhost:8000/api/v1/test-cases/batch-check \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"recording_ids": []}' | python3 -m json.tool
  ```

  期望：返回 `[]`（空列表）

- [ ] **Step 4：验证前端 UI**

  打开浏览器访问录制中心页面，检查：
  - 样本治理视图表格第一列有复选框
  - 勾选若干行后，右上角"批量生成用例"按钮变为高亮可点击（括号内显示数量）
  - 未勾选时按钮为禁用状态（灰色）
  - 点击按钮弹出 Modal，能填写前缀并点击"检测冲突"
  - 检测后展示冲突/可生成数量
  - 全部冲突时隐藏"确认生成"按钮
  - 生成后展示结果弹窗，"前往测试用例库"可跳转

- [ ] **Step 5：最终 Commit（若 Task 5 的 commit 在本次会话中未单独提交）**

  确认所有改动已 commit：

  ```bash
  git status
  git log --oneline -5
  ```
