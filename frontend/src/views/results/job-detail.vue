<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/replay/history')">回放历史</n-breadcrumb-item>
        <n-breadcrumb-item>任务 #{{ jobId }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button @click="router.push('/replay/history')">返回历史</n-button>
        <n-button type="info" @click="openReport">导出 HTML 报告</n-button>
      </n-space>
    </n-space>

    <!-- 任务基本信息 -->
    <n-card v-if="job" :title="job.name || `回放任务 #${jobId}`">
      <template #header-extra>
        <n-tag :type="jobStatusTypeMap[job.status] || 'default'">
          {{ jobStatusLabelMap[job.status] || job.status }}
        </n-tag>
      </template>
      <n-descriptions bordered :column="3" size="small">
        <n-descriptions-item label="回放应用">{{ appName }}</n-descriptions-item>
        <n-descriptions-item label="开始时间">{{ formatDateTime(job.started_at) }}</n-descriptions-item>
        <n-descriptions-item label="完成时间">{{ formatDateTime(job.finished_at) }}</n-descriptions-item>
        <n-descriptions-item label="并发数">{{ job.concurrency }}</n-descriptions-item>
        <n-descriptions-item label="超时">{{ job.timeout_ms }}ms</n-descriptions-item>
        <n-descriptions-item label="智能降噪">{{ job.smart_noise_reduction ? '开启' : '关闭' }}</n-descriptions-item>
      </n-descriptions>
      <n-space v-if="job.ignore_fields?.length" style="margin-top:12px">
        <span style="color:#666;font-size:13px">忽略字段：</span>
        <n-tag v-for="f in job.ignore_fields" :key="f" size="small" type="default">{{ f }}</n-tag>
      </n-space>
    </n-card>

    <!-- 统计卡片 -->
    <n-grid :cols="4" :x-gap="16">
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="总计" :value="job?.total || 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="通过">
            <template #default><span style="color:#18a058;font-size:28px;font-weight:bold">{{ job?.passed || 0 }}</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="失败">
            <template #default><span style="color:#d03050;font-size:28px;font-weight:bold">{{ job?.failed || 0 }}</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="通过率">
            <template #default>
              <span :style="{ color: passRate >= 90 ? '#18a058' : passRate >= 60 ? '#f0a020' : '#d03050', fontSize: '28px', fontWeight: 'bold' }">
                {{ passRate.toFixed(1) }}%
              </span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 失败原因分析 -->
    <n-card v-if="job && (job.failed > 0 || job.errored > 0)" title="失败原因分析">
      <n-spin :show="analysisLoading">
        <n-grid :cols="5" :x-gap="12">
          <n-grid-item v-for="cat in analysisCategories" :key="cat.key">
            <div class="analysis-card">
              <div class="analysis-icon">{{ cat.icon }}</div>
              <div class="analysis-label">{{ cat.label }}</div>
              <div class="analysis-count" :style="{ color: cat.color }">{{ cat.count }}</div>
              <n-progress
                type="line"
                :percentage="cat.percentage"
                :color="cat.color"
                :rail-color="'#f0f0f0'"
                :indicator-placement="'inside'"
                style="margin-top:6px"
              />
              <div class="analysis-pct">{{ cat.percentage.toFixed(0) }}%</div>
            </div>
          </n-grid-item>
        </n-grid>
      </n-spin>
    </n-card>

    <!-- 逐条结果 -->
    <n-card title="逐条结果">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="resultFilter"
            :options="resultFilterOptions"
            clearable
            placeholder="按状态筛选"
            style="width:160px"
            @update:value="loadResults"
          />
        </n-space>
      </template>
      <n-data-table
        :columns="resultColumns"
        :data="results"
        :loading="resultsLoading"
        :pagination="{ pageSize: 15 }"
        size="small"
      />
    </n-card>
  </n-space>

  <!-- 对比详情弹窗 -->
  <n-modal v-model:show="showDiff" preset="card" style="width:1000px" title="结果对比详情">
    <n-space vertical :size="12">
      <n-descriptions bordered :column="3" size="small">
        <n-descriptions-item label="接口">
          <b>{{ selectedResult?.request_method }}</b> {{ selectedResult?.request_uri }}
        </n-descriptions-item>
        <n-descriptions-item label="状态码">{{ selectedResult?.actual_status_code || '-' }}</n-descriptions-item>
        <n-descriptions-item label="Diff Score">
          <span :style="{ color: diffScoreColor(selectedResult?.diff_score) }">
            {{ selectedResult?.diff_score != null ? selectedResult.diff_score.toFixed(3) : '-' }}
          </span>
        </n-descriptions-item>
        <n-descriptions-item label="来源录制">
          <n-space align="center" :size="8">
            <n-tag :type="selectedResult?.use_sub_invocation_mocks ? 'success' : 'default'" size="small">
              {{ selectedResult?.use_sub_invocation_mocks ? 'Mock 开启' : 'Mock 关闭' }}
            </n-tag>
            <span>{{ selectedResult?.source_recording_id ? `#${selectedResult.source_recording_id}` : '-' }}</span>
          </n-space>
        </n-descriptions-item>
        <n-descriptions-item label="子调用数">{{ selectedResult?.source_recording_sub_call_count ?? '-' }}</n-descriptions-item>
        <n-descriptions-item label="失败分类" :span="2">
          {{ failureCategoryLabelMap[selectedResult?.failure_category || ''] || selectedResult?.failure_category || '-' }}
        </n-descriptions-item>
        <n-descriptions-item label="耗时">{{ selectedResult?.latency_ms != null ? `${selectedResult.latency_ms}ms` : '-' }}</n-descriptions-item>
      </n-descriptions>

      <n-grid :cols="2" :x-gap="16">
        <n-grid-item>
          <n-card title="期望响应（SIT 录制）" size="small">
            <pre class="code-block">{{ rawText(selectedResult?.expected_response) }}</pre>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="实际响应（UAT 回放）" size="small">
            <pre class="code-block">{{ rawText(selectedResult?.actual_response) }}</pre>
          </n-card>
        </n-grid-item>
      </n-grid>

      <n-card v-if="sourceRecording" title="来源录制链路" size="small">
        <template #header-extra>
          <n-space align="center" :size="8">
            <n-tag type="info" size="small">来源用例 #{{ sourceTestCase?.id || '-' }}</n-tag>
            <n-button v-if="sourceRecording.id" size="small" @click="router.push(`/recording/recordings/${sourceRecording.id}`)">
              打开录制详情
            </n-button>
          </n-space>
        </template>
        <n-descriptions bordered :column="2" size="small">
          <n-descriptions-item label="请求">{{ sourceRecording.request_method }} {{ sourceRecording.request_uri }}</n-descriptions-item>
          <n-descriptions-item label="交易码">{{ sourceRecording.transaction_code || '-' }}</n-descriptions-item>
          <n-descriptions-item label="治理状态">{{ sourceRecording.governance_status }}</n-descriptions-item>
          <n-descriptions-item label="子调用概览">{{ sourceRecordingSubCallSummary || '-' }}</n-descriptions-item>
        </n-descriptions>
        <div style="margin-top: 12px">
          <SubCallPanel :sub-calls="sourceRecording.sub_calls" />
        </div>
      </n-card>

      <n-tabs type="line" animated>
        <n-tab-pane name="diff" tab="差异详情">
          <n-card size="small" :bordered="false">
            <n-space vertical>
              <div>
                <div class="section-title">Diff 结果</div>
                <pre class="code-block compact">{{ prettyText(selectedResult?.diff_result) }}</pre>
              </div>
              <div v-if="parsedAssertionResults.length > 0">
                <div class="section-title">断言结果</div>
                <n-space vertical :size="6">
                  <div v-for="(item, i) in parsedAssertionResults" :key="i">
                    <n-tag :type="item.passed ? 'success' : 'error'" size="small">{{ item.passed ? '通过' : '失败' }}</n-tag>
                    <span style="margin-left:8px;font-size:12px">{{ item.message }}</span>
                  </div>
                </n-space>
              </div>
              <div v-if="selectedResult?.failure_reason">
                <div class="section-title">失败原因</div>
                <template v-if="failureReasonFields(selectedResult.failure_reason)">
                  <div style="font-size:13px;color:#555;margin-bottom:8px">
                    {{ failureReasonPrefix(selectedResult.failure_reason) }}
                  </div>
                  <n-space vertical :size="4">
                    <div
                      v-for="field in failureReasonFields(selectedResult.failure_reason)"
                      :key="field"
                      style="display:flex;align-items:center;gap:8px"
                    >
                      <n-tag type="error" size="small" style="font-family:monospace">{{ field }}</n-tag>
                    </div>
                  </n-space>
                </template>
                <pre v-else class="code-block compact">{{ selectedResult.failure_reason }}</pre>
              </div>
            </n-space>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="subcall" tab="子调用对比">
          <n-spin :show="subCallDiffLoading">
            <SubCallDiffPanel
              :pairs="subCallDiff?.pairs ?? []"
              :replayed="subCallDiff?.replayed ?? []"
            />
          </n-spin>
        </n-tab-pane>
      </n-tabs>
    </n-space>
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
  NGrid,
  NGridItem,
  NModal,
  NProgress,
  NSpace,
  NSelect,
  NSpin,
  NStatistic,
  NTabPane,
  NTabs,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { formatDateTime } from '@/utils/format'
