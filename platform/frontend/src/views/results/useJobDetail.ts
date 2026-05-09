import { computed, h, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NSpace, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi, type ReplayAuditLog, type SubCallDiffResult } from '@/api/replays'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'
import { lastValidPage, loadPagedData } from '@/utils/pagination'
import { extractError } from '@/utils/error'
import type {
  ReplayAnalysisData,
  ReplayJobRow,
  ReplayResultRow,
  RuleSuggestion,
  SourceRecording,
  SourceTestCase,
} from './types'

export function useJobDetail() {
const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const jobId = Number(route.params.jobId)

const job = ref<ReplayJobRow | null>(null)
const appName = ref('-')
const results = ref<ReplayResultRow[]>([])
const resultsLoading = ref(false)
const auditLogs = ref<ReplayAuditLog[]>([])
const auditLoading = ref(false)
const auditEventType = ref<string | null>(null)
const selectedAuditLog = ref<ReplayAuditLog | null>(null)
const showAuditDetail = ref(false)
const resultFilter = ref<string | null>(null)
const showDiff = ref(false)
const selectedResult = ref<ReplayResultRow | null>(null)
const analysisLoading = ref(false)
const analysisData = ref<ReplayAnalysisData | null>(null)
const sourceTestCase = ref<SourceTestCase | null>(null)
const sourceRecording = ref<SourceRecording | null>(null)
const sourceRecordingSubCallSummary = ref('')
const subCallDiff = ref<SubCallDiffResult | null>(null)
const subCallDiffLoading = ref(false)
const ruleSuggestions = ref<RuleSuggestion[]>([])
const applyingSuggestionKey = ref('')
const resultPagination = reactive({
  page: 1,
  pageSize: 15,
  itemCount: 0,
  pageSizes: [15, 30, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条结果`,
  onUpdatePage: (page: number) => {
    resultPagination.page = page
    void loadResults()
  },
  onUpdatePageSize: (pageSize: number) => {
    resultPagination.pageSize = pageSize
    resultPagination.page = 1
    void loadResults()
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

const passRate = computed(() => {
  if (!job.value || !job.value.total) return 0
  return (job.value.passed / job.value.total) * 100
})

const parsedAssertionResults = computed(() => {
  const raw = selectedResult.value?.assertion_results
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
})

const analysisCategoryDefs = [
  { key: 'ENVIRONMENT', label: '环境问题', icon: '🌐', color: '#f0a020' },
  { key: 'DATA_ISSUE',  label: '数据问题', icon: '📝', color: '#2080f0' },
  { key: 'BUG',         label: '代码缺陷', icon: '🐛', color: '#d03050' },
  { key: 'PERFORMANCE', label: '性能问题', icon: '⚡', color: '#8a2be2' },
  { key: 'UNKNOWN',     label: '未知',     icon: '❓', color: '#999'    },
]

const analysisCategories = computed(() => {
  const cats = analysisData.value?.categories || {}
  return analysisCategoryDefs.map((def) => ({
    ...def,
    count: cats[def.key]?.count || 0,
    percentage: cats[def.key]?.percentage || 0,
  }))
})

const jobStatusTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  DONE: 'success', RUNNING: 'info', FAILED: 'error', PENDING: 'default', CANCELLED: 'warning',
}
const jobStatusLabelMap: Record<string, string> = {
  DONE: '已完成', RUNNING: '运行中', FAILED: '存在失败', PENDING: '待执行', CANCELLED: '已取消',
}
const resultStatusTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  PASS: 'success', FAIL: 'error', ERROR: 'warning', TIMEOUT: 'warning', PENDING: 'default',
}
const resultStatusLabelMap: Record<string, string> = {
  PASS: '通过', FAIL: '失败', ERROR: '异常', TIMEOUT: '超时', PENDING: '待执行',
}

const failureCategoryLabelMap: Record<string, string> = {
  status_mismatch: '状态码不一致',
  response_diff: '响应内容差异',
  assertion_failed: '断言失败',
  performance: '性能超限',
  timeout: '请求超时',
  connection_error: '连接异常',
  mock_error: 'Mock 异常',
}

const resultFilterOptions: SelectOption[] = [
  { label: '通过', value: 'PASS' },
  { label: '失败', value: 'FAIL' },
  { label: '异常', value: 'ERROR' },
  { label: '超时', value: 'TIMEOUT' },
]

const auditEventOptions: SelectOption[] = [
  { label: '任务开始', value: 'job_started' },
  { label: '任务结束', value: 'job_finished' },
  { label: '用例开始', value: 'case_started' },
  { label: '请求发出', value: 'request_sent' },
  { label: '响应收到', value: 'response_received' },
  { label: 'Mock 加载', value: 'mock_loaded' },
  { label: 'Mock 移除', value: 'mock_removed' },
  { label: '子调用抓取', value: 'sub_calls_captured' },
  { label: '用例重试', value: 'case_retry' },
  { label: '用例结束', value: 'case_finished' },
]

function diffScoreColor(score?: number | null) {
  if (score == null) return '#999'
  if (score <= 0.1) return '#18a058'
  if (score <= 0.5) return '#f0a020'
  return '#d03050'
}

const resultColumns: DataTableColumns<ReplayResultRow> = [
  {
    title: '接口',
    key: 'request_uri',
    render: (row) =>
      h('div', { style: 'line-height:1.6' }, [
        h('div', [
          h('b', { style: 'margin-right:4px;color:#666' }, row.request_method || 'GET'),
          h('span', row.request_uri || '-'),
        ]),
        row.transaction_code
          ? h('div', {
              style: 'display:inline-block;background:#e8f0fe;color:#1a73e8;border-radius:4px;padding:1px 7px;font-size:12px;margin-top:2px;font-weight:500',
            }, row.transaction_code)
          : null,
      ]),
  },
  {
    title: '来源录制',
    key: 'source_recording_id',
    width: 170,
    render: (row) => {
      if (!row.source_recording_id) return h('span', { style: 'color:#ccc' }, '-')
      return h(NSpace, { size: 6, align: 'center' }, () => [
        h(NTag, { type: row.use_sub_invocation_mocks ? 'success' : 'default', size: 'small' }, () => row.use_sub_invocation_mocks ? 'Mock 开启' : 'Mock 关闭'),
        h('span', `#${row.source_recording_id}${row.source_recording_sub_call_count != null ? ` / 子调用 ${row.source_recording_sub_call_count}` : ''}`),
      ])
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render: (row) =>
      h(NTag, { type: resultStatusTypeMap[row.status] ?? 'default', size: 'small' },
        () => resultStatusLabelMap[row.status] || row.status),
  },
  {
    title: '失败分类',
    key: 'failure_category',
    width: 120,
    render: (row) => {
      if (!row.failure_category) return h('span', { style: 'color:#ccc' }, '-')
      return h('span', failureCategoryLabelMap[row.failure_category] || row.failure_category)
    },
  },
  {
    title: 'Diff Score',
    key: 'diff_score',
    width: 100,
    render: (row) => {
      if (row.diff_score == null) return h('span', { style: 'color:#ccc' }, '-')
      return h('span', { style: `color:${diffScoreColor(row.diff_score)};font-weight:bold` },
        row.diff_score.toFixed(3))
    },
  },
  {
    title: '状态码',
    key: 'actual_status_code',
    width: 80,
    render: (row) => h('span', row.actual_status_code?.toString() || '-'),
  },
  {
    title: '耗时',
    key: 'latency_ms',
    width: 80,
    render: (row) => h('span', row.latency_ms != null ? `${row.latency_ms}ms` : '-'),
  },
  {
    title: '时间',
    key: 'created_at',
    width: 145,
    render: (row) => h('span', { style: 'font-size:12px;color:#999' }, formatDateTime(row.created_at)),
  },
  {
    title: '对比',
    key: 'actions',
    width: 70,
    render: (row) =>
      h(NButton, { size: 'tiny', type: 'primary', ghost: true, onClick: () => openDiff(row) }, () => '对比'),
  },
]

