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
          v-if="canEdit && selectedRecordingIds.length > 0"
          type="error"
          @click="deleteSelectedRecordings"
        >
          批量删除{{ selectedRecordingIds.length > 0 ? ` (${selectedRecordingIds.length})` : '' }}
        </n-button>
        <n-button
          v-if="canEdit && selectedRecordingIds.length > 0"
          @click="openBatchModal"
        >
          批量生成用例{{ selectedRecordingIds.length > 0 ? ` (${selectedRecordingIds.length})` : '' }}
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
            @update:value="reloadRecordingsFromFirstPage"
          />
          <n-input
            v-model:value="recordingTransactionCode"
            clearable
            placeholder="交易码"
            style="width: 180px"
            @keyup.enter="reloadRecordingsFromFirstPage"
          />
          <n-checkbox v-model:checked="duplicateOnly" @update:checked="reloadRecordingsFromFirstPage">仅重复样本</n-checkbox>
          <n-input
            v-model:value="recordingSearch"
            clearable
            placeholder="搜索路径/交易码"
            style="width: 220px"
          />
          <n-button @click="reloadRecordingsFromFirstPage">查询</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="recordingColumns"
        :data="filteredRecordings"
        :loading="recordingsLoading"
        :pagination="recordingPagination"
        :row-key="(row: RecordingRow) => row.id"
        remote
        v-model:checked-row-keys="selectedRecordingIds"
        @update:sorter="handleRecordingSorterChange"
      />
    </n-card>

    <n-card title="采集审计日志">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="auditEventType"
            clearable
            :options="auditEventOptions"
            placeholder="事件类型"
            style="width: 180px"
            @update:value="reloadAuditLogsFromFirstPage"
          />
          <n-button @click="loadAuditLogs">刷新日志</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="auditColumns"
        :data="auditLogs"
        :loading="auditLoading"
        :pagination="auditPagination"
        remote
        size="small"
      />
    </n-card>
  </n-space>

  <n-modal v-model:show="showAuditDetailModal" title="采集审计详情" preset="card" style="width: 720px">
    <n-space vertical :size="12">
      <n-descriptions bordered :column="2" size="small">
        <n-descriptions-item label="事件">{{ formatAuditEvent(selectedAuditLog?.event_type) }}</n-descriptions-item>
        <n-descriptions-item label="时间">{{ formatDateTime(selectedAuditLog?.created_at) }}</n-descriptions-item>
        <n-descriptions-item label="请求">{{ selectedAuditLog?.request_uri ? `${selectedAuditLog?.request_method || ''} ${selectedAuditLog?.request_uri}`.trim() : '-' }}</n-descriptions-item>
        <n-descriptions-item label="交易码">{{ selectedAuditLog?.transaction_code || '-' }}</n-descriptions-item>
        <n-descriptions-item label="消息" :span="2">{{ selectedAuditLog?.message || '-' }}</n-descriptions-item>
      </n-descriptions>
      <n-card size="small" title="Detail JSON">
        <pre class="code-block compact">{{ prettyText(selectedAuditLog?.detail) }}</pre>
      </n-card>
    </n-space>
  </n-modal>

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
        <span>将对已选 {{ selectedRecordingIds.length }} 条录制生成用例</span>
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
import { computed, h, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
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
import { recordingApi, type RecordingAuditLog } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'
import type { RecordingSubCall } from '@/utils/recording'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData } from '@/utils/pagination'

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
  quality_score?: number | null
  quality_level?: string | null
  quality_recommendation?: string | null
  quality_reasons?: string[]
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
const auditLogs = ref<RecordingAuditLog[]>([])
const auditLoading = ref(false)
const selectedAuditLog = ref<RecordingAuditLog | null>(null)
const showAuditDetailModal = ref(false)
const selectedRecordingIds = ref<(string | number)[]>([])
const recordingSearch = ref('')
const recordingTransactionCode = ref('')
const recordingGovernanceStatus = ref<string | null>(null)
const duplicateOnly = ref(false)
const auditEventType = ref<string | null>(null)
const recordingSort = ref(defaultSortState('recorded_at'))
const recordingPagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
  pageSizes: [12, 24, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条录制`,
  onUpdatePage: (page: number) => {
    recordingPagination.page = page
    void loadRecordings()
  },
  onUpdatePageSize: (pageSize: number) => {
    recordingPagination.pageSize = pageSize
    recordingPagination.page = 1
    void loadRecordings()
  },
})
const auditPagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条日志`,
  onUpdatePage: (page: number) => {
    auditPagination.page = page
    void loadAuditLogs()
  },
  onUpdatePageSize: (pageSize: number) => {
    auditPagination.pageSize = pageSize
    auditPagination.page = 1
    void loadAuditLogs()
  },
})
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

