# 子调用对比视图设计文档

**日期**: 2026-04-18
**状态**: 已批准，待实现

---

## 背景

当前回放任务的「对比详情」弹窗只展示主响应报文的 diff，缺少子调用（HTTP 外呼、数据库调用）的对比视图。用户需要直接看到 System A 录制时的子调用 vs System B 回放时实际发出的子调用，以便判断差异来源。

---

## 目标

在回放结果弹窗中新增「子调用对比」Tab，展示：
- 左侧：源录制（System A）的子调用列表
- 右侧：回放时（System B）实际产生的子调用列表
- 按 type + 顺序 index 配对，标记一致 / 差异 / 仅一侧有

---

## 方案选择

采用**方案 A：响应头关联 + 延迟查询**。

回放请求发出后从响应头取 `arex-record-id`，等待 300ms 让 agent 完成异步上报，查询 `ArexMocker` 表获取回放侧子调用，存入 `ReplayResult.actual_sub_calls`。

---

## 后端设计

### 数据库变更

`ReplayResult` 表追加字段：

```sql
ALTER TABLE replay_result ADD COLUMN actual_sub_calls TEXT;
```

通过 `main.py` 的幂等 migration 列表追加，不影响旧数据（旧行该字段为 NULL）。

### 回放执行器改动（`backend/core/replay_executor.py`）

在 `_execute_single` 里，HTTP 请求响应后：

1. 从 `resp.headers` 提取 `arex-record-id`（大小写不敏感）
2. 若存在，等待 300ms
3. 查询 `ArexMocker`：`record_id = <响应头值> AND is_entry_point = False`
4. 将查到的 `mocker_data` 列表序列化为 JSON 存入 `result.actual_sub_calls`
5. 若响应头不存在或查询结果为空，`actual_sub_calls = null`，静默跳过，不影响 diff 计算

> 300ms 等待在并发回放时每条请求独立，不阻塞其他请求（asyncio.sleep 是协程安全的）。

### 新增 API 接口

```
GET /api/v1/replays/results/{result_id}/sub-call-diff
```

响应结构：

```json
{
  "recorded": [...],
  "replayed": [...],
  "pairs": [
    {
      "index": 1,
      "type": "MySQL",
      "recorded": { ...sub_call对象... },
      "replayed": { ...sub_call对象... },
      "side": "both",
      "response_matched": true
    }
  ]
}
```

`side` 取值：`"both"` / `"recorded_only"` / `"replayed_only"`

配对逻辑：先按 type 分组，组内按顺序 index 配对；多出来的标记 `recorded_only` / `replayed_only`。

接口实现位置：`backend/api/v1/replays.py`，需加载 `ReplayResult` 和对应 `TestCase → Recording` 的 `sub_calls`。

---

## 前端设计

### 弹窗改造（`frontend/src/views/results/job-detail.vue`）

将现有弹窗内容区包裹进 `n-tabs`，新增「子调用对比」Tab：

```
[差异详情] [子调用对比]
```

打开弹窗时异步调用 `/replays/results/{result_id}/sub-call-diff`，独立 loading 状态，不阻塞弹窗渲染。

### 新增组件（`frontend/src/components/recording/SubCallDiffPanel.vue`）

接收 `pairs: SubCallDiffPair[]`，对每个 pair 渲染：

- 标题行：`#index  <类型标签>  ·  <操作/目标>`，右侧显示 ✅一致 / 🔴差异 / ⚪仅录制侧 / ⚪仅回放侧
- 内容：两列 grid，左「录制（System A）」右「回放（System B）」，展示 SQL/请求/响应
- 响应差异高亮：对比 `recorded.response` vs `replayed.response`，不同时右侧响应框加红色边框

若 `pairs` 为空且 `replayed` 为空：显示灰色提示「Agent 未上报子调用（可能未启动或未配置录制模式）」。

### API 封装（`frontend/src/api/replays.ts`）

新增方法：

```typescript
getSubCallDiff(resultId: number): Promise<AxiosResponse<SubCallDiffResult>>
```

---

## 边界处理

| 场景 | 处理方式 |
|------|----------|
| 响应头无 `arex-record-id` | `actual_sub_calls = null`，前端显示提示 |
| ArexMocker 查到 0 条 | 同上 |
| 录制侧无子调用但回放侧有 | 正常展示，录制侧列为空 |
| 回放开启 Mock 模式 | agent 可能不上报，降级为提示 |
| 并发回放 | 响应头 record_id 精确关联，不受并发干扰 |

---

## 自测方案

1. 启动 `./start-all.sh`，确保 didi-system-a（18081）和 didi-system-b（18082）都运行且 AREX agent 已注入
2. 在平台对 didi-system-a 录制一批流量（`./send_samples.sh http://127.0.0.1:18081`），转为测试用例
3. 创建回放任务，目标 `http://127.0.0.1:18082`，**不开启子调用 Mock**
4. 回放完成后打开任意一条结果的「对比」弹窗，切到「子调用对比」Tab
5. 验证：
   - 录制侧子调用列表正常显示
   - 回放侧子调用列表正常显示（非空）
   - 已知差异交易码（`car000003/006/011/018/024/029`）的响应差异标红
   - 非差异交易码子调用显示 ✅一致
6. 验证降级：停止 didi-system-b 的 agent 后再回放，弹窗显示「Agent 未上报子调用」提示

---

## 涉及文件

| 文件 | 变更类型 |
|------|----------|
| `backend/main.py` | 追加 migration SQL |
| `backend/models/replay.py` | 新增 `actual_sub_calls` 字段 |
| `backend/core/replay_executor.py` | 捕获响应头，查询 ArexMocker，存 actual_sub_calls |
| `backend/api/v1/replays.py` | 新增 `sub-call-diff` 接口 |
| `frontend/src/api/replays.ts` | 新增 `getSubCallDiff` 方法 |
| `frontend/src/components/recording/SubCallDiffPanel.vue` | 新增组件 |
| `frontend/src/views/results/job-detail.vue` | 弹窗加 Tabs，调用新接口 |
