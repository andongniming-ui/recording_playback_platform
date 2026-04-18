# Sub-Call Diff View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在回放结果弹窗中增加「子调用对比」Tab，展示 System A 录制时的子调用 vs System B 回放时实际产生的子调用。

**Architecture:** 回放执行器从 HTTP 响应头提取 `arex-record-id`，等待 300ms 后查询 `ArexMocker` 表获取回放侧子调用，序列化存入 `ReplayResult.actual_sub_calls`。前端新增 `SubCallDiffPanel.vue` 组件，在弹窗 Tabs 里按 index 配对展示两侧子调用差异。

**Tech Stack:** Python/FastAPI (SQLAlchemy async)，Vue3/Naive UI，TypeScript

---

## 文件清单

| 文件 | 操作 |
|------|------|
| `backend/models/replay.py` | 新增 `actual_sub_calls` 字段 |
| `backend/main.py` | migration 追加 ALTER TABLE |
| `backend/core/replay_executor.py` | 捕获响应头、查 ArexMocker、传入 _save_result |
| `backend/api/v1/replays.py` | 新增 GET `/results/{result_id}/sub-call-diff` 接口 |
| `backend/tests/test_replay.py` | 新增相关测试 |
| `frontend/src/api/replays.ts` | 新增 `getSubCallDiff` 方法和类型 |
| `frontend/src/components/recording/SubCallDiffPanel.vue` | 新建组件 |
| `frontend/src/views/results/job-detail.vue` | 弹窗加 Tabs，调用新接口 |

---

## Task 1: 数据库字段 + Migration

**Files:**
- Modify: `backend/models/replay.py`
- Modify: `backend/main.py`

- [ ] **Step 1: 在 ReplayResult 模型中新增字段**

打开 `backend/models/replay.py`，在 `failure_reason` 字段后追加：

```python
    actual_sub_calls: Mapped[str | None] = mapped_column(Text)
```

完整字段上下文（`failure_reason` 下方）：
```python
    failure_category: Mapped[str | None] = mapped_column(String(64))
    failure_reason: Mapped[str | None] = mapped_column(Text)
    actual_sub_calls: Mapped[str | None] = mapped_column(Text)   # JSON list of sub-calls from replay

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

- [ ] **Step 2: 在 main.py 的 migrations 列表末尾追加 ALTER TABLE**

打开 `backend/main.py`，找到 `migrations = [...]` 列表，在最后一条 SQL 后追加：

```python
        "ALTER TABLE replay_result ADD COLUMN actual_sub_calls TEXT",
```

- [ ] **Step 3: 启动后端验证 migration 执行**

```bash
cd /home/test/arex-recorder/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
sleep 3
python3 -c "
import sqlite3
conn = sqlite3.connect('../data/arex_recorder.db')
cols = [row[1] for row in conn.execute('PRAGMA table_info(replay_result)')]
print('actual_sub_calls' in cols)
conn.close()
"
```

预期输出：`True`

- [ ] **Step 4: 停止后端，提交**

```bash
pkill -f "uvicorn main:app" 2>/dev/null || true
cd /home/test/arex-recorder
git add backend/models/replay.py backend/main.py
git commit -m "feat(sub-call-diff): add actual_sub_calls field to ReplayResult"
```

---

## Task 2: 回放执行器采集回放侧子调用

**Files:**
- Modify: `backend/core/replay_executor.py`

- [ ] **Step 1: 在文件顶部的 import 区添加 ArexMocker 导入**

找到 `from models.replay import ReplayJob, ReplayResult` 这行，在下方追加：

```python
from models.arex_mocker import ArexMocker
```

- [ ] **Step 2: 在 `_save_result` 函数签名中新增参数**

找到 `_save_result` 函数定义（约第 630 行），在 `failure_reason` 参数后追加 `actual_sub_calls`：

```python
async def _save_result(
    job_id: int,
    case_id: int,
    *,
    case: Optional[TestCase] = None,
    status: str,
    is_pass: bool,
    actual_status_code: Optional[int] = None,
    actual_response: Optional[str] = None,
    expected_response: Optional[str] = None,
    diff_result: Optional[str] = None,
    diff_score: Optional[float] = None,
    assertion_results: Optional[str] = None,
    latency_ms: Optional[int] = None,
    failure_category: Optional[str] = None,
    failure_reason: Optional[str] = None,
    actual_sub_calls: Optional[str] = None,
) -> ReplayResult:
```

- [ ] **Step 3: 在 `_save_result` 函数体中保存新字段**

找到 `replay_result.failure_reason = failure_reason` 这行，在其下方追加：

```python
        replay_result.actual_sub_calls = actual_sub_calls
