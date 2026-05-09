import { computed, h, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NPopconfirm, NSpace, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns, DataTableSortState, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { formatDateTime } from '@/utils/format'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData } from '@/utils/pagination'
import { extractError } from '@/utils/error'
import type { RecordingGroupRow, RecordingRow, SessionRow } from './types'

export function useRecordingPage() {
const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'

const sessions = ref<SessionRow[]>([])
const sessionsLoading = ref(false)
const filterApplicationId = ref<number | null>(null)
const filterStatus = ref<string | null>(null)
const filterDateRange = ref<[number, number] | null>(null)
const sessionSearch = ref('')
const appOptions = ref<SelectOption[]>([])
const appNameMap = ref<Record<number, string>>({})

const showSessionModal = ref(false)
const creatingSession = ref(false)
const sessionForm = ref({
  name: '',
  application_id: null as number | null,
  recording_filter_prefixes_text: '',
})

const showRecordingDrawer = ref(false)
const selectedSession = ref<SessionRow | null>(null)
const recordings = ref<RecordingRow[]>([])
const recordingsLoading = ref(false)
const recordingSearch = ref('')
const selectedSessionRecordingIds = ref<(string | number)[]>([])
const recordingGroups = ref<RecordingGroupRow[]>([])
const groupsLoading = ref(false)
const groupGovernanceStatus = ref<string | null>(null)
const groupSearch = ref('')
const selectedSessionIds = ref<(string | number)[]>([])
const selectedGroupRecordingIds = ref<(string | number)[]>([])
const sessionSort = ref(defaultSortState('created_at'))
const recordingSort = ref(defaultSortState('recorded_at'))
const groupSort = ref(defaultSortState('latest_recorded_at'))
const sessionCountPollingTimer = ref<number | null>(null)
const sessionPagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条`,
  onUpdatePage: (page: number) => {
    sessionPagination.page = page
    void loadSessions()
  },
  onUpdatePageSize: (pageSize: number) => {
    sessionPagination.pageSize = pageSize
    sessionPagination.page = 1
    void loadSessions()
  },
})
const groupPagination = reactive({
  page: 1,
  pageSize: 8,
  itemCount: 0,
  pageSizes: [8, 16, 32, 64],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 组`,
  onUpdatePage: (page: number) => {
    groupPagination.page = page
    void loadRecordingGroups()
  },
  onUpdatePageSize: (pageSize: number) => {
    groupPagination.pageSize = pageSize
    groupPagination.page = 1
    void loadRecordingGroups()
  },
})
const recordingPagination = reactive({
  page: 1,
  pageSize: 15,
  itemCount: 0,
  pageSizes: [15, 30, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条录制`,
  onUpdatePage: (page: number) => {
    recordingPagination.page = page
    void reloadCurrentRecordings()
  },
  onUpdatePageSize: (pageSize: number) => {
    recordingPagination.pageSize = pageSize
    recordingPagination.page = 1
    void reloadCurrentRecordings()
  },
})

const showConvertModal = ref(false)
// 批量生成用例
const batchSource = ref<'groups' | 'recordings'>('groups')
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
const convertingRecordingId = ref<number | null>(null)
const converting = ref(false)
const convertForm = ref({ name: '' })

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

const statusOptions: SelectOption[] = [
  { label: '待开始', value: 'idle' },
  { label: '录制中', value: 'active' },
  { label: '收集中', value: 'collecting' },
  { label: '已完成', value: 'done' },
  { label: '异常', value: 'error' },
]

const governanceOptions: SelectOption[] = [
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

const filteredSessions = computed(() => {
  return sessions.value
})

const filteredRecordings = computed(() => {
  const keyword = recordingSearch.value.trim().toLowerCase()
  if (!keyword) {
    return recordings.value
  }
  return recordings.value.filter((recording) =>
    recording.request_uri?.toLowerCase().includes(keyword)
    || recording.transaction_code?.toLowerCase().includes(keyword),
  )
})

const sessionColumns = computed<DataTableColumns<SessionRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const, disabled: (row: SessionRow) => row.status === 'active' || row.status === 'collecting' }] : []),
  {
    title: '#',
    key: 'seq',
    width: 55,
    render: (_row: SessionRow, index: number) => (sessionPagination.page - 1) * sessionPagination.pageSize + index + 1,
  },
  {
    title: '会话名称',
    key: 'name',
    ellipsis: { tooltip: true },
    render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => router.push(`/recording/sessions/${row.id}`) }, () => row.name),
  },
  {
    title: '所属应用',
    key: 'application_id',
    render: (row) => appNameMap.value[row.application_id] || `#${row.application_id}`,
  },
  {
    title: '交易码过滤',
    key: 'recording_filter_prefixes',
    width: 180,
    render: (row) => formatPrefixSummary(row.recording_filter_prefixes),
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(
      NTag,
      {
        type: sessionStatusTagType[row.status] ?? 'default',
        size: 'small',
        title: row.status === 'error' ? (row.error_message || '同步失败') : undefined,
      },
      () => sessionStatusLabelMap[row.status] || row.status,
    ),
  },
  { title: '录制数', key: 'total_count', width: 100 },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    sorter: true,
    sortOrder: resolveSortOrder(sessionSort.value, 'created_at'),
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/sessions/${row.id}`) }, () => '会话详情'),
        ...(canEdit && row.status === 'idle'
          ? [h(NButton, { size: 'tiny', type: 'primary', onClick: () => startSession(row.id) }, () => '开始录制')]
          : []),
        ...(canEdit && row.status === 'active'
          ? [h(NButton, { size: 'tiny', type: 'warning', onClick: () => stopSession(row.id) }, () => '停止录制')]
          : []),
        h(NButton, { size: 'tiny', onClick: () => viewRecordings(row) }, () => '查看录制'),
        ...(canEdit && row.status !== 'active' && row.status !== 'collecting' ? [
          h(NPopconfirm, { onPositiveClick: () => deleteSession(row.id) }, {
            default: () => '确认删除该会话及其所有录制数据？',
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
          }),
        ] : []),
      ]),
  },
])

const recordingColumns = computed<DataTableColumns<RecordingRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const }] : []),
  {
    title: '请求信息',
    key: 'request_uri',
    render: (row) =>
      h('span', [
        h('b', row.request_method || 'GET'),
        ' ',
        row.request_uri,
      ]),
  },
  { title: '交易码', key: 'transaction_code', width: 140, render: (row) => row.transaction_code || '-' },
  { title: '治理状态', key: 'governance_status', width: 100, render: (row) => governanceLabelMap[row.governance_status] || row.governance_status || '-' },
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
    width: 250,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/recordings/${row.id}`) }, () => '详情'),
        ...(canEdit ? [
          h(NButton, { size: 'tiny', onClick: () => quickGovernance(row.id, 'candidate') }, () => '标候选'),
          h(NButton, { size: 'tiny', type: 'primary', onClick: () => openConvert(row.id) }, () => '生成用例'),
          h(NPopconfirm, { onPositiveClick: () => deleteRecording(row.id) }, {
            default: () => '确认删除该录制?',
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
          }),
        ] : []),
      ]),
  },
])