const auditColumns: DataTableColumns<ReplayAuditLog> = [
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
  },
  {
    title: '接口',
    key: 'request_uri',
    width: 260,
    render: (row) => row.request_uri ? `${row.request_method || ''} ${row.request_uri}`.trim() : (row.target_url || '-'),
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
    width: 160,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => openAuditDetail(row) }, () => '详情'),
        ...(row.result_id
          ? [
              h(
                NButton,
                { size: 'tiny', type: 'primary', ghost: true, onClick: () => openAuditResult(row) },
                () => '结果',
              ),
            ]
          : []),
      ]),
  },
]

function prettyText(value?: string | null) {
  if (!value) return '-'
  try { return JSON.stringify(JSON.parse(value), null, 2) } catch { return value }
}

function openAuditDetail(row: ReplayAuditLog) {
  selectedAuditLog.value = row
  showAuditDetail.value = true
}

async function openAuditResult(row: ReplayAuditLog) {
  if (!row.result_id) return
  const existing = results.value.find(item => item.id === row.result_id)
  if (existing) {
    openDiff(existing)
    return
  }
  try {
    const res = await replayApi.getResult(row.result_id)
    openDiff(res.data)
  } catch (error: unknown) {
    message.error(extractError(error, 'Open replay result detail failed'))
  }
}