```

- [ ] **Step 4: 新增辅助函数 `_fetch_replay_sub_calls`**

在 `_save_result` 函数定义的上方（约第 629 行）插入：

```python
async def _fetch_replay_sub_calls(record_id: str) -> Optional[str]:
    """Wait for AREX agent to finish reporting, then fetch sub-calls by record_id."""
    await asyncio.sleep(0.3)
    async with database.async_session_factory() as db:
        result = await db.execute(
            select(ArexMocker)
            .where(
                ArexMocker.record_id == record_id,
                ArexMocker.is_entry_point == False,  # noqa: E712
            )
            .order_by(ArexMocker.id)
        )
        mockers = result.scalars().all()
    if not mockers:
        return None
    sub_calls = []
    for m in mockers:
        try:
            mocker = json.loads(m.mocker_data)
            category = mocker.get("categoryType") or {}
            cat_name = category.get("name") if isinstance(category, dict) else str(category)
            target_req = mocker.get("targetRequest") or {}
            target_resp = mocker.get("targetResponse") or {}
            sub_calls.append({
                "type": cat_name or m.category_name,
                "operation": mocker.get("operationName") or "",
                "request": target_req.get("body") if isinstance(target_req, dict) else None,
                "response": target_resp.get("body") if isinstance(target_resp, dict) else None,
            })
        except Exception:
            pass
    return json.dumps(sub_calls, ensure_ascii=False) if sub_calls else None
```

- [ ] **Step 5: 在 `_execute_single` 中捕获响应头并调用辅助函数**

找到 `_execute_single` 内的以下代码块（约第 504–513 行）：

```python
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.request(
                method=case.request_method or "GET",
                url=url,
                content=mapped_request_body.encode() if mapped_request_body else None,
                headers=headers,
            )
        actual_status = resp.status_code
        actual_body = resp.text
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "OK_GOT_RESPONSE"
```

替换为：

```python
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.request(
                method=case.request_method or "GET",
                url=url,
                content=mapped_request_body.encode() if mapped_request_body else None,
                headers=headers,
            )
        actual_status = resp.status_code
        actual_body = resp.text
        replay_arex_record_id = resp.headers.get("arex-record-id")
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "OK_GOT_RESPONSE"
```

还需在 try 块开始前（`mock_record_id = None` 附近）声明变量：

```python
    mock_record_id = None
    replay_arex_record_id = None   # add this line
```

- [ ] **Step 6: 在 `_execute_single` 末尾调用 `_fetch_replay_sub_calls` 并传入 `_save_result`**

找到函数末尾的 `return await _save_result(...)` 调用（约第 612 行），在其之前插入：

```python
    actual_sub_calls_json = None
    if replay_arex_record_id and status not in ("TIMEOUT", "ERROR"):
        actual_sub_calls_json = await _fetch_replay_sub_calls(replay_arex_record_id)
```

然后在 `_save_result` 调用中追加参数：

```python
    return await _save_result(
        job_id=job_id,
        case_id=case_id,
        case=case,
        status=status,
        actual_status_code=actual_status,
        actual_response=mapped_actual_body if status == "OK_GOT_RESPONSE" else actual_body,
        expected_response=case.expected_response,
        diff_result=diff_json,
        diff_score=diff_score,
        assertion_results=assertion_results_json,
        is_pass=is_pass,
        latency_ms=latency_ms,
        failure_category=failure_category,
        failure_reason=failure_reason,
        actual_sub_calls=actual_sub_calls_json,
    )