const groupColumns = computed<DataTableColumns<RecordingGroupRow>>(() => [
  { type: 'selection' as const },
  {
    title: '交易码 / 场景',
    key: 'transaction_code',
    render: (row) => h('div', [
      h('div', [h('b', row.transaction_code || '未识别交易码')]),
      h('div', { style: 'color:#666;font-size:12px' }, row.scene_key || '-'),
    ]),
  },
  {
    title: '代表样本',
    key: 'representative_recording_id',
    render: (row) => h('span', [h('b', { style: 'margin-right:4px' }, row.representative_request_method), row.representative_request_uri]),
  },
  { title: '总数', key: 'total_count', width: 70 },
  { title: '已批准', key: 'approved_count', width: 80 },
  { title: '候选', key: 'candidate_count', width: 70 },
  { title: '原始', key: 'raw_count', width: 70 },
  {
    title: '最新录制',
    key: 'latest_recorded_at',
    width: 170,
    sorter: true,
    sortOrder: resolveSortOrder(groupSort.value, 'latest_recorded_at'),
    render: (row) => formatDateTime(row.latest_recorded_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    render: (row) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/recordings/${row.representative_recording_id}`) }, () => '代表样本'),
      ...(canEdit ? [
        h(NButton, { size: 'tiny', type: 'success', onClick: () => quickGovernance(row.representative_recording_id, 'approved', true) }, () => '批准代表'),
        h(NButton, { size: 'tiny', onClick: () => openConvert(row.representative_recording_id) }, () => '生成用例'),
        h(NPopconfirm, { onPositiveClick: () => deleteRecording(row.representative_recording_id, true) }, {
          default: () => '确认删除代表样本?',
          trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除代表'),
        }),
      ] : []),
    ]),
  },
])

function rangeStartIso(value: number) {
  return new Date(value).toISOString()
}

function rangeEndIso(value: number) {
  return new Date(value + 86_399_999).toISOString()
}

async function loadApps() {
  try {
    const res = await applicationApi.list({ limit: 100 })
    appOptions.value = res.data.map((app: { id: number; name: string }) => ({
      label: app.name,
      value: app.id,
    }))
    appNameMap.value = Object.fromEntries(res.data.map((app: { id: number; name: string }) => [app.id, app.name]))
  } catch (error: unknown) {
    appOptions.value = []
    appNameMap.value = {}
    message.error(extractError(error, 'Load application list failed'))
  }
}

async function loadSessions(options: { silent?: boolean } = {}) {
  if (!options.silent) {
    sessionsLoading.value = true
  }
  try {
    const params: Record<string, number | string | boolean> = {}
    if (filterApplicationId.value != null) {
      params.application_id = filterApplicationId.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (sessionSearch.value.trim()) {
      params.search = sessionSearch.value.trim()
    }
    if (filterDateRange.value) {
      params.created_after = rangeStartIso(filterDateRange.value[0])
      params.created_before = rangeEndIso(filterDateRange.value[1])
    }
    params.sort_by = sessionSort.value.columnKey
    params.sort_order = toApiSortOrder(sessionSort.value.order)
    params.refresh_active_count = true
    const page = await loadPagedData<SessionRow>(recordingApi.listSessions, params, sessionPagination.page, sessionPagination.pageSize, 100)
    sessions.value = page.items
    sessionPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && sessionPagination.page > 1) {
      sessionPagination.page = lastValidPage(page.total, sessionPagination.pageSize)
      void loadSessions()
      return
    }
    selectedSessionIds.value = []
    updateSessionCountPolling()
  } catch (error: unknown) {
    sessions.value = []
    sessionPagination.itemCount = 0
    updateSessionCountPolling()
    if (!options.silent) {
      message.error(extractError(error, 'Load recording sessions failed'))
    }
  } finally {
    if (!options.silent) {
      sessionsLoading.value = false
    }
  }
}

function reloadSessionsFromFirstPage() {
  sessionPagination.page = 1
  void loadSessions()
}

function shouldPollSessionList() {
  return sessions.value.some((session) => session.status === 'active' || session.status === 'collecting')
}

function startSessionCountPolling() {
  if (sessionCountPollingTimer.value != null) {
    return
  }
  sessionCountPollingTimer.value = window.setInterval(() => {
    void loadSessions({ silent: true })
  }, 10_000)
}

function stopSessionCountPolling() {
  if (sessionCountPollingTimer.value == null) {
    return
  }
  window.clearInterval(sessionCountPollingTimer.value)
  sessionCountPollingTimer.value = null
}

function updateSessionCountPolling() {
  if (shouldPollSessionList()) {
    startSessionCountPolling()
  } else {
    stopSessionCountPolling()
  }
}

async function loadRecordingGroups() {
  groupsLoading.value = true
  try {
    const page = await loadPagedData<RecordingGroupRow>(recordingApi.listRecordingGroups, {
      application_id: filterApplicationId.value ?? undefined,
      governance_status: groupGovernanceStatus.value || undefined,
      search: groupSearch.value.trim() || undefined,
      sort_by: groupSort.value.columnKey,
      sort_order: toApiSortOrder(groupSort.value.order),
    }, groupPagination.page, groupPagination.pageSize, 200)
    recordingGroups.value = page.items
    groupPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && groupPagination.page > 1) {
      groupPagination.page = lastValidPage(page.total, groupPagination.pageSize)
      void loadRecordingGroups()
      return
    }
    selectedGroupRecordingIds.value = []
  } catch (error: unknown) {
    recordingGroups.value = []
    groupPagination.itemCount = 0
    message.error(extractError(error, 'Load recording groups failed'))
  } finally {
    groupsLoading.value = false
  }
}

function reloadRecordingGroupsFromFirstPage() {
  groupPagination.page = 1
  void loadRecordingGroups()
}

function handleApplicationFilterChange() {
  sessionPagination.page = 1
  groupPagination.page = 1
  void Promise.all([loadSessions(), loadRecordingGroups()])
}

function resetFilters() {
  filterApplicationId.value = null
  filterStatus.value = null
  filterDateRange.value = null
  sessionSearch.value = ''
  groupGovernanceStatus.value = null
  groupSearch.value = ''
  sessionPagination.page = 1
  groupPagination.page = 1
  void Promise.all([loadSessions(), loadRecordingGroups()])
}

function openCreateSession() {
  sessionForm.value = {
    name: '',
    application_id: null,
    recording_filter_prefixes_text: '',
  }
  showSessionModal.value = true
}

function parsePrefixList(raw: string): string[] {
  const text = raw.trim()
  if (!text) {
    return []
  }

  const hasStructuredSeparator = /[\n;；]/.test(text)
  if (hasStructuredSeparator) {
    return text
      .split(/[\n;；]+/)
      .map((item) => item.trim())
      .filter(Boolean)
  }

  if (/^(?:re:|regex:|=|\/).*/i.test(text)) {
    return [text]
  }

  return text
    .split(/[，,]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function formatPrefixSummary(prefixes?: string[] | null) {
  if (!prefixes || prefixes.length === 0) {
    return '-'
  }
  return prefixes.join(', ')
}

async function createSession() {
  if (sessionForm.value.application_id == null) {
    message.warning('请先选择应用')
    return
  }

  creatingSession.value = true
  try {
    const prefixes = parsePrefixList(sessionForm.value.recording_filter_prefixes_text)
    await recordingApi.createSession({
      application_id: sessionForm.value.application_id,
      name: sessionForm.value.name,
      recording_filter_prefixes: prefixes.length > 0 ? prefixes : undefined,
    })
    message.success('录制会话创建成功')
    showSessionModal.value = false
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Create recording session failed'))
  } finally {
    creatingSession.value = false
  }
}

async function startSession(sessionId: number) {
  try {
    await recordingApi.startSession(sessionId)
    message.success('录制已开始')
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Start recording failed'))
  }
}

async function stopSession(sessionId: number) {
  try {
    await recordingApi.stopSession(sessionId, {})
    message.success('已停止录制，平台开始收集数据')
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Stop recording failed'))
  }
}

async function deleteSession(sessionId: number) {
  try {
    await recordingApi.deleteSession(sessionId)
    message.success('会话已删除')
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Delete session failed'))
  }
}

async function deleteSelectedSessions() {
  if (selectedSessionIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteSessions({ ids: selectedSessionIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 个会话`)
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Bulk delete sessions failed'))
  }
}

async function viewRecordings(session: SessionRow) {
  selectedSession.value = session
  showRecordingDrawer.value = true
  recordingsLoading.value = true
  recordingSearch.value = ''
  recordingPagination.page = 1
  selectedSessionRecordingIds.value = []
  try {
    const page = await loadPagedData<RecordingRow>((requestParams) => recordingApi.listRecordings(session.id, requestParams), {
      sort_by: recordingSort.value.columnKey,
      sort_order: toApiSortOrder(recordingSort.value.order),
      search: recordingSearch.value.trim() || undefined,
    }, recordingPagination.page, recordingPagination.pageSize, 200)
    recordings.value = page.items
    recordingPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && recordingPagination.page > 1) {
      recordingPagination.page = lastValidPage(page.total, recordingPagination.pageSize)
      void reloadCurrentRecordings()
      return
    }
  } catch (error: unknown) {
    recordings.value = []
    recordingPagination.itemCount = 0
    message.error(extractError(error, 'Load recordings failed'))
  } finally {
    recordingsLoading.value = false
  }
}