function rawText(value?: string | null) {
  return value || '-'
}

/** 从失败原因中提取差异字段列表；格式："...差异字段 a, b, c" */
function failureReasonFields(reason?: string | null): string[] | null {
  if (!reason) return null
  const match = reason.match(/差异字段\s+(.+)$/)
  if (!match) return null
  return match[1].split(',').map(s => s.trim()).filter(Boolean)
}

function failureReasonPrefix(reason: string): string {
  return reason.replace(/差异字段.+$/, '').trim().replace(/:$/, '').trim()
}

function openDiff(row: ReplayResultRow) {
  selectedResult.value = row
  showDiff.value = true
  void loadSourceRecording(row)
  void loadSubCallDiff(row.id)
  void loadRuleSuggestions(row.id)
}

async function loadRuleSuggestions(resultId: number) {
  ruleSuggestions.value = []
  try {
    const res = await replayApi.getRuleSuggestions(resultId)
    ruleSuggestions.value = res.data?.suggestions || []
  } catch {
    ruleSuggestions.value = []
  }
}

async function applyRuleSuggestion(
  suggestionKey: string,
  target: 'job_ignore_fields' | 'application_default_ignore_fields',
) {
  if (!selectedResult.value) return
  applyingSuggestionKey.value = `${suggestionKey}:${target}`
  try {
    await replayApi.applyRuleSuggestion(selectedResult.value.id, { suggestion_key: suggestionKey, target })
    message.success(target === 'job_ignore_fields' ? '已加入本次回放任务忽略字段' : '已加入应用默认忽略字段')
    await loadRuleSuggestions(selectedResult.value.id)
  } catch (error: unknown) {
    message.error(extractError(error, 'Load replay result detail failed'))
  } finally {
    applyingSuggestionKey.value = ''
  }
}

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

async function loadSourceRecording(row: ReplayResultRow) {
  sourceTestCase.value = null
  sourceRecording.value = null
  sourceRecordingSubCallSummary.value = ''

  if (!row.test_case_id) {
    return
  }

  try {
    const caseRes = await testCaseApi.get(row.test_case_id)
    sourceTestCase.value = caseRes.data
    if (caseRes.data.source_recording_id) {
      const recordingRes = await recordingApi.getRecording(caseRes.data.source_recording_id)
      sourceRecording.value = recordingRes.data
      sourceRecordingSubCallSummary.value = buildRecordingSubCallSummary(
        parseRecordingSubCalls(recordingRes.data.sub_calls),
      )
    }
  } catch {
    sourceTestCase.value = null
    sourceRecording.value = null
    sourceRecordingSubCallSummary.value = ''
  }
}

