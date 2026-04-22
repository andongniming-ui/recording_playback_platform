# 回放高级配置功能设计文档

**日期**：2026-04-11  
**状态**：已确认，待实现

---

## 背景

arex-recorder 的回放表单当前仅有基础字段（应用、用例、并发、超时），缺少 arex-platform 中已有的忽略字段、差异规则、断言规则、请求头转换等高级配置能力。后端 schema 中部分字段已存在但前端未暴露，还有少数字段后端也缺失。本次改造目标是全面对齐 arex-platform 的回放功能。

---

## 范围

### 包含

- 后端：补全 4 个缺失字段（`ignore_fields`、`delay_ms`、`repeat_count`、`header_transforms`）
- 前端：回放表单拆分为"基础配置"+"高级配置"两组，完整暴露所有后端已有及新增字段

### 不包含

- 推荐忽略字段（需后端独立分析接口，复杂度高，后续单独做）
- 加载应用默认配置（同上）
- Mock 子调用（`use_sub_invocation_mocks`）— 已在后端 schema 中但基础设施不完整，暂不暴露

---

## 后端改动

### 1. `backend/models/replay.py`

新增四列（均有默认值，向后兼容）：

| 列名 | SQLAlchemy 类型 | 默认值 | 说明 |
|------|----------------|--------|------|
| `ignore_fields` | `Text` | `NULL` | JSON 字符串，字段名列表 |
| `delay_ms` | `Integer` | `0` | 每次请求前等待毫秒数 |
| `repeat_count` | `Integer` | `1` | 每条录制重复回放次数 |
| `header_transforms` | `Text` | `NULL` | JSON 字符串，转换规则列表 |

### 2. `backend/schemas/replay.py`

`ReplayJobCreate` 新增字段：

```python
ignore_fields: Optional[List[str]] = None
delay_ms: int = 0
repeat_count: int = 1
header_transforms: Optional[str] = None  # JSON
```

`ReplayJobOut` 新增相同字段用于回显。

### 3. `backend/main.py` — `_migrate_db()`

追加四条 ALTER TABLE 语句：

```sql
ALTER TABLE replay_job ADD COLUMN ignore_fields TEXT;
ALTER TABLE replay_job ADD COLUMN delay_ms INTEGER DEFAULT 0;
ALTER TABLE replay_job ADD COLUMN repeat_count INTEGER DEFAULT 1;
ALTER TABLE replay_job ADD COLUMN header_transforms TEXT;
```

### 4. `backend/api/v1/replays.py`

创建 job 时将新字段写入 model（`ignore_fields` 序列化为 JSON）。

### 5. `backend/core/replay_executor.py`

- **`ignore_fields`**：从 job 读取后解析 JSON，传给 `compute_diff(ignore_fields=...)` — `diff.py` 已支持此参数。
- **`delay_ms`**：在 `_run_one` 里发请求前 `await asyncio.sleep(job.delay_ms / 1000)`。
- **`repeat_count`**：构建回放任务列表时，将每条录制复制 `repeat_count` 次。
- **`header_transforms`**：解析 JSON，在 `_execute_single` 里构建 httpx 请求 headers 之后，按 type（replace/add/remove）逐条处理。

---

## 前端改动

### `frontend/src/views/replay/index.vue`

表单结构改为两段，用 `n-collapse` 分组：

#### 基础配置（默认展开）

| 控件 | 字段 | 说明 |
|------|------|------|
| `n-select`（多选） | `case_ids` | 测试用例，不变 |
| `n-select` | `application_id` | 所属应用，不变 |
| `n-input-number` | `concurrency` | 并发数，不变 |
| `n-input-number` | `timeout_ms` | 超时时间，不变 |
| `n-input` | `name` | 任务名称，不变 |

#### 高级配置（默认收起）

| 控件 | 字段 | 说明 |
|------|------|------|
| `n-dynamic-tags` | `ignore_fields` | 忽略字段，手动输入字段名 |
| `n-switch` | `smart_noise_reduction` | 智能降噪（现有，移入此组） |
| 动态列表 | `diff_rules` | 差异规则：ignore / numeric_tolerance / regex_match / type_only |
| 动态列表 | `assertions` | 断言规则：7 种类型 |
| 动态列表+预设 | `header_transforms` | 请求头转换，带常用预设标签 |
| `n-input-number` | `perf_threshold_ms` | 性能阈值（ms） |
| `n-input-number` | `delay_ms` | 请求间隔（ms） |
| `n-input-number` | `repeat_count` | 流量放大（每条重复 N 次） |
| `n-input-number` | `retry_count` | 失败重试（现有，移入此组） |
| `n-input` | `target_host` | Host 覆盖 |
| `n-input` + `n-select` | `webhook_url` + `notify_type` | Webhook 通知 |

### 提交逻辑

- `ignore_fields` 作为 `List<string>` 直接提交（后端接受 JSON 列表）
- `diff_rules` / `assertions` 序列化为 JSON 字符串提交（与现有逻辑一致）
- `header_transforms` 序列化为 JSON 字符串提交
- 空值字段（空列表、0、null）在提交前清除，避免干扰

---

## 数据流

```
用户填写表单
  → POST /api/v1/replays（ReplayJobCreate）
  → replay_executor.run_job(job)
      → 构建录制列表（×repeat_count）
      → 信号量控制并发
          → delay_ms 等待
          → 应用 header_transforms
          → 发 HTTP 请求
          → compute_diff(ignore_fields, diff_rules, smart_noise_reduction)
          → evaluate_assertions
          → retry_count 重试
      → 保存 ReplayResult
  → WebSocket 推送进度
```

---

## 兼容性

- 所有新字段均有默认值（None / 0 / 1 / False），不影响现有回放任务的展示和执行
- 数据库通过 `_migrate_db()` 的 try/except 机制安全追加列，服务启动时自动执行