async function reloadCurrentRecordings() {
  if (!selectedSession.value) return
  recordingsLoading.value = true
  selectedSessionRecordingIds.value = []
  try {
    const page = await loadPagedData<RecordingRow>((requestParams) => recordingApi.listRecordings(selectedSession.value!.id, requestParams), {
      sort_by: recordingSort.value.columnKey,
      sort_order: toApiSortOrder(recordingSort.value.order),
      search: recordingSearch.value.trim() || undefined,
    }, recordingPagination.page, recordingPagination.pageSize, 200)
    recordings.value = page.items
    recordingPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && recordingPagination.page > 1) {
      recordingPagination.page = lastValidPage(page.total, recordingPagination.pageSize)
      void reloadCurrentRecordings()
    }
  } catch (error: unknown) {
    recordings.value = []
    recordingPagination.itemCount = 0
    message.error(extractError(error, 'Load recordings failed'))
  } finally {
    recordingsLoading.value = false
  }
}

function reloadCurrentRecordingsFromFirstPage() {
  recordingPagination.page = 1
  void reloadCurrentRecordings()
}

async function quickGovernance(recordingId: number, governanceStatus: string, refreshGroups = false) {
  try {
    await recordingApi.updateRecording(recordingId, { governance_status: governanceStatus })
    message.success('治理状态已更新')
    if (selectedSession.value) {
      await viewRecordings(selectedSession.value)
    }
    if (refreshGroups) {
      await loadRecordingGroups()
    }
  } catch (error: unknown) {
    message.error(extractError(error, 'Update governance status failed'))
  }
}

