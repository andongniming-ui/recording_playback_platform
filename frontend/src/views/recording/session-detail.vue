<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/recording')">录制中心</n-breadcrumb-item>
        <n-breadcrumb-item>{{ session?.name || `会话 #${sessionId}` }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button v-if="session" @click="router.push(`/applications/${session.application_id}`)">返回应用</n-button>
        <n-button
          v-if="canEdit && recordings.length > 0"
          @click="openBatchModal"
        >
          批量生成用例
        </n-button>
        <n-button
          v-if="canEdit && session && session.status === 'idle'"
          type="primary"
          @click="startSession"
          :loading="starting"
        >
          开始录制
        </n-button>
        <n-button
          v-if="canEdit && session && session.status === 'active'"
          type="warning"
          @click="stopSession"
          :loading="stopping"
        >
          停止录制
        </n-button>
      </n-space>
    </n-space>

    <n-card v-if="session" :title="session.name">
      <template #header-extra>
        <n-tag :type="sessionStatusTagType[session.status] || 'default'">
          {{ sessionStatusLabelMap[session.status] || session.status }}
        </n-tag>
      </template>
      <n-descriptions bordered :column="2">
        <n-descriptions-item label="所属应用">{{ appName }}</n-descriptions-item>
        <n-descriptions-item label="录制数量">{{ session.total_count }}</n-descriptions-item>
        <n-descriptions-item label="交易码过滤">{{ formatPrefixSummary(session.recording_filter_prefixes) }}</n-descriptions-item>
        <n-descriptions-item label="开始时间">{{ formatDateTime(session.start_time) }}</n-descriptions-item>
        <n-descriptions-item label="结束时间">{{ formatDateTime(session.end_time) }}</n-descriptions-item>
        <n-descriptions-item label="创建时间">{{ formatDateTime(session.created_at) }}</n-descriptions-item>
        <n-descriptions-item label="错误信息">{{ session.error_message || '-' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="录制数据">
      <n-alert type="info" :show-icon="false" style="margin-bottom: 12px">
        创建会话后先点击“开始录制”，真实请求正常跑起来后再点击“停止录制”。平台会自动从 arex-storage 收集这次录制的数据并把状态推进到“收集中 / 已完成”。
      </n-alert>
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="recordingGovernanceStatus"
            clearable
            :options="governanceOptions"
            placeholder="治理状态"
            style="width: 160px"
            @update:value="loadRecordings"
          />
          <n-input
            v-model:value="recordingTransactionCode"
            clearable
            placeholder="交易码"
            style="width: 180px"
            @keyup.enter="loadRecordings"
          />
          <n-checkbox v-model:checked="duplicateOnly" @update:checked="loadRecordings">仅重复样本</n-checkbox>
          <n-input
            v-model:value="recordingSearch"
            clearable
            placeholder="搜索路径/交易码"
            style="width: 220px"
          />
          <n-button @click="loadRecordings">查询</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="recordingColumns"
        :data="filteredRecordings"
        :loading="recordingsLoading"
        :pagination="{ pageSize: 12 }"
      />
    </n-card>
  </n-space>

  <!-- 批量生成用例 Modal（两步：前缀输入 → 冲突检测结果） -->
  <n-modal
    v-model:show="showBatchModal"
    :title="batchStep === 'prefix' ? '批量生成测试用例' : '冲突检测结果'"
    preset="card"
    style="width: 480px"
    :closable="!batchGenerating"
    :mask-closable="!batchGenerating"
  >
    <template v-if="batchStep === 'prefix'">
      <n-space vertical>
        <span>将对本会话 {{ filteredRecordings.length }} 条录制生成用例</span>
        <n-form label-placement="left" label-width="100px">
          <n-form-item label="用例名称前缀">
            <n-input
              v-model:value="batchPrefix"
              placeholder="如：滴滴计价"
              @keyup.enter="doBatchCheck"
            />
          </n-form-item>
        </n-form>
      </n-space>
    </template>
    <template v-else>
      <n-space vertical>
        <n-alert v-if="batchCheckItems.filter(i => !i.has_existing).length > 0" type="success" :show-icon="true">
          {{ batchCheckItems.filter(i => !i.has_existing).length }} 条可生成
        </n-alert>
        <n-alert v-if="batchCheckItems.filter(i => i.has_existing).length > 0" type="warning" :show-icon="true">
          {{ batchCheckItems.filter(i => i.has_existing).length }} 条已有用例（{{
            batchCheckItems.filter(i => i.has_existing).map(i => i.transaction_code || `#${i.recording_id}`).join('、')
          }}），将自动跳过
        </n-alert>
        <n-alert v-if="batchCheckItems.filter(i => !i.has_existing).length === 0" type="info">
          所有录制均已有对应用例，无需重复生成
        </n-alert>
      </n-space>
    </template>
    <template #footer>
      <n-space justify="end">
        <template v-if="batchStep === 'prefix'">
          <n-button @click="showBatchModal = false">取消</n-button>
          <n-button type="primary" :loading="batchChecking" @click="doBatchCheck">检测冲突 →</n-button>
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

  <n-modal v-model:show="showConvertModal" title="由录制生成测试用例" preset="card" style="width: 420px">
    <n-form :model="convertForm" label-placement="left" label-width="100px">
      <n-form-item label="用例名称">
        <n-input v-model:value="convertForm.name" placeholder="留空则自动生成" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showConvertModal = false">取消</n-button>
        <n-button type="primary" :loading="converting" @click="doConvert">生成</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, h, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NAlert,
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NCheckbox,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NSelect,
  NSpace,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'
import type { RecordingSubCall } from '@/utils/recording'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'

type SessionRow = {
  id: number
  application_id: number
  name: string
  status: string
  total_count: number
  error_message?: string | null
  recording_filter_prefixes?: string[] | null
  start_time?: string | null
  end_time?: string | null
  created_at: string
}

type RecordingRow = {
  id: number
  request_method: string
  request_uri: string
  transaction_code?: string | null
  governance_status: string
  duplicate_count?: number | null
  response_status?: number | null
  latency_ms?: number | null
  sub_calls?: RecordingSubCall[] | string | null
  recorded_at: string
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const sessionId = Number(route.params.id)

const session = ref<SessionRow | null>(null)
const appName = ref('-')
const recordings = ref<RecordingRow[]>([])
const recordingsLoading = ref(false)
const recordingSearch = ref('')
const recordingTransactionCode = ref('')
const recordingGovernanceStatus = ref<string | null>(null)
const duplicateOnly = ref(false)
const starting = ref(false)
const stopping = ref(false)
const showConvertModal = ref(false)
const converting = ref(false)
const convertingRecordingId = ref<number | null>(null)
const convertForm = ref({ name: '' })
const pollingTimer = ref<number | null>(null)

// 批量生成用例
const showBatchModal = ref(false)
const batchStep = ref<'prefix' | 'check'>('prefix')
const batchPrefix = ref('')
const batchChecking = ref(false)
const batchGenerating = ref(false)
const batchCheckItems = ref<Array<{
  recording_id: number
  transaction_code: string | null
  has_existing: boolean
  existing_case_id: number | null
  existing_case_name: string | null
}>>([])

function formatPrefixSummary(prefixes?: string[] | null) {
  if (!prefixes || prefixes.length === 0) {
    return '-'
  }
  return prefixes.join(', ')
}

const sessionStatusTagType: Record<string, NonNullable<TagProps['type']>> = {
  idle: 'default',
  active: 'info',
  collecting: 'warning',
  done: 'success',
  error: 'error',
}

const sessionStatusLabelMap: Record<string, string> = {
  idle: '待开始',
  active: '录制中',
  collecting: '收集中',
  done: '已完成',
  error: '异常',
}

const governanceOptions = [
  { label: '原始录制', value: 'raw' },
  { label: '候选样本', value: 'candidate' },
  { label: '已批准', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已归档', value: 'archived' },
]

const governanceLabelMap: Record<string, string> = {
  raw: '原始录制',
  candidate: '候选样本',
  approved: '已批准',
  rejected: '已拒绝',
  archived: '已归档',
}

const filteredRecordings = computed(() => {
  const keyword = recordingSearch.value.trim().toLowerCase()
  if (!keyword) return recordings.value
  return recordings.value.filter((item) =>
    item.request_uri?.toLowerCase().includes(keyword)
    || item.transaction_code?.toLowerCase().includes(keyword),
  )
})

const recordingColumns: DataTableColumns<RecordingRow> = [
  {
    title: '请求',
    key: 'request_uri',
    render: (row) => h('span', [h('b', { style: 'margin-right:4px' }, row.request_method || 'GET'), row.request_uri]),
  },
  { title: '交易码', key: 'transaction_code', width: 140, render: (row) => row.transaction_code || '-' },
  { title: '治理状态', key: 'governance_status', width: 110, render: (row) => governanceLabelMap[row.governance_status] || row.governance_status },
  { title: '重复', key: 'duplicate_count', width: 70, render: (row) => row.duplicate_count ?? 1 },
  {
    title: '子调用',
    key: 'sub_calls',
    width: 140,
    render: (row) => {
      const summary = buildRecordingSubCallSummary(parseRecordingSubCalls(row.sub_calls))
      return summary === '无细分' ? '-' : summary
    },
  },
  { title: '响应码', key: 'response_status', width: 80 },
  {
    title: '耗时',
    key: 'latency_ms',
    width: 90,
    render: (row) => (row.latency_ms != null ? `${row.latency_ms}ms` : '-'),
  },
  {
    title: '录制时间',
    key: 'recorded_at',
    width: 170,
    render: (row) => formatDateTime(row.recorded_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 260,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/recordings/${row.id}?session_id=${sessionId}`) }, () => '查看详情'),
        ...(canEdit
          ? [
              h(NButton, { size: 'tiny', onClick: () => updateGovernance(row.id, 'candidate') }, () => '标候选'),
              h(NButton, { size: 'tiny', type: 'success', onClick: () => updateGovernance(row.id, 'approved') }, () => '批准'),
              h(NButton, { size: 'tiny', type: 'primary', onClick: () => openConvert(row.id) }, () => '生成用例'),
            ]
          : []),
      ]),
  },
]

async function loadPage() {
  await loadSession()
  await loadRecordings()
}

async function loadSession() {
  try {
    const res = await recordingApi.getSession(sessionId)
    session.value = res.data
    if (res.data.application_id != null) {
      const appRes = await applicationApi.get(res.data.application_id)
      appName.value = appRes.data.name
    } else {
      appName.value = '-'
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载会话详情失败')
  }
}

function stopPolling() {
  if (pollingTimer.value != null) {
    window.clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

function startPolling() {
  if (pollingTimer.value != null) {
    return
  }
  pollingTimer.value = window.setInterval(async () => {
    if (session.value?.status !== 'collecting') {
      stopPolling()
      return
    }
    await loadSession()
    await loadRecordings()
  }, 5000)
}

watch(
  () => session.value?.status,
  (status) => {
    if (status === 'collecting') {
      startPolling()
    } else {
      stopPolling()
    }
  },
  { immediate: true },
)

async function loadRecordings() {
  recordingsLoading.value = true
  try {
    const res = await recordingApi.listRecordings(sessionId, {
      limit: 200,
      search: recordingSearch.value.trim() || undefined,
      transaction_code: recordingTransactionCode.value.trim() || undefined,
      governance_status: recordingGovernanceStatus.value || undefined,
      duplicate_only: duplicateOnly.value || undefined,
    })
    recordings.value = res.data
  } catch (error: any) {
    recordings.value = []
    message.error(error.response?.data?.detail || '加载录制数据失败')
  } finally {
    recordingsLoading.value = false
  }
}

async function updateGovernance(recordingId: number, governanceStatus: string) {
  try {
    await recordingApi.updateRecording(recordingId, { governance_status: governanceStatus })
    message.success('治理状态已更新')
    await loadRecordings()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '更新治理状态失败')
  }
}

async function startSession() {
  starting.value = true
  try {
    await recordingApi.startSession(sessionId)
    message.success('录制已开始')
    await loadSession()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '开始录制失败')
  } finally {
    starting.value = false
  }
}

async function stopSession() {
  stopping.value = true
  try {
    await recordingApi.stopSession(sessionId, {})
    message.success('已停止录制，平台开始收集数据')
    await loadSession()
    await loadRecordings()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '停止录制失败')
  } finally {
    stopping.value = false
  }
}

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
    const ids = filteredRecordings.value.map(r => r.id)
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
  const toGenerate = batchCheckItems.value.filter(i => !i.has_existing).map(i => i.recording_id)
  if (toGenerate.length === 0) {
    message.warning('没有可生成的用例')
    return
  }
  batchGenerating.value = true
  try {
    const res = await testCaseApi.batchFromRecordings({
      recording_ids: toGenerate,
      prefix: batchPrefix.value.trim(),
    })
    showBatchModal.value = false
    const { created } = res.data
    message.success(`批量生成完成，共新增 ${created} 条用例`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量生成失败')
  } finally {
    batchGenerating.value = false
  }
}

function openConvert(recordingId: number) {
  convertingRecordingId.value = recordingId
  convertForm.value = { name: '' }
  showConvertModal.value = true
}

async function doConvert() {
  if (convertingRecordingId.value == null) return
  converting.value = true
  try {
    const res = await testCaseApi.fromRecording({
      recording_id: convertingRecordingId.value,
      name: convertForm.value.name || undefined,
    })
    message.success('已由录制生成测试用例')
    showConvertModal.value = false
    router.push(`/testcases/${res.data.id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '生成测试用例失败')
  } finally {
    converting.value = false
  }
}

onMounted(() => {
  void loadPage()
})

onUnmounted(() => {
  stopPolling()
})
</script>