```

- [ ] **Step 7: 写测试**

在 `backend/tests/test_replay.py` 末尾追加：

```python
@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_empty(tmp_path):
    """When no ArexMocker rows exist for record_id, returns None."""
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await _fetch_replay_sub_calls("nonexistent-id")
        assert result is None
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_returns_json(tmp_path):
    """When ArexMocker rows exist, returns JSON string of sub-calls."""
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.arex_mocker import ArexMocker as MockerModel

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t2.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    mocker_data = json.dumps({
        "categoryType": {"name": "MySQL", "entryPoint": False},
        "operationName": "SELECT * FROM car_policy",
        "targetRequest": {"body": {"sql": "SELECT * FROM car_policy"}},
        "targetResponse": {"body": {"rows": [{"id": 1}]}},
    })
    async with factory() as session:
        session.add(MockerModel(
            record_id="replay-001",
            app_id="didi-car-uat",
            category_name="MySQL",
            is_entry_point=False,
            mocker_data=mocker_data,
        ))
        await session.commit()

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await _fetch_replay_sub_calls("replay-001")
        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["type"] == "MySQL"
        assert parsed[0]["operation"] == "SELECT * FROM car_policy"
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()
```

- [ ] **Step 8: 运行测试验证**

```bash
cd /home/test/arex-recorder
pytest backend/tests/test_replay.py::test_fetch_replay_sub_calls_empty backend/tests/test_replay.py::test_fetch_replay_sub_calls_returns_json -v
```

预期：2 tests PASSED

- [ ] **Step 9: 运行全量测试确保无回归**

```bash
cd /home/test/arex-recorder
pytest backend/tests/ -v --tb=short -q
```

预期：全部 PASSED（或与改动前相同数量的 pass）

- [ ] **Step 10: 提交**

```bash
cd /home/test/arex-recorder
git add backend/core/replay_executor.py backend/tests/test_replay.py
git commit -m "feat(sub-call-diff): capture replay sub-calls from arex-record-id header"
```

---

## Task 3: 后端新增 sub-call-diff API 接口

**Files:**
- Modify: `backend/api/v1/replays.py`
- Modify: `backend/tests/test_replay.py`

- [ ] **Step 1: 在 `replays.py` 末尾新增辅助函数和接口**

打开 `backend/api/v1/replays.py`，在文件末尾追加：

```python
def _pair_sub_calls(recorded: list, replayed: list) -> list:
    """Pair recorded and replayed sub-calls by sequential index."""
    max_len = max(len(recorded), len(replayed)) if (recorded or replayed) else 0
    pairs = []
    for i in range(max_len):
        rec = recorded[i] if i < len(recorded) else None
        rep = replayed[i] if i < len(replayed) else None
        if rec and rep:
            side = "both"
            try:
                response_matched = (
                    json.dumps(rec.get("response"), sort_keys=True)
                    == json.dumps(rep.get("response"), sort_keys=True)
                )
            except Exception:
                response_matched = False
        elif rec:
            side = "recorded_only"
            response_matched = None
        else:
            side = "replayed_only"
            response_matched = None
        pairs.append({
            "index": i + 1,
            "type": (rec or rep or {}).get("type") or "",
            "recorded": rec,
            "replayed": rep,
            "side": side,
            "response_matched": response_matched,
        })
    return pairs