function openConvert(recordingId: number) {
  convertingRecordingId.value = recordingId
  convertForm.value = { name: '' }
  showConvertModal.value = true
}

async function doConvert() {
  if (convertingRecordingId.value == null) {
    return
  }

  converting.value = true
  try {
    await testCaseApi.fromRecording({
      recording_id: convertingRecordingId.value,
      name: convertForm.value.name || undefined,
    })
    message.success('已由录制生成测试用例')
    showConvertModal.value = false
  } catch (error: unknown) {
    message.error(extractError(error, 'Generate test case failed'))
  } finally {
    converting.value = false
  }
}

function openBatchModal(source: 'groups' | 'recordings') {
  batchSource.value = source
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
    const ids = (batchSource.value === 'groups' ? selectedGroupRecordingIds.value : selectedSessionRecordingIds.value).map(Number)
    const res = await testCaseApi.batchCheck({ recording_ids: ids })
    batchCheckItems.value = res.data
    batchStep.value = 'check'
  } catch (error: unknown) {
    message.error(extractError(error, 'Check conflicts failed'))
  } finally {
    batchChecking.value = false
  }
}

async function doBatchGenerate() {
  const toGenerate = batchCheckItems.value
    .filter(i => !i.has_existing)
    .map(i => i.recording_id)
  if (toGenerate.length === 0) {
    message.warning('没有可生成的用例')
    return
  }
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
    if (batchSource.value === 'groups') {
      selectedGroupRecordingIds.value = []
    } else {
      selectedSessionRecordingIds.value = []
    }
  } catch (error: unknown) {
    message.error(extractError(error, 'Batch generate failed'))
  } finally {
    batchGenerating.value = false
  }
}

