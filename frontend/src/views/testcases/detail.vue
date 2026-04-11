<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/testcases')">测试用例</n-breadcrumb-item>
        <n-breadcrumb-item>{{ testCase?.name || `用例 #${caseId}` }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button v-if="testCase?.source_recording_id" @click="router.push(`/recording/recordings/${testCase.source_recording_id}`)">来源录制</n-button>
        <n-button type="primary" @click="startReplay" :disabled="!testCase">发起回放</n-button>
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
    </n-space>

    <n-card v-if="testCase" :title="testCase.name">
      <template #header-extra>
        <n-tag :type="statusTagMap[testCase.status] || 'default'">
          {{ statusLabelMap[testCase.status] || testCase.status }}
        </n-tag>
      </template>

      <n-descriptions bordered :column="2">
        <n-descriptions-item label="所属应用">{{ applicationName }}</n-descriptions-item>
        <n-descriptions-item label="来源录制">{{ testCase.source_recording_id || '-' }}</n-descriptions-item>
        <n-descriptions-item label="交易码">{{ testCase.transaction_code || '-' }}</n-descriptions-item>
        <n-descriptions-item label="治理状态">{{ governanceLabelMap[testCase.governance_status] || testCase.governance_status }}</n-descriptions-item>
        <n-descriptions-item label="请求">{{ `${testCase.request_method} ${testCase.request_uri}` }}</n-descriptions-item>
        <n-descriptions-item label="期望状态码">{{ testCase.expected_status ?? '-' }}</n-descriptions-item>
        <n-descriptions-item label="场景键" :span="2">{{ testCase.scene_key || '-' }}</n-descriptions-item>
        <n-descriptions-item label="标签">{{ testCase.tags || '-' }}</n-descriptions-item>
        <n-descriptions-item label="性能阈值">{{ testCase.perf_threshold_ms != null ? `${testCase.perf_threshold_ms}ms` : '-' }}</n-descriptions-item>
        <n-descriptions-item label="描述" :span="2">{{ testCase.description || '-' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-grid :cols="2" :x-gap="16">
      <n-grid-item>
        <n-card title="请求头">
          <pre class="code-block">{{ prettyText(testCase?.request_headers) }}</pre>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="请求体">
          <pre class="code-block">{{ prettyText(testCase?.request_body) }}</pre>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="期望响应">
          <pre class="code-block">{{ prettyText(testCase?.expected_response) }}</pre>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card title="断言与忽略字段">
          <n-space vertical>
            <div>
              <div class="section-title">断言规则</div>
              <pre class="code-block compact">{{ prettyText(testCase?.assert_rules) }}</pre>
            </div>
            <div>
              <div class="section-title">忽略字段</div>
              <pre class="code-block compact">{{ prettyText(testCase?.ignore_fields) }}</pre>
            </div>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>

  <n-modal v-model:show="showAddSuiteModal" title="加入测试套件" preset="card" style="width:420px">
    <n-form :model="addSuiteForm" label-placement="left" label-width="80px">
      <n-form-item label="选择套件">
        <n-select
          v-model:value="addSuiteForm.suite_id"
          :options="suiteOptions"
          filterable
          placeholder="请选择测试套件"
        />
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
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
import { applicationApi } from '@/api/applications'
import { suiteApi } from '@/api/suites'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'

type TestCaseDetail = {
  id: number
  name: string
  description?: string | null
  application_id?: number | null
  source_recording_id?: number | null
  status: string
  governance_status: string
  transaction_code?: string | null
  scene_key?: string | null
  tags?: string | null
  request_method: string
  request_uri: string
  request_headers?: string | null
  request_body?: string | null
  expected_status?: number | null
  expected_response?: string | null
  assert_rules?: string | null
  ignore_fields?: string | null
  perf_threshold_ms?: number | null
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const caseId = Number(route.params.id)

const testCase = ref<TestCaseDetail | null>(null)
const applicationName = ref('-')
const cloning = ref(false)
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

const showAddSuiteModal = ref(false)
const addingSuite = ref(false)
const quickAddingType = ref<string | null>(null)
const suiteOptions = ref<{ label: string; value: number }[]>([])
const addSuiteForm = ref({ suite_id: null as number | null })

const statusTagMap: Record<string, 'default' | 'success' | 'error'> = {
  draft: 'default',
  active: 'success',
  deprecated: 'error',
}

const statusLabelMap: Record<string, string> = {
  draft: '草稿',
  active: '激活',
  deprecated: '已废弃',
}

const governanceLabelMap: Record<string, string> = {
  raw: '原始录制',
  candidate: '候选样本',
  approved: '已批准',
  rejected: '已拒绝',
  archived: '已归档',
}

function prettyText(value?: string | null) {
  if (!value) return '-'
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

async function loadPage() {
  try {
    const res = await testCaseApi.get(caseId)
    testCase.value = res.data
    if (res.data.application_id != null) {
      const appRes = await applicationApi.get(res.data.application_id)
      applicationName.value = appRes.data.name
    } else {
      applicationName.value = '-'
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载测试用例失败')
  }
}

async function loadSuites() {
  try {
    const res = await suiteApi.list()
    suiteOptions.value = res.data.map((item: { id: number; name: string }) => ({
      label: `${item.name} (#${item.id})`,
      value: item.id,
    }))
  } catch (error: any) {
    suiteOptions.value = []
    message.error(error.response?.data?.detail || '加载测试套件失败')
  }
}

async function ensureRecommendedSuite(suiteType: 'smoke' | 'regression') {
  const existing = await suiteApi.list({ suite_type: suiteType, limit: 200 })
  const appScopedName = applicationName.value !== '-' ? `${applicationName.value}-${suiteType === 'smoke' ? '冒烟套件' : '回归套件'}` : ''
  const matched = existing.data.find((item: any) => item.name === appScopedName) || existing.data[0]
  if (matched) {
    return matched
  }
  const created = await suiteApi.create({
    name: appScopedName || `${suiteType === 'smoke' ? '冒烟' : '回归'}套件`,
    description: `由测试用例 #${caseId} 快速创建`,
    suite_type: suiteType,
  })
  return created.data
}

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

function startReplay() {
  if (!testCase.value) return
  const query: Record<string, string> = {
    case_ids: String(testCase.value.id),
  }
  if (testCase.value.application_id != null) {
    query.application_id = String(testCase.value.application_id)
  }
  router.push({ path: '/replay', query })
}

async function cloneCase() {
  cloning.value = true
  try {
    const res = await testCaseApi.clone(caseId)
    message.success('克隆成功')
    router.push(`/testcases/${res.data.id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '克隆失败')
  } finally {
    cloning.value = false
  }
}

async function openAddSuite() {
  addSuiteForm.value = { suite_id: null }
  showAddSuiteModal.value = true
  await loadSuites()
}

async function doAddToSuite() {
  if (!addSuiteForm.value.suite_id) {
    message.warning('请选择测试套件')
    return
  }
  addingSuite.value = true
  try {
    await testCaseApi.addToSuite(caseId, { suite_id: addSuiteForm.value.suite_id })
    message.success('已加入套件')
    showAddSuiteModal.value = false
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加入套件失败')
  } finally {
    addingSuite.value = false
  }
}

async function quickAddToSuite(suiteType: 'smoke' | 'regression') {
  if (!testCase.value) return
  quickAddingType.value = suiteType
  try {
    const suite = await ensureRecommendedSuite(suiteType)
    await testCaseApi.addToSuite(caseId, { suite_id: suite.id })
    message.success(`已加入${suiteType === 'smoke' ? '冒烟' : '回归'}套件`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加入推荐套件失败')
  } finally {
    quickAddingType.value = null
  }
}

onMounted(() => {
  void loadPage()
})
</script>

<style scoped>
.code-block {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 360px;
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  background: #f8f8f8;
  font-family: monospace;
  font-size: 12px;
}

.code-block.compact {
  max-height: 150px;
}

.section-title {
  margin-bottom: 8px;
  font-size: 13px;
  color: #666;
}
</style>
