# 测试用例详情页编辑能力 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在测试用例详情页加入"编辑"按钮（完整字段抽屉）和治理状态快捷切换下拉，让用户无需回列表页即可修改用例。

**Architecture:** 所有改动集中在单一 Vue 文件 `detail.vue`，复用已有的 `testCaseApi.update()` 接口。新增编辑抽屉（NDrawer）和治理状态下拉（NDropdown），共享同一个 `loadPage()` 刷新逻辑。

**Tech Stack:** Vue 3 Composition API, Naive UI (NDrawer, NDropdown, NInput, NSelect), TypeScript

---

## 涉及文件

| 操作 | 文件 |
|------|------|
| Modify | `frontend/src/views/testcases/detail.vue` |

---

### Task 1: 扩展 script — 新增 import、响应式状态和辅助数据

**Files:**
- Modify: `frontend/src/views/testcases/detail.vue`

- [ ] **Step 1: 在 `<script setup>` 顶部扩展 naive-ui import**

将现有 import 行：
```ts
import {
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NModal,
  NSelect,
  NSpace,
  NTag,
  useMessage,
} from 'naive-ui'
```
替换为：
```ts
import {
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NDrawer,
  NDrawerContent,
  NDropdown,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NModal,
  NSelect,
  NSpace,
  NTag,
  useMessage,
} from 'naive-ui'
```

- [ ] **Step 2: 在现有 `const cloning = ref(false)` 之后添加编辑抽屉相关状态**

```ts
const showEditDrawer = ref(false)
const saving = ref(false)
const editForm = ref({
  name: '',
  description: '',
  status: 'active',
  governance_status: 'candidate',
  transaction_code: '',
  request_method: 'GET',
  request_uri: '',
  headers_json: '',
  body_json: '',
  assertions_json: '',
})
```

- [ ] **Step 3: 在同一位置添加选项常量**

```ts
const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '激活', value: 'active' },
  { label: '已废弃', value: 'deprecated' },
]

const governanceOptions = [
  { label: '原始录制', value: 'raw' },
  { label: '候选样本', value: 'candidate' },
  { label: '已批准', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已归档', value: 'archived' },
]

const methodOptions = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map(m => ({ label: m, value: m }))
```

- [ ] **Step 4: 添加 `openEdit`、`saveEdit`、`quickSwitchGovernance` 函数（在 `startReplay` 函数之前）**

```ts
function prettifyJsonString(value: unknown) {
  if (typeof value !== 'string' || !value.trim()) return ''
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value as string
  }
}

function openEdit() {
  if (!testCase.value) return
  const tc = testCase.value
  editForm.value = {
    name: tc.name || '',
    description: tc.description || '',
    status: tc.status || 'active',
    governance_status: tc.governance_status || 'candidate',
    transaction_code: tc.transaction_code || '',
    request_method: tc.request_method || 'GET',
    request_uri: tc.request_uri || '',
    headers_json: prettifyJsonString(tc.request_headers),
    body_json: prettifyJsonString(tc.request_body),
    assertions_json: prettifyJsonString(tc.assert_rules),
  }
  showEditDrawer.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    const serializeJson = (value: string) => {
      const text = value.trim()
      if (!text) return undefined
      try { return JSON.stringify(JSON.parse(text)) } catch { return text }
    }
    await testCaseApi.update(caseId, {
      name: editForm.value.name,
      description: editForm.value.description || undefined,
      status: editForm.value.status,
      governance_status: editForm.value.governance_status,
      transaction_code: editForm.value.transaction_code.trim() || undefined,
      request_method: editForm.value.request_method,
      request_uri: editForm.value.request_uri,
      request_headers: serializeJson(editForm.value.headers_json),
      request_body: serializeJson(editForm.value.body_json),
      assert_rules: serializeJson(editForm.value.assertions_json),
    })
    message.success('保存成功')
    showEditDrawer.value = false
    await loadPage()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function quickSwitchGovernance(newStatus: string) {
  try {
    await testCaseApi.update(caseId, { governance_status: newStatus })
    message.success('治理状态已更新')
    await loadPage()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '更新失败')
  }
}
```

- [ ] **Step 5: 手动检查 script 区块，确认无语法错误（如多余逗号、括号不匹配）**

- [ ] **Step 6: Commit**

```bash
cd /home/test/arex-recorder
git add frontend/src/views/testcases/detail.vue
git commit -m "feat(testcase-detail): add edit state, options and handler functions"
```

---

### Task 2: 在顶部按钮栏加"编辑"按钮

**Files:**
- Modify: `frontend/src/views/testcases/detail.vue`（template 区块）

- [ ] **Step 1: 在现有 `<n-space>` 按钮组中加"编辑"按钮**

找到 template 中的按钮区域：
```html
        <n-button v-if="canEdit" @click="cloneCase" :loading="cloning">克隆</n-button>
```

在它**之前**插入：
```html
        <n-button v-if="canEdit" type="default" @click="openEdit">编辑</n-button>
```

