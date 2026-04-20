<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/suites')">测试套件</n-breadcrumb-item>
        <n-breadcrumb-item>{{ suite?.name || `套件 #${suiteId}` }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="router.push('/suites')">返回</n-button>
        <n-button @click="loadPage">刷新</n-button>
        <n-button v-if="canEdit" type="primary" @click="openAddCase">添加用例</n-button>
        <n-button v-if="canEdit" type="success" :loading="running" @click="openRunModal">运行套件</n-button>
      </n-space>
    </n-space>

    <n-card v-if="suite" :title="suite.name">
      <n-descriptions bordered :column="2">
        <n-descriptions-item label="套件类型">{{ suiteTypeLabelMap[suite.suite_type] || suite.suite_type }}</n-descriptions-item>
        <n-descriptions-item label="描述">{{ suite.description || '-' }}</n-descriptions-item>
        <n-descriptions-item label="用例数量">{{ suite.cases?.length || 0 }}</n-descriptions-item>
        <n-descriptions-item label="创建时间">{{ formatDateTime(suite.created_at) }}</n-descriptions-item>
        <n-descriptions-item label="更新时间">{{ formatDateTime(suite.updated_at) }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="套件用例">
      <template #header-extra>
        <n-text depth="3">共 {{ caseRows.length }} 个用例</n-text>
      </template>
      <n-data-table :columns="columns" :data="caseRows" :loading="loading || caseRowsLoading" :pagination="{ pageSize: 12 }" />
    </n-card>
  </n-space>

  <!-- 运行套件配置弹窗 -->
  <n-modal v-model:show="showRunModal" title="运行套件配置" preset="card" style="width:500px">
    <n-form label-placement="left" label-width="110px" :style="{ padding: '4px 0' }">
      <n-form-item label="回放目标应用">
        <n-select
          v-model:value="runConfig.target_application_id"
          :options="appOptions"
          placeholder="默认使用用例所属应用（SIT）"
          clearable
          filterable
        />
      </n-form-item>
      <n-form-item label="">
        <n-text depth="3" style="font-size:12px">
          选择与用例不同的应用可回放到其他环境（如 UAT），用于差异对比
        </n-text>
      </n-form-item>
      <n-form-item label="忽略字段">
        <n-dynamic-tags v-model:value="runConfig.ignore_fields" placeholder="输入字段名后回车" />
      </n-form-item>
      <n-form-item label="并发数">
        <n-input-number v-model:value="runConfig.concurrency" :min="1" :max="50" style="width:120px" />
      </n-form-item>
      <n-form-item label="超时（ms）">
        <n-input-number v-model:value="runConfig.timeout_ms" :min="500" :max="60000" :step="500" style="width:150px" />
      </n-form-item>
      <n-form-item label="智能降噪">
        <n-switch v-model:value="runConfig.smart_noise_reduction" />
        <n-text depth="3" style="margin-left:8px;font-size:12px">自动忽略时间戳等动态字段</n-text>
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showRunModal = false">取消</n-button>
        <n-button type="success" :loading="running" @click="doRunSuite">开始回放</n-button>
      </n-space>
    </template>
  </n-modal>

  <!-- 添加用例弹窗 -->
  <n-modal v-model:show="showAddCase" title="添加用例到套件" preset="card" style="width:760px">
    <n-space vertical :size="12">
      <!-- 搜索栏 -->
      <n-space>
        <n-input
          v-model:value="caseSearch"
          placeholder="搜索名称 / 交易码"
          clearable
          style="width:220px"
        />
        <n-text depth="3" style="line-height:34px">
          已选 {{ selectedCaseIds.length }} 个 / 共 {{ filteredCases.length }} 个
        </n-text>
      </n-space>
      <!-- 用例表格 -->
      <n-data-table
        :columns="addCaseCols"
        :data="filteredCases"
        :loading="caseOptionsLoading"
        :row-key="(row: any) => row.id"
        v-model:checked-row-keys="selectedCaseIds"
        :pagination="{ pageSize: 8 }"
        size="small"
        max-height="380"
      />
    </n-space>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showAddCase = false">取消</n-button>
        <n-button type="primary" :loading="savingCases" @click="addCases">
          确认添加 ({{ selectedCaseIds.length }})
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NDynamicTags,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NModal,
  NSelect,
  NSpace,
  NSwitch,
  NTag,
  NText,
  useMessage,
} from 'naive-ui'
import { suiteApi } from '@/api/suites'
import { testCaseApi } from '@/api/testcases'
import { applicationApi } from '@/api/applications'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'

type SuiteCase = {
  test_case_id: number
  order_index: number
}

type SuiteDetail = {
  id: number
  name: string
  description?: string | null
  suite_type: string
  created_at?: string | null
  updated_at?: string | null
  cases: SuiteCase[]
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const suiteId = Number(route.params.id)

const suite = ref<SuiteDetail | null>(null)
const caseMap = ref<Record<number, any>>({})
const allCases = ref<any[]>([])
const loading = ref(false)
const caseRowsLoading = ref(false)
const running = ref(false)
const showAddCase = ref(false)
const savingCases = ref(false)
const caseOptionsLoading = ref(false)
const selectedCaseIds = ref<(string | number)[]>([])
const caseSearch = ref('')

// 运行套件配置
const showRunModal = ref(false)
const appOptions = ref<{ label: string; value: number }[]>([])
const runConfig = ref({
  target_application_id: null as number | null,
  ignore_fields: [] as string[],
  concurrency: 5,
  timeout_ms: 5000,
  smart_noise_reduction: false,
})

const suiteTypeLabelMap: Record<string, string> = {
  smoke: '冒烟',
  regression: '回归',
}

const governanceLabelMap: Record<string, string> = {
  raw: '原始录制',
  candidate: '候选样本',
  approved: '已批准',
  rejected: '已拒绝',
  archived: '已归档',
}

const filteredCases = computed(() => {
  const q = caseSearch.value.trim().toLowerCase()
  if (!q) return allCases.value
  return allCases.value.filter(
    (c) =>
      (c.name || '').toLowerCase().includes(q) ||
      (c.transaction_code || '').toLowerCase().includes(q),
  )
})

const caseRows = computed(() =>
  (suite.value?.cases || []).map((item) => {
    const testCase = caseMap.value[item.test_case_id]
    return {
      order_index: item.order_index,
      test_case_id: item.test_case_id,
      name: testCase?.name || `用例 #${item.test_case_id}`,
      transaction_code: testCase?.transaction_code || '-',
      governance_status: testCase?.governance_status || '-',
      request_method: testCase?.request_method || '-',
      request_uri: testCase?.request_uri || '-',
      status: testCase?.status || '-',
    }
  }),
)

const columns = [
  { title: '顺序', key: 'order_index', width: 70 },
  {
    title: '用例名称',
    key: 'name',
    render: (row: any) =>
      h(NButton, { text: true, type: 'primary', onClick: () => router.push(`/testcases/${row.test_case_id}`) }, () => row.name),
  },
  {
    title: '请求',
    key: 'request_uri',
    render: (row: any) => h('span', [h('b', { style: 'margin-right:4px' }, row.request_method), row.request_uri]),
  },
  { title: '交易码', key: 'transaction_code', width: 140 },
  { title: '治理状态', key: 'governance_status', width: 100 },
  { title: '状态', key: 'status', width: 100 },
]

const addCaseCols = [
  { type: 'selection' as const },
  { title: '名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '请求',
    key: 'request_uri',
    width: 220,
    render: (row: any) =>
      h('span', [h('b', { style: 'margin-right:4px' }, row.request_method), row.request_uri]),
  },
  { title: '交易码', key: 'transaction_code', width: 140 },
  {
    title: '治理状态',
    key: 'governance_status',
    width: 100,
    render: (row: any) =>
      h(NTag, { size: 'small', type: row.governance_status === 'approved' ? 'success' : 'default' },
        () => governanceLabelMap[row.governance_status] || row.governance_status || '-'),
  },
]

async function loadAllCases() {
  caseOptionsLoading.value = true
  try {
    const res = await testCaseApi.list({ limit: 500 })
    allCases.value = res.data
  } catch (error: any) {
    allCases.value = []
    message.error(error.response?.data?.detail || '加载测试用例失败')
  } finally {
    caseOptionsLoading.value = false
  }
}

async function loadReferencedCases(caseIds: number[]) {
  if (!caseIds.length) {
    caseMap.value = {}
    return
  }
  caseRowsLoading.value = true
  try {
    const records = await Promise.all(
      caseIds.map(async (id) => {
        try {
          const res = await testCaseApi.get(id)
          return [id, res.data] as const
        } catch {
          return [id, null] as const
        }
      }),
    )
    caseMap.value = Object.fromEntries(records.filter(([, item]) => item != null))
  } finally {
    caseRowsLoading.value = false
  }
}

async function loadSuite() {
  loading.value = true
  try {
    const res = await suiteApi.get(suiteId)
    suite.value = res.data
    await loadReferencedCases((res.data.cases || []).map((item: SuiteCase) => item.test_case_id))
  } catch (error: any) {
    suite.value = null
    caseMap.value = {}
    message.error(error.response?.data?.detail || '加载套件详情失败')
  } finally {
    loading.value = false
  }
}

async function loadPage() {
  await loadSuite()
}

async function openAddCase() {
  caseSearch.value = ''
  await loadAllCases()
  const existing = suite.value?.cases?.map((item) => item.test_case_id) || []
  selectedCaseIds.value = [...existing]
  showAddCase.value = true
}

async function addCases() {
  if (!suite.value) return
  savingCases.value = true
  try {
    await suiteApi.setCases(suite.value.id, { case_ids: selectedCaseIds.value as number[] })
    message.success('套件用例已更新')
    showAddCase.value = false
    await loadSuite()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '更新套件失败')
  } finally {
    savingCases.value = false
  }
}

async function openRunModal() {
  // 加载应用列表（用于切换回放目标）
  if (!appOptions.value.length) {
    try {
      const res = await applicationApi.list()
      appOptions.value = res.data.map((app: any) => ({ label: app.name, value: app.id }))
    } catch {
      appOptions.value = []
    }
  }
  // 重置配置
  runConfig.value = {
    target_application_id: null,
    ignore_fields: [],
    concurrency: 5,
    timeout_ms: 5000,
    smart_noise_reduction: false,
  }
  showRunModal.value = true
}

async function doRunSuite() {
  if (!suite.value) return
  running.value = true
  try {
    const payload: any = {
      concurrency: runConfig.value.concurrency,
      timeout_ms: runConfig.value.timeout_ms,
      smart_noise_reduction: runConfig.value.smart_noise_reduction,
    }
    if (runConfig.value.target_application_id != null) {
      payload.target_application_id = runConfig.value.target_application_id
    }
    if (runConfig.value.ignore_fields.length > 0) {
      payload.ignore_fields = runConfig.value.ignore_fields
    }
    const res = await suiteApi.run(suite.value.id, payload)
    message.success(`回放任务 #${res.data.job_id} 已启动`)
    showRunModal.value = false
    router.push(`/results/${res.data.job_id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '运行套件失败')
  } finally {
    running.value = false
  }
}

onMounted(() => {
  void loadPage()
})
</script>