const auditEventOptions = [
  { label: '录制启动', value: 'recording_started' },
  { label: '同步入队', value: 'collection_enqueued' },
  { label: '同步开始', value: 'sync_started' },
  { label: '分页拉取', value: 'page_fetched' },
  { label: '录制入库', value: 'record_saved' },
  { label: '重复跳过', value: 'record_skipped_duplicate' },
  { label: '过滤跳过', value: 'record_skipped_filter' },
  { label: '子调用清理', value: 'sub_invocation_cleanup' },
  { label: '同步完成', value: 'sync_finished' },
  { label: '同步失败', value: 'sync_failed' },
]

const auditEventLabelMap = Object.fromEntries(auditEventOptions.map((item) => [item.value, item.label]))

const governanceLabelMap: Record<string, string> = {
  raw: '原始录制',
  candidate: '候选样本',
  approved: '已批准',
  rejected: '已拒绝',
  archived: '已归档',
}

const qualityLevelTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  good: 'success',
  warning: 'warning',
  bad: 'error',
}

const qualityRecommendationLabelMap: Record<string, string> = {
  approve: '建议批准',
  candidate: '建议候选',
  reject: '建议丢弃',
}

const filteredRecordings = computed(() => {
  const keyword = recordingSearch.value.trim().toLowerCase()
  if (!keyword) return recordings.value
  return recordings.value.filter((item) =>
    item.request_uri?.toLowerCase().includes(keyword)
    || item.transaction_code?.toLowerCase().includes(keyword),
  )
})

const recordingColumns = computed<DataTableColumns<RecordingRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const }] : []),
  {
    title: '请求',
    key: 'request_uri',
    width: 280,
    render: (row) =>
      h('div', { class: 'request-cell' }, [
        h('span', { class: 'request-cell__method' }, row.request_method || 'GET'),
        h('span', { class: 'request-cell__uri' }, row.request_uri),
      ]),
  },
  { title: '交易码', key: 'transaction_code', width: 140, render: (row) => row.transaction_code || '-' },
  { title: '治理状态', key: 'governance_status', width: 110, render: (row) => governanceLabelMap[row.governance_status] || row.governance_status },
  {
    title: '质量',
    key: 'quality_score',
    width: 130,
    render: (row) => h(NSpace, { size: 4, vertical: true }, () => [
      h(NTag, { size: 'small', type: qualityLevelTypeMap[row.quality_level || ''] || 'default' }, () => `${row.quality_score ?? '-'}分`),
      h('span', { class: 'quality-hint' }, qualityRecommendationLabelMap[row.quality_recommendation || ''] || '-'),
    ]),
  },
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
    sorter: true,
    sortOrder: resolveSortOrder(recordingSort.value, 'recorded_at'),
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
              h(NButton, { size: 'tiny', type: 'error', onClick: () => deleteRecording(row.id) }, () => '删除'),
            ]
          : []),
      ]),
  },
])

const auditColumns: DataTableColumns<RecordingAuditLog> = [
  {
    title: '时间',
    key: 'created_at',
    width: 160,
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '事件',
    key: 'event_type',
    width: 160,
    render: (row) => formatAuditEvent(row.event_type),
  },
  {
    title: '请求',
    key: 'request_uri',
    width: 260,
    render: (row) => row.request_uri ? `${row.request_method || ''} ${row.request_uri}`.trim() : '-',
  },
  {
    title: '交易码',
    key: 'transaction_code',
    width: 140,
    render: (row) => row.transaction_code || '-',
  },
  {
    title: '消息',
    key: 'message',
    minWidth: 220,
    render: (row) => row.message || '-',
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => openAuditDetail(row) }, () => '详情'),
        ...(row.recording_id
          ? [
              h(
                NButton,
                { size: 'tiny', type: 'primary', ghost: true, onClick: () => router.push(`/recording/recordings/${row.recording_id}?session_id=${sessionId}`) },
                () => '录制',
              ),
            ]
          : []),
      ]),
  },
]