完整按钮栏变为：
```html
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button v-if="testCase?.source_recording_id" @click="router.push(`/recording/recordings/${testCase.source_recording_id}`)">来源录制</n-button>
        <n-button type="primary" @click="startReplay" :disabled="!testCase">发起回放</n-button>
        <n-button v-if="canEdit" type="default" @click="openEdit">编辑</n-button>
        <n-button v-if="canEdit" @click="cloneCase" :loading="cloning">克隆</n-button>
        <n-button
          v-if="canEdit"
          @click="quickAddToSuite('smoke')"
          :loading="quickAddingType === 'smoke'"
        >
          加入冒烟套件
        </n-button>
        <n-button
          v-if="canEdit"
          @click="quickAddToSuite('regression')"
          :loading="quickAddingType === 'regression'"
        >
          加入回归套件
        </n-button>
        <n-button v-if="canEdit" @click="openAddSuite">加入套件</n-button>
      </n-space>
```

- [ ] **Step 2: 在 `</template>` 关闭标签之前（现有 `n-modal` 之后）添加编辑抽屉**

```html
  <n-drawer v-model:show="showEditDrawer" :width="640" placement="right">
    <n-drawer-content title="编辑测试用例" closable>
      <n-form :model="editForm" label-placement="top">
        <n-form-item label="用例名称">
          <n-input v-model:value="editForm.name" placeholder="用例名称" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="editForm.description" type="textarea" :rows="2" />
        </n-form-item>
        <n-form-item label="状态">
          <n-select v-model:value="editForm.status" :options="statusOptions" />
        </n-form-item>
        <n-form-item label="治理状态">
          <n-select v-model:value="editForm.governance_status" :options="governanceOptions" />
        </n-form-item>
        <n-form-item label="交易码">
          <n-input v-model:value="editForm.transaction_code" placeholder="如 OPEN_ACCOUNT" />
        </n-form-item>
        <n-form-item label="请求方法">
          <n-select v-model:value="editForm.request_method" :options="methodOptions" style="width:120px" />
        </n-form-item>
        <n-form-item label="请求 URI">
          <n-input v-model:value="editForm.request_uri" placeholder="/api/path" />
        </n-form-item>
        <n-form-item label="请求 Headers (JSON)">
          <n-input
            v-model:value="editForm.headers_json"
            type="textarea"
            :rows="3"
            placeholder='{"Content-Type": "application/json"}'
            style="font-family:monospace"
          />
        </n-form-item>
        <n-form-item label="请求 Body">
          <n-input
            v-model:value="editForm.body_json"
            type="textarea"
            :rows="6"
            placeholder="支持 JSON / XML / 普通文本"
            style="font-family:monospace"
          />
        </n-form-item>
        <n-form-item label="断言规则 (JSON)">
          <n-input
            v-model:value="editForm.assertions_json"
            type="textarea"
            :rows="4"
            placeholder='[{"path": "/code", "op": "eq", "value": "0"}]'
            style="font-family:monospace"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditDrawer = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="saveEdit">保存</n-button>
        </n-space>
      </template>
    </n-drawer-content>
  </n-drawer>
```

- [ ] **Step 3: 在浏览器打开测试用例详情页，确认"编辑"按钮出现，点击后抽屉弹出且字段已预填当前数据**

- [ ] **Step 4: 修改某个字段（如名称），保存，确认详情页数据已更新**

- [ ] **Step 5: Commit**

```bash
cd /home/test/arex-recorder
git add frontend/src/views/testcases/detail.vue
git commit -m "feat(testcase-detail): add edit button and full-field edit drawer"
```

---

### Task 3: 治理状态快捷切换下拉

**Files:**
- Modify: `frontend/src/views/testcases/detail.vue`（template 区块）

- [ ] **Step 1: 找到 `n-descriptions` 中治理状态行并添加快捷切换下拉**

找到：
```html
        <n-descriptions-item label="治理状态">{{ governanceLabelMap[testCase.governance_status] || testCase.governance_status }}</n-descriptions-item>
```

替换为：
```html
        <n-descriptions-item label="治理状态">
          <n-space align="center" :size="8">
            <span>{{ governanceLabelMap[testCase.governance_status] || testCase.governance_status }}</span>
            <n-dropdown
              v-if="canEdit"
              trigger="click"
              :options="governanceOptions.map(o => ({ ...o, disabled: o.value === testCase.governance_status }))"
              @select="quickSwitchGovernance"
            >
              <n-button size="tiny" quaternary>切换 ▾</n-button>
            </n-dropdown>
          </n-space>
        </n-descriptions-item>
```

- [ ] **Step 2: 在浏览器详情页确认治理状态旁出现"切换 ▾"按钮，点击后展示下拉菜单，当前状态已禁用**

- [ ] **Step 3: 选择一个新治理状态，确认页面数据更新且右上角出现成功提示**

- [ ] **Step 4: 确认非 admin/editor 角色登录时"切换 ▾"按钮不显示**

- [ ] **Step 5: Commit**

```bash
cd /home/test/arex-recorder
git add frontend/src/views/testcases/detail.vue
git commit -m "feat(testcase-detail): add governance status quick-switch dropdown"
```
