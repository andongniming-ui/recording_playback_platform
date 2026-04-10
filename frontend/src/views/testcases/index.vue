<template>
  <n-space vertical :size="12">
    <n-space justify="space-between">
      <n-h2 style="margin:0">测试用例库</n-h2>
      <n-space>
        <n-button @click="exportCases">导出</n-button>
        <n-button type="primary" @click="openCreate">+ 新增用例</n-button>
      </n-space>
    </n-space>

    <!-- 过滤栏 -->
    <n-space>
      <n-select
        v-model:value="filterAppId"
        :options="appOptions"
        clearable
        placeholder="选择应用"
        style="width:180px"
        @update:value="loadCases"
      />
      <n-select
        v-model:value="filterStatus"
        :options="statusOptions"
        clearable
        placeholder="状态"
        style="width:130px"
        @update:value="loadCases"
      />
      <n-input
        v-model:value="filterSearch"
        clearable
        placeholder="搜索名称/URI"
        style="width:220px"
        @input="loadCases"
      />
    </n-space>

    <n-data-table
      :columns="columns"
      :data="cases"
      :loading="loading"
      :pagination="{ pageSize: 10 }"
    />
  </n-space>

  <!-- 新增/编辑抽屉 -->
  <n-drawer v-model:show="showDrawer" :width="640" placement="right">
    <n-drawer-content :title="editingId ? '编辑测试用例' : '新增测试用例'" closable>
      <n-form :model="form" label-placement="top">
        <n-form-item label="用例名称">
          <n-input v-model:value="form.name" placeholder="用例名称" />
        </n-form-item>
        <n-form-item label="应用">
          <n-select v-model:value="form.app_id" :options="appOptions" placeholder="选择应用" />
        </n-form-item>
        <n-form-item label="状态">
          <n-select v-model:value="form.status" :options="statusOptions" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="form.description" type="textarea" :rows="2" />
        </n-form-item>
        <n-form-item label="请求方法">
          <n-select
            v-model:value="form.method"
            :options="methodOptions"
            style="width:120px"
          />
        </n-form-item>
        <n-form-item label="请求 URI">
          <n-input v-model:value="form.uri" placeholder="/api/path" />
        </n-form-item>
        <n-form-item label="请求 Headers (JSON)">
          <n-input
            v-model:value="form.headers_json"
            type="textarea"
            :rows="3"
            placeholder='{"Content-Type": "application/json"}'
            style="font-family:monospace"
          />
        </n-form-item>
        <n-form-item label="请求 Body (JSON)">
          <n-input
            v-model:value="form.body_json"
            type="textarea"
            :rows="6"
            placeholder='{"key": "value"}'
            style="font-family:monospace"
          />
        </n-form-item>
        <n-form-item label="期望断言 (JSON)">
          <n-input
            v-model:value="form.assertions_json"
            type="textarea"
            :rows="4"
            placeholder='{"status_code": 200}'
            style="font-family:monospace"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showDrawer = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="save">保存</n-button>
        </n-space>
      </template>
    </n-drawer-content>
  </n-drawer>

  <!-- 加入套件弹窗 -->
  <n-modal v-model:show="showAddSuiteModal" title="加入测试套件" preset="card" style="width:400px">
    <n-form :model="addSuiteForm" label-placement="left" label-width="80px">
      <n-form-item label="套件 ID">
        <n-input-number v-model:value="addSuiteForm.suite_id" :min="1" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showAddSuiteModal = false">取消</n-button>
        <n-button type="primary" :loading="addingSuite" @click="doAddToSuite">确认</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import {
  NSpace, NH2, NButton, NDataTable, NSelect, NInput, NInputNumber,
  NDrawer, NDrawerContent, NModal, NForm, NFormItem, NTag, NPopconfirm, useMessage
} from 'naive-ui'
import { testCaseApi } from '@/api/testcases'
import { applicationApi } from '@/api/applications'

const message = useMessage()

const cases = ref<any[]>([])
const loading = ref(false)
const filterAppId = ref<number | null>(null)
const filterStatus = ref<string | null>(null)
const filterSearch = ref('')
const appOptions = ref<any[]>([])

const showDrawer = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  name: '', app_id: null as number | null, status: 'active', description: '',
  method: 'GET', uri: '', headers_json: '', body_json: '', assertions_json: '',
})

const showAddSuiteModal = ref(false)
const addingSuite = ref(false)
const addSuiteForm = ref({ suite_id: null as number | null, case_id: null as number | null })

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '激活', value: 'active' },
  { label: '已废弃', value: 'deprecated' },
]