@router.get("/results/{result_id}/sub-call-diff")
async def get_sub_call_diff(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Return paired sub-calls for a replay result: recorded vs replayed."""
    result_row = await db.execute(select(ReplayResult).where(ReplayResult.id == result_id))
    result = result_row.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Replay result not found")

    # Load recorded sub-calls from source recording
    recorded_raw = []
    if result.test_case_id:
        case_row = await db.execute(select(TestCase).where(TestCase.id == result.test_case_id))
        test_case = case_row.scalar_one_or_none()
        if test_case and test_case.source_recording_id:
            rec_row = await db.execute(
                select(Recording).where(Recording.id == test_case.source_recording_id)
            )
            recording = rec_row.scalar_one_or_none()
            if recording and recording.sub_calls:
                try:
                    recorded_raw = json.loads(recording.sub_calls)
                    if not isinstance(recorded_raw, list):
                        recorded_raw = []
                except Exception:
                    recorded_raw = []

    # Load replayed sub-calls stored during replay execution
    replayed_raw = []
    if result.actual_sub_calls:
        try:
            replayed_raw = json.loads(result.actual_sub_calls)
            if not isinstance(replayed_raw, list):
                replayed_raw = []
        except Exception:
            replayed_raw = []

    pairs = _pair_sub_calls(recorded_raw, replayed_raw)
    return {
        "recorded": recorded_raw,
        "replayed": replayed_raw,
        "pairs": pairs,
    }
```

- [ ] **Step 2: 写测试**

在 `backend/tests/test_replay.py` 末尾追加：

```python
def test_sub_call_diff_not_found(client, admin_headers):
    resp = client.get("/api/v1/replays/results/99999/sub-call-diff", headers=admin_headers)
    assert resp.status_code == 404


def test_sub_call_diff_no_sub_calls(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job_resp = _create_replay_job(client, admin_headers, [tc["id"]])
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    results_resp = client.get(f"/api/v1/replays/{job_id}/results", headers=admin_headers)
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert len(results) >= 1
    result_id = results[0]["id"]

    resp = client.get(f"/api/v1/replays/results/{result_id}/sub-call-diff", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "recorded" in data
    assert "replayed" in data
    assert "pairs" in data
    assert data["replayed"] == []


def test_pair_sub_calls_both_sides():
    from api.v1.replays import _pair_sub_calls
    recorded = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    replayed = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 2}}]
    pairs = _pair_sub_calls(recorded, replayed)
    assert len(pairs) == 1
    assert pairs[0]["side"] == "both"
    assert pairs[0]["response_matched"] is False


def test_pair_sub_calls_recorded_only():
    from api.v1.replays import _pair_sub_calls
    recorded = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    pairs = _pair_sub_calls(recorded, [])
    assert len(pairs) == 1
    assert pairs[0]["side"] == "recorded_only"
    assert pairs[0]["response_matched"] is None
```

- [ ] **Step 3: 运行测试**

```bash
cd /home/test/arex-recorder
pytest backend/tests/test_replay.py::test_sub_call_diff_not_found \
       backend/tests/test_replay.py::test_sub_call_diff_no_sub_calls \
       backend/tests/test_replay.py::test_pair_sub_calls_both_sides \
       backend/tests/test_replay.py::test_pair_sub_calls_recorded_only -v
```

预期：4 tests PASSED

- [ ] **Step 4: 运行全量测试**

```bash
cd /home/test/arex-recorder
pytest backend/tests/ -q
```

- [ ] **Step 5: 提交**

```bash
cd /home/test/arex-recorder
git add backend/api/v1/replays.py backend/tests/test_replay.py
git commit -m "feat(sub-call-diff): add GET /replays/results/{id}/sub-call-diff endpoint"
```

---

## Task 4: 前端 API 封装 + SubCallDiffPanel 组件

**Files:**
- Modify: `frontend/src/api/replays.ts`
- Create: `frontend/src/components/recording/SubCallDiffPanel.vue`

- [ ] **Step 1: 在 `replays.ts` 中新增类型和方法**

打开 `frontend/src/api/replays.ts`，在文件末尾追加类型定义，并在 `replayApi` 对象中新增方法：

```typescript
export interface SubCallDiffItem {
  type?: string | null
  operation?: string | null
  request?: unknown
  response?: unknown
}

export interface SubCallDiffPair {
  index: number
  type: string
  recorded: SubCallDiffItem | null
  replayed: SubCallDiffItem | null
  side: 'both' | 'recorded_only' | 'replayed_only'
  response_matched: boolean | null
}

export interface SubCallDiffResult {
  recorded: SubCallDiffItem[]
  replayed: SubCallDiffItem[]
  pairs: SubCallDiffPair[]
}
```

在 `replayApi` 对象的 `getAnalysis` 行后追加：

```typescript
  getSubCallDiff: (resultId: number) => api.get<SubCallDiffResult>(`/replays/results/${resultId}/sub-call-diff`),
```

- [ ] **Step 2: 新建 SubCallDiffPanel.vue 组件**

创建文件 `frontend/src/components/recording/SubCallDiffPanel.vue`，内容如下：

```vue
<template>
  <div>
    <n-alert v-if="!pairs.length" type="default" :show-icon="false" style="color:#999">
      {{ replayed.length === 0
          ? 'Agent 未上报子调用（回放时 AREX Agent 可能未启动或未配置录制模式）'
          : '暂无子调用数据' }}
    </n-alert>

    <n-space v-else vertical :size="12">
      <n-card
        v-for="pair in pairs"
        :key="pair.index"
        size="small"
        :style="{ borderLeft: `3px solid ${pairColor(pair)}` }"
      >
        <template #header>
          <n-space align="center" :size="8">
            <span style="font-weight:600">#{{ pair.index }}</span>
            <n-tag size="small" :type="typeTagType(pair.type)">{{ pair.type || '未知' }}</n-tag>
            <span style="color:#666;font-size:13px">{{ pairOperation(pair) }}</span>
          </n-space>
        </template>
        <template #header-extra>
          <n-tag :type="pairTagType(pair)" size="small">{{ pairLabel(pair) }}</n-tag>
        </template>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <div class="col-title">录制（System A）</div>
            <template v-if="pair.recorded">
              <div v-if="pair.recorded.operation" class="field-label">操作</div>
              <pre v-if="pair.recorded.operation" class="code-block compact">{{ pair.recorded.operation }}</pre>
              <div class="field-label">响应</div>
              <pre class="code-block" :class="{ diff: pair.side === 'both' && pair.response_matched === false }">{{ formatValue(pair.recorded.response) }}</pre>
            </template>
            <div v-else class="empty-side">— 仅回放侧有此调用 —</div>
          </n-grid-item>
          <n-grid-item>
            <div class="col-title">回放（System B）</div>
            <template v-if="pair.replayed">
              <div v-if="pair.replayed.operation" class="field-label">操作</div>
              <pre v-if="pair.replayed.operation" class="code-block compact">{{ pair.replayed.operation }}</pre>
              <div class="field-label">响应</div>
              <pre class="code-block" :class="{ diff: pair.side === 'both' && pair.response_matched === false }">{{ formatValue(pair.replayed.response) }}</pre>
            </template>
            <div v-else class="empty-side">— 仅录制侧有此调用 —</div>
          </n-grid-item>
        </n-grid>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { NAlert, NCard, NGrid, NGridItem, NSpace, NTag } from 'naive-ui'
import type { SubCallDiffPair, SubCallDiffItem } from '@/api/replays'

const props = defineProps<{
  pairs: SubCallDiffPair[]
  replayed: SubCallDiffItem[]
}>()

function formatValue(value: unknown): string {
  if (value == null) return '-'
  if (typeof value === 'string') {
    try { return JSON.stringify(JSON.parse(value), null, 2) } catch { return value }
  }
  return JSON.stringify(value, null, 2)
}

function pairOperation(pair: SubCallDiffPair): string {
  const op = pair.recorded?.operation || pair.replayed?.operation || ''
  return op.length > 60 ? op.slice(0, 60) + '…' : op
}

function pairColor(pair: SubCallDiffPair): string {
  if (pair.side === 'recorded_only' || pair.side === 'replayed_only') return '#f0a020'
  if (pair.response_matched === false) return '#d03050'
  return '#18a058'
}

function pairTagType(pair: SubCallDiffPair): 'success' | 'error' | 'warning' | 'default' {
  if (pair.side === 'recorded_only' || pair.side === 'replayed_only') return 'warning'
  if (pair.response_matched === false) return 'error'
  return 'success'
}

function pairLabel(pair: SubCallDiffPair): string {
  if (pair.side === 'recorded_only') return '仅录制侧'
  if (pair.side === 'replayed_only') return '仅回放侧'
  if (pair.response_matched === false) return '响应差异'
  return '一致'
}

function typeTagType(type: string): 'warning' | 'info' | 'default' {
  const t = (type || '').toLowerCase()
  if (t.includes('mysql') || t.includes('jdbc')) return 'warning'
  if (t.includes('redis')) return 'info'
  return 'default'
}
</script>

<style scoped>
.col-title {
  font-size: 12px;
  font-weight: 600;
  color: #888;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.field-label {
  font-size: 12px;
  color: #aaa;
  margin: 6px 0 3px;
}
.code-block {
  margin: 0;
  padding: 8px 10px;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  border-radius: 4px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
  font-family: monospace;
  font-size: 12px;
}
.code-block.compact {
  max-height: 60px;
}
.code-block.diff {
  border-color: #ffb3b3;
  background: #fff5f5;
}
.empty-side {
  color: #ccc;
  font-size: 13px;
  padding: 20px 0;
  text-align: center;
}
</style>
```

- [ ] **Step 3: 提交**

```bash
cd /home/test/arex-recorder
git add frontend/src/api/replays.ts frontend/src/components/recording/SubCallDiffPanel.vue
git commit -m "feat(sub-call-diff): add SubCallDiffPanel component and API method"
```

---

## Task 5: job-detail.vue 弹窗加 Tabs

**Files:**
- Modify: `frontend/src/views/results/job-detail.vue`

- [ ] **Step 1: 引入新组件和 NTabs**

在 `<script setup>` 的 import 区找到 `import SubCallPanel from '@/components/recording/SubCallPanel.vue'`，在其下方追加：

```typescript
import SubCallDiffPanel from '@/components/recording/SubCallDiffPanel.vue'
import type { SubCallDiffResult } from '@/api/replays'
```

在 Naive UI 的 import 解构中追加 `NTabs, NTabPane`：

```typescript
import {
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NGrid,
  NGridItem,
  NModal,
  NProgress,
  NSpace,
  NSelect,
  NSpin,
  NStatistic,
  NTag,
  NTabs,
  NTabPane,
  useMessage,
} from 'naive-ui'
```

- [ ] **Step 2: 新增响应式变量**

在 `const sourceRecordingSubCallSummary = ref('')` 下方追加：

```typescript
const subCallDiff = ref<SubCallDiffResult | null>(null)
const subCallDiffLoading = ref(false)
```

- [ ] **Step 3: 新增加载函数**

在 `openDiff` 函数下方追加：

```typescript
async function loadSubCallDiff(resultId: number) {
  subCallDiff.value = null
  subCallDiffLoading.value = true
  try {
    const res = await replayApi.getSubCallDiff(resultId)
    subCallDiff.value = res.data
  } catch {
    subCallDiff.value = null
  } finally {
    subCallDiffLoading.value = false
  }
}
```

在 `openDiff` 函数中，`void loadSourceRecording(row)` 下方追加：

```typescript
  void loadSubCallDiff(row.id)
```

- [ ] **Step 4: 改造弹窗模板**

找到弹窗内的 `<n-card title="差异详情" size="small">` 及其上方内容，用 `<n-tabs>` 包裹。

将弹窗 `<n-space vertical :size="12">` 内的最后两块（「来源录制链路」card 和「差异详情」card）替换为：

```vue
      <n-card v-if="sourceRecording" title="来源录制链路" size="small">
        <template #header-extra>
          <n-space align="center" :size="8">
            <n-tag type="info" size="small">来源用例 #{{ sourceTestCase?.id || '-' }}</n-tag>
            <n-button v-if="sourceRecording.id" size="small" @click="router.push(`/recording/recordings/${sourceRecording.id}`)">
              打开录制详情
            </n-button>
          </n-space>
        </template>
        <n-descriptions bordered :column="2" size="small">
          <n-descriptions-item label="请求">{{ sourceRecording.request_method }} {{ sourceRecording.request_uri }}</n-descriptions-item>
          <n-descriptions-item label="交易码">{{ sourceRecording.transaction_code || '-' }}</n-descriptions-item>
          <n-descriptions-item label="治理状态">{{ sourceRecording.governance_status }}</n-descriptions-item>
          <n-descriptions-item label="子调用概览">{{ sourceRecordingSubCallSummary || '-' }}</n-descriptions-item>
        </n-descriptions>
      </n-card>

      <n-tabs type="line" animated>
        <n-tab-pane name="diff" tab="差异详情">
          <n-card size="small" :bordered="false">
            <n-space vertical>
              <div>
                <div class="section-title">Diff 结果</div>
                <pre class="code-block compact">{{ prettyText(selectedResult?.diff_result) }}</pre>
              </div>
              <div v-if="parsedAssertionResults.length > 0">
                <div class="section-title">断言结果</div>
                <n-space vertical :size="6">
                  <div v-for="(item, i) in parsedAssertionResults" :key="i">
                    <n-tag :type="item.passed ? 'success' : 'error'" size="small">{{ item.passed ? '通过' : '失败' }}</n-tag>
                    <span style="margin-left:8px;font-size:12px">{{ item.message }}</span>
                  </div>
                </n-space>
              </div>
              <div v-if="selectedResult?.failure_reason">
                <div class="section-title">失败原因</div>
                <template v-if="failureReasonFields(selectedResult.failure_reason)">
                  <div style="font-size:13px;color:#555;margin-bottom:8px">
                    {{ failureReasonPrefix(selectedResult.failure_reason) }}
                  </div>
                  <n-space vertical :size="4">
                    <div
                      v-for="field in failureReasonFields(selectedResult.failure_reason)"
                      :key="field"
                      style="display:flex;align-items:center;gap:8px"
                    >
                      <n-tag type="error" size="small" style="font-family:monospace">{{ field }}</n-tag>
                    </div>
                  </n-space>
                </template>
                <pre v-else class="code-block compact">{{ selectedResult.failure_reason }}</pre>
              </div>
            </n-space>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="subcall" tab="子调用对比">
          <n-spin :show="subCallDiffLoading">
            <SubCallDiffPanel
              :pairs="subCallDiff?.pairs ?? []"
              :replayed="subCallDiff?.replayed ?? []"
            />
          </n-spin>
        </n-tab-pane>
      </n-tabs>
```

- [ ] **Step 5: 启动前端验证编译**

```bash
cd /home/test/arex-recorder/frontend
npm run build 2>&1 | tail -20
```

预期：无 TypeScript 错误，build 成功（或只有无关的 warn）

- [ ] **Step 6: 提交**

```bash
cd /home/test/arex-recorder
git add frontend/src/views/results/job-detail.vue
git commit -m "feat(sub-call-diff): add sub-call comparison tab to replay result modal"
```

---

## Task 6: 集成自测

- [ ] **Step 1: 启动全部服务**

```bash
cd /home/test/arex-recorder
./start-all.sh
```

等待输出「启动完成！」

- [ ] **Step 2: 打流量录制**

```bash
cd /home/test/arex-recorder/didi
./send_samples.sh http://127.0.0.1:18081
```

- [ ] **Step 3: 在平台完成录制 → 转用例 → 创建回放任务**

1. 打开 http://localhost:3000，登录（admin/admin123）
2. 进入「录制中心」，找到 didi-system-a 的会话，停止录制并同步
3. 选取若干录制（包含 car000003/car000006/car000011），批量转为测试用例
4. 创建回放任务：目标 `http://127.0.0.1:18082`，**不勾选「子调用 Mock」**
5. 等待回放完成

- [ ] **Step 4: 验证子调用对比 Tab**

1. 进入回放任务详情，点击任意一条结果的「对比」按钮
2. 弹窗出现后，点击「子调用对比」Tab
3. 验证：
   - 录制侧和回放侧子调用列表均不为空
   - 已知差异交易码（car000003/006/011/018/024/029）显示「响应差异」红色标签
   - 非差异交易码显示「一致」绿色标签

- [ ] **Step 5: 验证降级提示**

停止 didi-system-b，再次创建回放任务并查看子调用对比 Tab，应显示「Agent 未上报子调用」提示。