async function deleteRecording(recordingId: number, refreshGroups = false) {
  try {
    await recordingApi.deleteRecording(recordingId)
    message.success('录制已删除')
    if (selectedSession.value) {
      await reloadCurrentRecordings()
    }
    if (refreshGroups) {
      await loadRecordingGroups()
    }
  } catch (error: unknown) {
    message.error(extractError(error, 'Delete recording failed'))
  }
}

async function deleteSelectedSessionRecordings() {
  if (selectedSessionRecordingIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteRecordings({ ids: selectedSessionRecordingIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 条录制`)
    selectedSessionRecordingIds.value = []
    await Promise.all([reloadCurrentRecordings(), loadRecordingGroups()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Bulk delete recordings failed'))
  }
}

async function deleteSelectedGroupRecordings() {
  if (selectedGroupRecordingIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteRecordings({ ids: selectedGroupRecordingIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 条代表样本`)
    selectedGroupRecordingIds.value = []
    await Promise.all([loadRecordingGroups(), reloadCurrentRecordings()])
  } catch (error: unknown) {
    message.error(extractError(error, 'Bulk delete recordings failed'))
  }
}

function handleSessionSorterChange(sorter: DataTableSortState | null) {
  sessionSort.value = updateSortState(sorter, 'created_at')
  sessionPagination.page = 1
  void loadSessions()
}

function handleRecordingSorterChange(sorter: DataTableSortState | null) {
  recordingSort.value = updateSortState(sorter, 'recorded_at')
  recordingPagination.page = 1
  void reloadCurrentRecordings()
}

function handleGroupSorterChange(sorter: DataTableSortState | null) {
  groupSort.value = updateSortState(sorter, 'latest_recorded_at')
  groupPagination.page = 1
  void loadRecordingGroups()
}

onMounted(async () => {
  const queryAppId = typeof route.query.application_id === 'string' ? Number(route.query.application_id) : null
  if (queryAppId != null && !Number.isNaN(queryAppId)) {
    filterApplicationId.value = queryAppId
  }
  if (typeof route.query.status === 'string' && route.query.status) {
    filterStatus.value = route.query.status
  }
  if (typeof route.query.search === 'string' && route.query.search) {
    sessionSearch.value = route.query.search
  }
  await Promise.all([loadApps(), loadSessions(), loadRecordingGroups()])
})

onBeforeUnmount(() => {
  stopSessionCountPolling()
})

  return {
    router,
    canEdit,
    sessions,
    sessionsLoading,
    filterApplicationId,
    filterStatus,
    filterDateRange,
    sessionSearch,
    appOptions,
    appNameMap,
    showSessionModal,
    creatingSession,
    sessionForm,
    showRecordingDrawer,
    selectedSession,
    recordings,
    recordingsLoading,
    recordingSearch,
    selectedSessionRecordingIds,
    recordingGroups,
    groupsLoading,
    groupGovernanceStatus,
    groupSearch,
    selectedSessionIds,
    selectedGroupRecordingIds,
    sessionSort,
    recordingSort,
    groupSort,
    sessionPagination,
    groupPagination,
    recordingPagination,
    showConvertModal,
    batchSource,
    showBatchModal,
    batchStep,
    batchPrefix,
    batchChecking,
    batchCheckItems,
    batchGenerating,
    showBatchResultModal,
    batchResult,
    convertingRecordingId,
    converting,
    convertForm,
    sessionStatusTagType,
    sessionStatusLabelMap,
    statusOptions,
    governanceOptions,
    governanceLabelMap,
    qualityLevelTypeMap,
    qualityRecommendationLabelMap,
    filteredSessions,
    filteredRecordings,
    sessionColumns,
    recordingColumns,
    groupColumns,
    rangeStartIso,
    rangeEndIso,
    loadApps,
    loadSessions,
    reloadSessionsFromFirstPage,
    loadRecordingGroups,
    reloadRecordingGroupsFromFirstPage,
    handleApplicationFilterChange,
    resetFilters,
    openCreateSession,
    parsePrefixList,
    formatPrefixSummary,
    createSession,
    startSession,
    stopSession,
    deleteSession,
    deleteSelectedSessions,
    viewRecordings,
    reloadCurrentRecordings,
    reloadCurrentRecordingsFromFirstPage,
    quickGovernance,
    openConvert,
    doConvert,
    openBatchModal,
    doBatchCheck,
    doBatchGenerate,
    deleteRecording,
    deleteSelectedSessionRecordings,
    deleteSelectedGroupRecordings,
    handleSessionSorterChange,
    handleRecordingSorterChange,
    handleGroupSorterChange
  }
}