async function openReport() {
  try {
    const res = await replayApi.getReport(jobId)
    const blob = new Blob([res.data], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `replay_report_${jobId}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
  } catch (error: unknown) {
    message.error(extractError(error, '导出报告失败'))
  }
}

async function loadAnalysis() {
  if (!job.value || (job.value.failed === 0 && job.value.errored === 0)) return
  analysisLoading.value = true
  try {
    const res = await replayApi.getAnalysis(jobId)
    analysisData.value = res.data
  } catch (error: unknown) {
    analysisData.value = null
    message.error(extractError(error, '加载失败原因分析失败'))
  } finally {
    analysisLoading.value = false
  }
}

async function loadAuditLogs() {
  auditLoading.value = true
  try {
    const page = await loadPagedData<ReplayAuditLog>((params) => replayApi.getAuditLogs(jobId, params), {
      event_type: auditEventType.value || undefined,
    }, auditPagination.page, auditPagination.pageSize, 500)
    auditLogs.value = page.items
    auditPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && auditPagination.page > 1) {
      auditPagination.page = lastValidPage(page.total, auditPagination.pageSize)
      void loadAuditLogs()
      return
    }
  } catch (error: unknown) {
    auditLogs.value = []
    auditPagination.itemCount = 0
    message.error(extractError(error, '加载审计日志失败'))
  } finally {
    auditLoading.value = false
  }
}

async function loadPage() {
  try {
    const res = await replayApi.get(jobId)
    job.value = res.data
    if (res.data.application_id != null) {
      const appRes = await applicationApi.get(res.data.application_id)
      appName.value = appRes.data.name
    } else {
      appName.value = '-'
    }
  } catch (error: unknown) {
    message.error(extractError(error, '加载回放任务失败'))
  }
  await Promise.all([loadResults(), loadAnalysis(), loadAuditLogs()])
}

async function loadResults() {
  resultsLoading.value = true
  try {
    const params: Record<string, string | number | boolean> = {}
    if (resultFilter.value) params.status = resultFilter.value
    const page = await loadPagedData<ReplayResultRow>(
      (requestParams) => replayApi.getResults(jobId, requestParams),
      params,
      resultPagination.page,
      resultPagination.pageSize,
      200,
    )
    results.value = page.items
    resultPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && resultPagination.page > 1) {
      resultPagination.page = lastValidPage(page.total, resultPagination.pageSize)
      void loadResults()
      return
    }
  } catch (error: unknown) {
    results.value = []
    resultPagination.itemCount = 0
    message.error(extractError(error, '加载回放结果失败'))
  } finally {
    resultsLoading.value = false
  }
}

function reloadResultsFromFirstPage() {
  resultPagination.page = 1
  void loadResults()
}

function reloadAuditLogsFromFirstPage() {
  auditPagination.page = 1
  void loadAuditLogs()
}

onMounted(() => {
  void loadPage()
})

  return {
    router,
    canEdit,
    jobId,
    job,
    appName,
    results,
    resultsLoading,
    auditLogs,
    auditLoading,
    auditEventType,
    selectedAuditLog,
    showAuditDetail,
    resultFilter,
    showDiff,
    selectedResult,
    analysisLoading,
    sourceTestCase,
    sourceRecording,
    sourceRecordingSubCallSummary,
    subCallDiff,
    subCallDiffLoading,
    ruleSuggestions,
    applyingSuggestionKey,
    resultPagination,
    auditPagination,
    passRate,
    parsedAssertionResults,
    analysisCategories,
    jobStatusTypeMap,
    jobStatusLabelMap,
    resultStatusTypeMap,
    resultStatusLabelMap,
    failureCategoryLabelMap,
    resultFilterOptions,
    auditEventOptions,
    diffScoreColor,
    resultColumns,
    auditColumns,
    prettyText,
    openAuditDetail,
    openAuditResult,
    rawText,
    failureReasonFields,
    failureReasonPrefix,
    openDiff,
    applyRuleSuggestion,
    openReport,
    loadAuditLogs,
    loadPage,
    loadResults,
    reloadResultsFromFirstPage,
    reloadAuditLogsFromFirstPage,
    formatDateTime
  }
}