import SubCallPanel from '@/components/recording/SubCallPanel.vue'
import SubCallDiffPanel from '@/components/recording/SubCallDiffPanel.vue'
import type { SubCallDiffResult } from '@/api/replays'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'

type ReplayJobRow = {
  id: number
  name?: string | null
  application_id?: number | null
  status: string
  concurrency: number
  timeout_ms: number
  delay_ms?: number
  total: number
  passed: number
  failed: number
  errored: number
  ignore_fields?: string[] | null
  diff_rules?: Array<{ type: string; path?: string | null }> | null
  assertions?: Array<{ type: string; path?: string | null }> | null
  header_transforms?: Array<{ type: string; key: string }> | null
  use_sub_invocation_mocks?: boolean
  perf_threshold_ms?: number | null
  smart_noise_reduction?: boolean
  retry_count?: number
  webhook_url?: string | null
  created_at: string
  started_at?: string | null
  finished_at?: string | null
}

type ReplayResultRow = {
  id: number
  test_case_id?: number | null
  use_sub_invocation_mocks?: boolean
  source_recording_id?: number | null
  source_recording_transaction_code?: string | null
  source_recording_scene_key?: string | null
  source_recording_sub_call_count?: number | null
  request_method?: string | null
  request_uri?: string | null
  actual_status_code?: number | null
  actual_response?: string | null
  expected_response?: string | null
  diff_result?: string | null
  diff_score?: number | null
  assertion_results?: string | null
  status: string
  latency_ms?: number | null
  failure_category?: string | null
  failure_reason?: string | null
  created_at: string
  transaction_code?: string | null
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const jobId = Number(route.params.jobId)

const job = ref<ReplayJobRow | null>(null)
const appName = ref('-')
const results = ref<ReplayResultRow[]>([])
const resultsLoading = ref(false)
const resultFilter = ref<string | null>(null)
const showDiff = ref(false)
const selectedResult = ref<ReplayResultRow | null>(null)
const analysisLoading = ref(false)
const analysisData = ref<any>(null)
const sourceTestCase = ref<any | null>(null)
const sourceRecording = ref<any | null>(null)
const sourceRecordingSubCallSummary = ref('')
const subCallDiff = ref<SubCallDiffResult | null>(null)
const subCallDiffLoading = ref(false)

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
  DONE: '已完成', RUNNING: '运行中', FAILED: '失败', PENDING: '待执行', CANCELLED: '已取消',
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

function prettyText(value?: string | null) {
  if (!value) return '-'
  try { return JSON.stringify(JSON.parse(value), null, 2) } catch { return value }
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
  } catch (error: any) {
    message.error(error.response?.data?.detail || '导出报告失败')
  }
}