function prettyText(value?: string | null) {
  if (!value) return '-'
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

function formatAuditEvent(eventType?: string | null) {
  if (!eventType) return '-'
  const label = auditEventLabelMap[eventType]
  return label ? `${label}（${eventType}）` : eventType
}

function openAuditDetail(row: RecordingAuditLog) {
  selectedAuditLog.value = row
  showAuditDetailModal.value = true
}

async function loadPage() {
  await loadSession()
  await loadRecordings()
  await loadAuditLogs()
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

function shouldPollSession(status?: string | null) {
  return status === 'active' || status === 'collecting'
}

function startPolling() {
  if (pollingTimer.value != null) {
    return
  }
  pollingTimer.value = window.setInterval(async () => {
    if (!shouldPollSession(session.value?.status)) {
      stopPolling()
      return
    }
    await loadSession()
    await loadRecordings()
    await loadAuditLogs()
  }, 5000)
}

watch(
  () => session.value?.status,
  (status) => {
    if (shouldPollSession(status)) {
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
    const page = await loadPagedData<RecordingRow>((params) => recordingApi.listRecordings(sessionId, params), {
      search: recordingSearch.value.trim() || undefined,
      transaction_code: recordingTransactionCode.value.trim() || undefined,
      governance_status: recordingGovernanceStatus.value || undefined,
      duplicate_only: duplicateOnly.value || undefined,
      sort_by: recordingSort.value.columnKey,
      sort_order: toApiSortOrder(recordingSort.value.order),
    }, recordingPagination.page, recordingPagination.pageSize, 200)
    recordings.value = page.items
    recordingPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && recordingPagination.page > 1) {
      recordingPagination.page = lastValidPage(page.total, recordingPagination.pageSize)
      void loadRecordings()
      return
    }
    selectedRecordingIds.value = []
  } catch (error: any) {
    recordings.value = []
    recordingPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载录制数据失败')
  } finally {
    recordingsLoading.value = false
  }
}

async function loadAuditLogs() {
  auditLoading.value = true
  try {
    const page = await loadPagedData<RecordingAuditLog>((params) => recordingApi.getSessionAuditLogs(sessionId, params), {
      event_type: auditEventType.value || undefined,
    }, auditPagination.page, auditPagination.pageSize, 500)
    auditLogs.value = page.items
    auditPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && auditPagination.page > 1) {
      auditPagination.page = lastValidPage(page.total, auditPagination.pageSize)
      void loadAuditLogs()
      return
    }
  } catch (error: any) {
    auditLogs.value = []
    auditPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载采集审计日志失败')
  } finally {
    auditLoading.value = false
  }
}

function reloadRecordingsFromFirstPage() {
  recordingPagination.page = 1
  void loadRecordings()
}

function reloadAuditLogsFromFirstPage() {
  auditPagination.page = 1
  void loadAuditLogs()
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

async function deleteRecording(recordingId: number) {
  try {
    await recordingApi.deleteRecording(recordingId)
    message.success('录制已删除')
    await loadRecordings()
    await loadSession()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}

async function deleteSelectedRecordings() {
  if (selectedRecordingIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteRecordings({ ids: selectedRecordingIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 条录制`)
    await loadRecordings()
    await loadSession()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
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
    selectedRecordingIds.value = []
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

function handleRecordingSorterChange(sorter: any) {
  recordingSort.value = updateSortState(sorter, 'recorded_at')
  recordingPagination.page = 1
  void loadRecordings()
}

onMounted(() => {
  void loadPage()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.code-block {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 320px;
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  background: #f8f8f8;
  font-family: monospace;
  font-size: 12px;
}
.code-block.compact {
  max-height: 240px;
}
.request-cell {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  min-width: 0;
}

.request-cell__method {
  flex: none;
  font-weight: 700;
  white-space: nowrap;
}

.request-cell__uri {
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.quality-hint {
  font-size: 12px;
  color: #888;
  line-height: 1.2;
}
</style>