const methodOptions = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map(m => ({ label: m, value: m }))

const statusTagMap: Record<string, any> = {
  draft: 'default', active: 'success', deprecated: 'error',
}

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name', ellipsis: { tooltip: true } },
  { title: '应用', key: 'app_name', width: 120 },
  {
    title: '请求', key: 'uri',
    render: (r: any) => h('span', [
      h('b', { style: 'margin-right:4px' }, r.method || 'GET'),
      r.uri,
    ]),
  },
  {
    title: '状态', key: 'status', width: 80,
    render: (r: any) => h(NTag, { type: statusTagMap[r.status] || 'default', size: 'small' }, () => r.status),
  },
  {
    title: '创建时间', key: 'created_at', width: 155,
    render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' '),
  },
  {
    title: '操作', key: 'actions',
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => openEdit(r) }, () => '编辑'),
      h(NButton, { size: 'tiny', type: 'info', onClick: () => cloneCase(r.id) }, () => '克隆'),
      h(NButton, { size: 'tiny', onClick: () => openAddSuite(r.id) }, () => '加入套件'),
      h(NPopconfirm, { onPositiveClick: () => deleteCase(r.id) }, {
        default: () => '确认删除?',
        trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
      }),
    ]),
  },
]

async function loadApps() {
  try {
    const res = await applicationApi.list()
    appOptions.value = res.data.map((a: any) => ({ label: a.name, value: a.id }))
  } catch {
    // ignore
  }
}

async function loadCases() {
  loading.value = true
  try {
    const params: any = {}
    if (filterAppId.value) params.app_id = filterAppId.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterSearch.value) params.search = filterSearch.value
    const res = await testCaseApi.list(params)
    cases.value = res.data
  } catch {
    message.error('加载用例失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = {
    name: '', app_id: null, status: 'active', description: '',
    method: 'GET', uri: '', headers_json: '', body_json: '', assertions_json: '',
  }
  showDrawer.value = true
}

function openEdit(tc: any) {
  editingId.value = tc.id
  form.value = {
    name: tc.name || '',
    app_id: tc.app_id || null,
    status: tc.status || 'active',
    description: tc.description || '',
    method: tc.method || 'GET',
    uri: tc.uri || '',
    headers_json: tc.headers ? JSON.stringify(tc.headers, null, 2) : '',
    body_json: tc.body ? JSON.stringify(tc.body, null, 2) : '',
    assertions_json: tc.assertions ? JSON.stringify(tc.assertions, null, 2) : '',
  }
  showDrawer.value = true
}

async function save() {
  saving.value = true
  try {
    const parseJson = (s: string) => {
      if (!s.trim()) return undefined
      try { return JSON.parse(s) } catch { return s }
    }
    const payload: any = {
      ...form.value,
      headers: parseJson(form.value.headers_json),
      body: parseJson(form.value.body_json),
      assertions: parseJson(form.value.assertions_json),
    }
    delete payload.headers_json
    delete payload.body_json
    delete payload.assertions_json
    if (editingId.value) {
      await testCaseApi.update(editingId.value, payload)
    } else {
      await testCaseApi.create(payload)
    }
    message.success('保存成功')
    showDrawer.value = false
    await loadCases()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function cloneCase(id: number) {
  try {
    await testCaseApi.clone(id)
    message.success('克隆成功')
    await loadCases()
  } catch {
    message.error('克隆失败')
  }
}

async function deleteCase(id: number) {
  try {
    await testCaseApi.delete(id)
    message.success('删除成功')
    await loadCases()
  } catch {
    message.error('删除失败')
  }
}

async function exportCases() {
  try {
    const params: any = {}
    if (filterAppId.value) params.app_id = filterAppId.value
    const res = await testCaseApi.exportCases(params)
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'test-cases-export.json'
    a.click()
    URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch {
    message.error('导出失败')
  }
}

function openAddSuite(caseId: number) {
  addSuiteForm.value = { suite_id: null, case_id: caseId }
  showAddSuiteModal.value = true
}

async function doAddToSuite() {
  if (!addSuiteForm.value.suite_id) {
    message.warning('请输入套件 ID')
    return
  }
  addingSuite.value = true
  try {
    await testCaseApi.addToSuite(addSuiteForm.value.case_id!, { suite_id: addSuiteForm.value.suite_id })
    message.success('已加入套件')
    showAddSuiteModal.value = false
  } catch (e: any) {
    message.error(e.response?.data?.detail || '操作失败')
  } finally {
    addingSuite.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadApps(), loadCases()])
})
</script>