async function loadAnalysis() {
  if (!job.value || (job.value.failed === 0 && job.value.errored === 0)) return
  analysisLoading.value = true
  try {
    const res = await replayApi.getAnalysis(jobId)
    analysisData.value = res.data
  } catch {
    analysisData.value = null
  } finally {
    analysisLoading.value = false
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
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载回放任务失败')
  }
  await Promise.all([loadResults(), loadAnalysis()])
}

async function loadResults() {
  resultsLoading.value = true
  try {
    const params: Record<string, string | number> = { limit: 200 }
    if (resultFilter.value) params.status = resultFilter.value
    const res = await replayApi.getResults(jobId, params)
    results.value = res.data
  } catch (error: any) {
    results.value = []
    message.error(error.response?.data?.detail || '加载结果详情失败')
  } finally {
    resultsLoading.value = false
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
  max-height: 320px;
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  background: #f8f8f8;
  font-family: monospace;
  font-size: 12px;
}
.code-block.compact {
  max-height: 160px;
}
.section-title {
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #555;
}
.analysis-card {
  text-align: center;
  padding: 12px 8px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
}
.analysis-icon {
  font-size: 22px;
  margin-bottom: 4px;
}
.analysis-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}
.analysis-count {
  font-size: 24px;
  font-weight: bold;
  line-height: 1.2;
}
.analysis-pct {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
