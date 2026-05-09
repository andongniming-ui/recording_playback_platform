<template>
  <n-space vertical :size="16">
    <n-card v-if="canEdit" title="发起回放">
      <template #header-extra>
        <n-space>
          <n-button size="small" @click="router.push('/replay/history')">查看全部历史</n-button>
          <n-button size="small" :disabled="launchForm.application_id == null" @click="loadAppDefaults">
            加载应用默认配置
          </n-button>
        </n-space>
      </template>
      <n-form :model="launchForm" label-placement="left" label-width="120px">
        <n-form-item label="所属应用">
          <n-select
            v-model:value="launchForm.application_id"
            :options="appOptions"
            clearable
            placeholder="当所选用例都属于同一应用时可留空"
            style="width: 320px"
            @update:value="reloadJobsFromFirstPage"
          />
        </n-form-item>
        <n-form-item label="测试用例">
          <n-select
            v-model:value="launchForm.case_ids"
            multiple
            filterable
            :options="filteredCaseOptions"
            placeholder="请选择一个或多个测试用例"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="并发数">
          <n-input-number v-model:value="launchForm.concurrency" :min="1" :max="50" />
        </n-form-item>
        <n-form-item label="超时时间(ms)">
          <n-input-number v-model:value="launchForm.timeout_ms" :min="500" :max="60000" :step="500" />
        </n-form-item>
        <n-form-item label="任务名称">
          <n-input v-model:value="launchForm.name" placeholder="可选，便于识别" style="width: 320px" />
        </n-form-item>

        <n-collapse>
          <n-collapse-item title="高级回放配置" name="advanced">
            <n-space vertical :size="16" style="width: 100%">
              <n-alert type="info" :show-icon="false">
                这里的配置会直接影响回放比对结果。常用的是 `忽略字段`、`智能降噪`、`性能阈值` 和 `断言规则`。
              </n-alert>

              <n-grid cols="1 l:2" responsive="screen" :x-gap="16" :y-gap="8">
                <n-grid-item>
                  <n-form-item label="请求间隔(ms)">
                    <n-input-number v-model:value="launchForm.delay_ms" :min="0" :step="100" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="性能阈值(ms)">
                    <n-input-number v-model:value="launchForm.perf_threshold_ms" :min="0" clearable />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="失败重试">
                    <n-input-number v-model:value="launchForm.retry_count" :min="0" :max="5" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="流量放大">
                    <n-space align="center">
                      <n-input-number v-model:value="launchForm.repeat_count" :min="1" :max="100" style="width: 100px" />
                      <span class="hint-text">每条录制重复回放 N 次</span>
                    </n-space>
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="Host 覆盖">
                    <n-input v-model:value="launchForm.target_host" placeholder="留空使用应用配置的地址" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="Webhook URL">
                    <n-input v-model:value="launchForm.webhook_url" placeholder="回放完成后回调，留空不通知" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>

              <n-form-item label="Mock 子调用">
                <n-space align="center">
                  <n-switch v-model:value="launchForm.use_sub_invocation_mocks" />
                  <span class="hint-text">适合从录制生成的用例，回放时复用录制时的下游返回值。</span>
                </n-space>
              </n-form-item>

              <n-form-item label="严格子调用比对">
                <n-space align="center">
                  <n-switch v-model:value="launchForm.fail_on_sub_call_diff" />
                  <span class="hint-text">开启后，子调用缺失、数量不一致或响应不一致都会判定回放失败。</span>
                </n-space>
              </n-form-item>

              <n-form-item label="智能降噪">
                <n-space align="center">
                  <n-switch v-model:value="launchForm.smart_noise_reduction" />
                  <span class="hint-text">自动忽略时间戳、UUID、Token 等常见动态字段。</span>
                </n-space>
              </n-form-item>

              <n-form-item label="忽略数组顺序">
                <n-space align="center">
                  <n-switch v-model:value="launchForm.ignore_order" />
                  <span class="hint-text">关闭后，响应数组元素顺序不同也会判定为差异。</span>
                </n-space>
              </n-form-item>

              <n-form-item label="忽略字段">
                <n-space vertical style="width: 100%">
                  <n-space>
                    <n-button size="small" @click="addIgnorePreset('timestamp')">timestamp</n-button>
                    <n-button size="small" @click="addIgnorePreset('traceId')">traceId</n-button>
                    <n-button size="small" @click="addIgnorePreset('requestId')">requestId</n-button>
                    <n-button size="small" @click="addIgnorePreset('nonce')">nonce</n-button>
                    <n-button size="small" @click="addIgnorePreset('sign')">sign</n-button>
                    <n-button size="small" @click="addIgnorePreset('token')">token</n-button>
                  </n-space>
                  <n-dynamic-tags v-model:value="launchForm.ignore_fields" />
                  <span class="hint-text">填写字段名即可，例如 `timestamp`、`traceId`。会和应用默认忽略字段、用例忽略字段一起生效。</span>
                </n-space>
              </n-form-item>

              <n-form-item label="请求头转换">
                <n-space vertical style="width: 100%">
                  <n-space
                    v-for="(transform, index) in launchForm.header_transforms"
                    :key="index"
                    align="center"
                    wrap
                    style="width: 100%"
                  >
                    <n-select
                      v-model:value="transform.type"
                      :options="headerTransformTypeOptions"
                      style="width: 120px"
                    />
                    <n-input v-model:value="transform.key" placeholder="Header 名称" style="width: 180px" />
                    <n-input
                      v-if="transform.type !== 'remove'"
                      v-model:value="transform.value"
                      placeholder="Header 值"
                      style="width: 260px"
                    />
                    <n-button size="small" type="error" @click="removeHeaderTransform(index)">删除</n-button>
                  </n-space>
                  <n-button size="small" dashed @click="addHeaderTransform">+ 添加请求头转换</n-button>
                </n-space>
              </n-form-item>

              <n-form-item label="差异规则">
                <n-space vertical style="width: 100%">
                  <n-space
                    v-for="(rule, index) in launchForm.diff_rules"
                    :key="index"
                    align="center"
                    wrap
                    style="width: 100%"
                  >
                    <n-select v-model:value="rule.type" :options="diffRuleTypeOptions" style="width: 180px" />
                    <n-input v-model:value="rule.path" placeholder="字段路径，如 data.price" style="width: 220px" />
                    <n-input-number
                      v-if="rule.type === 'numeric_tolerance'"
                      v-model:value="rule.tolerance"
                      :min="0"
                      :step="0.01"
                      style="width: 140px"
                    />
                    <n-input
                      v-if="rule.type === 'regex_match'"
                      v-model:value="rule.pattern"
                      placeholder="正则表达式"
                      style="width: 220px"
                    />
                    <n-button size="small" type="error" @click="removeDiffRule(index)">删除</n-button>
                  </n-space>
                  <n-button size="small" dashed @click="addDiffRule">+ 添加差异规则</n-button>
                </n-space>
              </n-form-item>

              <n-form-item label="断言规则">
                <n-space vertical style="width: 100%">
                  <n-space
                    v-for="(rule, index) in launchForm.assertions"
                    :key="index"
                    align="center"
                    wrap
                    style="width: 100%"
                  >
                    <n-select v-model:value="rule.type" :options="assertionTypeOptions" style="width: 180px" />
                    <n-input
                      v-if="needsPath(rule.type)"
                      v-model:value="rule.path"
                      placeholder="字段路径，如 code"
                      style="width: 200px"
                    />
                    <n-input
                      v-if="needsValue(rule.type)"
                      v-model:value="rule.value"
                      placeholder="期望值"
                      style="width: 180px"
                    />
                    <n-input
                      v-if="rule.type === 'json_path_regex'"
                      v-model:value="rule.pattern"
                      placeholder="正则表达式"
                      style="width: 220px"
                    />
                    <n-button size="small" type="error" @click="removeAssertion(index)">删除</n-button>
                  </n-space>
                  <n-button size="small" dashed @click="addAssertion">+ 添加断言规则</n-button>
                </n-space>
              </n-form-item>
            </n-space>
          </n-collapse-item>
        </n-collapse>

        <n-form-item>
          <n-button type="primary" :loading="launching" :disabled="launchForm.case_ids.length === 0" @click="launchReplay">
            开始回放
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="最近回放任务">
      <template #header-extra>
        <n-space>
          <n-button
            v-if="canEdit && selectedJobIds.length > 0"
            size="small"
            type="error"
            @click="deleteSelectedJobs"
          >
            批量删除{{ selectedJobIds.length > 0 ? ` (${selectedJobIds.length})` : '' }}
          </n-button>
          <n-button size="small" @click="loadJobs">刷新</n-button>
          <n-button size="small" @click="router.push('/replay/history')">全部历史</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="jobColumns"
        :data="jobs"
        :loading="loading"
        :pagination="jobPagination"
        :row-key="(row: JobRow) => row.id"
        remote
        v-model:checked-row-keys="selectedJobIds"
        @update:sorter="handleJobSorterChange"
      />
    </n-card>
  </n-space>

  <n-drawer v-model:show="showDrawer" :width="760" placement="right">
    <n-drawer-content :title="`回放结果 - 任务 #${selectedJobId}`" closable>
      <n-space style="margin-bottom: 12px">
        <n-select
          v-model:value="resultFilter"
          :options="resultFilterOptions"
          clearable
          placeholder="按结果明细筛选"
          style="width: 180px"
          @update:value="reloadResultsFromFirstPage"
        />
      </n-space>
      <n-data-table
        :columns="resultColumns"
        :data="results"
        :loading="resultsLoading"
        :pagination="resultPagination"
        size="small"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NAlert,
  NButton,
  NCard,
  NCollapse,
  NCollapseItem,
  NDataTable,
  NDrawer,
  NDrawerContent,
  NDynamicTags,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NInputNumber,
  NPopconfirm,
  NSpace,
  NSelect,
  NSwitch,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import type { AssertionRule, DiffRule, HeaderTransform } from '@/api/replays'
import { formatDateTime } from '@/utils/format'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData, unpackPagedResponse } from '@/utils/pagination'

type JobRow = {
  id: number
  name: string | null
  status: string
  total: number
  passed: number
  failed: number
  errored: number
  created_at: string
}

type ResultRow = {
  request_uri: string | null
  status: string
  actual_status_code: number | null
  latency_ms: number | null
  failure_reason: string | null
  use_sub_invocation_mocks?: boolean
  source_recording_id?: number | null
  source_recording_transaction_code?: string | null
  source_recording_scene_key?: string | null
  source_recording_sub_call_count?: number | null
}

type CaseCatalogItem = {
  id: number
  name: string
  request_method: string
  request_uri: string
  application_id?: number | null
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const jobs = ref<JobRow[]>([])
const loading = ref(false)
const launching = ref(false)
const showDrawer = ref(false)
const selectedJobId = ref<number | null>(null)
const results = ref<ResultRow[]>([])
const resultsLoading = ref(false)
const resultFilter = ref<string | null>(null)
const appOptions = ref<SelectOption[]>([])
const caseCatalog = ref<CaseCatalogItem[]>([])
const selectedJobIds = ref<(string | number)[]>([])
const jobSort = ref(defaultSortState('created_at'))
const jobPagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 个任务`,
  onUpdatePage: (page: number) => {
    jobPagination.page = page
    void loadJobs()
  },
  onUpdatePageSize: (pageSize: number) => {
    jobPagination.pageSize = pageSize
    jobPagination.page = 1
    void loadJobs()
  },
})
const resultPagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  pageSizes: [20, 50, 100, 200],
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

const tagTypeByJobStatus: Record<string, NonNullable<TagProps['type']>> = {
  DONE: 'success',
  RUNNING: 'info',
  FAILED: 'error',
  PENDING: 'default',
}

const jobStatusLabelMap: Record<string, string> = {
  DONE: '已完成',
  RUNNING: '运行中',
  FAILED: '存在失败',
  PENDING: '待执行',
}

const tagTypeByResultStatus: Record<string, NonNullable<TagProps['type']>> = {
  PASS: 'success',
  FAIL: 'error',
  ERROR: 'warning',
  TIMEOUT: 'warning',
  PENDING: 'default',
}

const resultStatusLabelMap: Record<string, string> = {
  PASS: '通过',
  FAIL: '失败',
  ERROR: '异常',
  TIMEOUT: '超时',
  PENDING: '待执行',
}

const launchForm = ref({
  name: '',
  application_id: null as number | null,
  case_ids: [] as number[],
  concurrency: 5,
  timeout_ms: 5000,
  delay_ms: 0,
  ignore_fields: [] as string[],
  use_sub_invocation_mocks: false,
  fail_on_sub_call_diff: false,
  diff_rules: [] as DiffRule[],
  assertions: [] as AssertionRule[],
  perf_threshold_ms: null as number | null,
  webhook_url: '',
  notify_type: null as string | null,
  smart_noise_reduction: false,
  ignore_order: true,
  retry_count: 0,
  repeat_count: 1,
  header_transforms: [] as HeaderTransform[],
  target_host: '',
})

const resultFilterOptions: SelectOption[] = [
  { label: '通过', value: 'PASS' },
  { label: '失败', value: 'FAIL' },
  { label: '异常', value: 'ERROR' },
  { label: '超时', value: 'TIMEOUT' },
]

const headerTransformTypeOptions: SelectOption[] = [
  { label: '替换', value: 'replace' },
  { label: '新增', value: 'add' },
  { label: '删除', value: 'remove' },
]

const diffRuleTypeOptions: SelectOption[] = [
  { label: '忽略字段', value: 'ignore' },
  { label: '数值容差', value: 'numeric_tolerance' },
  { label: '正则匹配', value: 'regex_match' },
  { label: '仅比较类型', value: 'type_only' },
]

const assertionTypeOptions: SelectOption[] = [
  { label: 'HTTP状态码等于', value: 'status_code_eq' },
  { label: '响应体不为空', value: 'response_not_empty' },
  { label: 'JSON字段等于', value: 'json_path_eq' },
  { label: 'JSON字段包含', value: 'json_path_contains' },
  { label: 'JSON字段存在', value: 'json_path_exists' },
  { label: 'JSON字段匹配正则', value: 'json_path_regex' },
  { label: 'Diff分值小于等于', value: 'diff_score_lte' },
]

const filteredCaseOptions = computed<SelectOption[]>(() => {
  const selectedAppId = launchForm.value.application_id
  const selectedIds = new Set(launchForm.value.case_ids)
  return caseCatalog.value
    .filter((item) => selectedAppId == null || item.application_id === selectedAppId || selectedIds.has(item.id))
    .map((item) => ({
      label: `[${item.request_method}] ${item.request_uri} - ${item.name}`,
      value: item.id,
    }))
})

const jobColumns = computed<DataTableColumns<JobRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const, disabled: (row: JobRow) => ['RUNNING', 'PENDING'].includes(row.status) }] : []),
  {
    title: '#',
    key: 'seq',
    width: 55,
    render: (_row: JobRow, index: number) => (jobPagination.page - 1) * jobPagination.pageSize + index + 1,
  },
  { title: '任务名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) =>
      h(
        NTag,
        { type: tagTypeByJobStatus[row.status] ?? 'default', size: 'small' },
        () => jobStatusLabelMap[row.status] || row.status,
      ),
  },
  {
    title: '进度',
    key: 'progress',
    width: 120,
    render: (row) => {
      const completed = (row.passed ?? 0) + (row.failed ?? 0) + (row.errored ?? 0)
      return row.total ? `${completed}/${row.total} (${((completed / row.total) * 100).toFixed(0)}%)` : '-'
    },
  },
  {
    title: '失败数',
    key: 'failed',
    width: 80,
    render: (row) => h('span', { style: row.failed > 0 ? 'color:#d03050' : '' }, String(row.failed ?? 0)),
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    sorter: true,
    sortOrder: resolveSortOrder(jobSort.value, 'created_at'),
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: canEdit ? 290 : 220,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/results/${row.id}`) }, () => '查看结果'),
        h(NButton, { size: 'tiny', onClick: () => openDrawer(row.id) }, () => '快速看'),
        h(NButton, { size: 'tiny', type: 'info', onClick: () => openReport(row.id) }, () => '查看报告'),
        ...(canEdit ? [
          h(NPopconfirm, { onPositiveClick: () => deleteJob(row.id) }, {
            default: () => '确认删除该回放任务?',
            trigger: () => h(NButton, { size: 'tiny', type: 'error', disabled: ['RUNNING', 'PENDING'].includes(row.status) }, () => '删除'),
          }),
        ] : []),
      ]),
  },
])

const resultColumns: DataTableColumns<ResultRow> = [
  { title: '请求路径', key: 'request_uri', ellipsis: { tooltip: true } },
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
    width: 90,
    render: (row) =>
      h(
        NTag,
        { type: tagTypeByResultStatus[row.status] ?? 'default', size: 'small' },
        () => resultStatusLabelMap[row.status] || row.status,
      ),
  },
  { title: '响应码', key: 'actual_status_code', width: 70 },
  {
    title: '耗时',
    key: 'latency_ms',
    width: 90,
    render: (row) => (row.latency_ms != null ? `${row.latency_ms}ms` : '-'),
  },
  { title: '失败原因', key: 'failure_reason', ellipsis: { tooltip: true } },
]

function needsPath(type?: string) {
  return !!type && !['status_code_eq', 'response_not_empty', 'diff_score_lte'].includes(type)
}

function needsValue(type?: string) {
  return !!type && ['status_code_eq', 'json_path_eq', 'json_path_contains', 'diff_score_lte'].includes(type)
}

function addIgnorePreset(field: string) {
  if (!launchForm.value.ignore_fields.includes(field)) {
    launchForm.value.ignore_fields.push(field)
  }
}

function addHeaderTransform() {
  launchForm.value.header_transforms.push({ type: 'replace', key: '', value: '' })
}

function removeHeaderTransform(index: number) {
  launchForm.value.header_transforms.splice(index, 1)
}

function addDiffRule() {
  launchForm.value.diff_rules.push({ type: 'ignore', path: '' })
}

function removeDiffRule(index: number) {
  launchForm.value.diff_rules.splice(index, 1)
}

function addAssertion() {
  launchForm.value.assertions.push({ type: 'status_code_eq', value: '200' })
}

function removeAssertion(index: number) {
  launchForm.value.assertions.splice(index, 1)
}

function inferApplicationIdFromCases() {
  if (launchForm.value.application_id != null || launchForm.value.case_ids.length === 0) {
    return
  }
  const selected = caseCatalog.value.filter((item) => launchForm.value.case_ids.includes(item.id))
  const appIds = [...new Set(selected.map((item) => item.application_id).filter((item) => item != null))]
  if (appIds.length === 1) {
    launchForm.value.application_id = Number(appIds[0])
  }
}

async function openReport(jobId: number) {
  try {
    const res = await replayApi.getReport(jobId)
    const blob = new Blob([res.data], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank', 'noopener')
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载报告失败')
  }
}

async function loadJobs() {
  loading.value = true
  try {
    const params: Record<string, string | number | boolean> = {}
    if (launchForm.value.application_id != null) {
      params.application_id = launchForm.value.application_id
    }
    params.sort_by = jobSort.value.columnKey
    params.sort_order = toApiSortOrder(jobSort.value.order)
    const page = await loadPagedData<JobRow>(replayApi.list, params, jobPagination.page, jobPagination.pageSize, 100)
    jobs.value = page.items
    jobPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && jobPagination.page > 1) {
      jobPagination.page = lastValidPage(page.total, jobPagination.pageSize)
      void loadJobs()
      return
    }
    selectedJobIds.value = []
  } catch (error: any) {
    jobs.value = []
    jobPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载回放任务失败')
  } finally {
    loading.value = false
  }
}

async function deleteJob(jobId: number) {
  try {
    await replayApi.delete(jobId)
    message.success('回放任务已删除')
    await loadJobs()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}

async function deleteSelectedJobs() {
  if (selectedJobIds.value.length === 0) return
  try {
    const res = await replayApi.bulkDelete({ ids: selectedJobIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 个回放任务`)
    await loadJobs()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
  }
}

function handleJobSorterChange(sorter: any) {
  jobSort.value = updateSortState(sorter, 'created_at')
  jobPagination.page = 1
  void loadJobs()
}

function reloadJobsFromFirstPage() {
  jobPagination.page = 1
  void loadJobs()
}

async function openDrawer(jobId: number) {
  selectedJobId.value = jobId
  showDrawer.value = true
  resultPagination.page = 1
  await loadResults()
}

async function loadResults() {
  if (selectedJobId.value == null) {
    return
  }
  resultsLoading.value = true
  try {
    const params: Record<string, string | number | boolean> = {}
    if (resultFilter.value) {
      params.status = resultFilter.value
    }
    const page = await loadPagedData<ResultRow>(
      (requestParams) => replayApi.getResults(selectedJobId.value!, requestParams),
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
  } catch (error: any) {
    results.value = []
    resultPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载回放结果失败')
  } finally {
    resultsLoading.value = false
  }
}

function reloadResultsFromFirstPage() {
  resultPagination.page = 1
  void loadResults()
}

async function loadAppDefaults() {
  if (launchForm.value.application_id == null) {
    message.warning('请先选择应用')
    return
  }
  try {
    const res = await applicationApi.get(launchForm.value.application_id)
    const app = res.data
    if (Array.isArray(app.default_ignore_fields)) {
      launchForm.value.ignore_fields = [...new Set([...launchForm.value.ignore_fields, ...app.default_ignore_fields])]
    }
    if (Array.isArray(app.default_assertions) && app.default_assertions.length) {
      launchForm.value.assertions = [...app.default_assertions]
    }
    if (app.default_perf_threshold_ms != null) {
      launchForm.value.perf_threshold_ms = app.default_perf_threshold_ms
    }
    message.success('已加载应用默认配置')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载应用默认配置失败')
  }
}

async function launchReplay() {
  launching.value = true
  try {
    const payload: Record<string, unknown> = {
      ...launchForm.value,
      application_id: launchForm.value.application_id ?? undefined,
      perf_threshold_ms: launchForm.value.perf_threshold_ms ?? undefined,
      notify_type: launchForm.value.notify_type || undefined,
      webhook_url: launchForm.value.webhook_url.trim() || undefined,
      target_host: launchForm.value.target_host.trim() || undefined,
      repeat_count: launchForm.value.repeat_count > 1 ? launchForm.value.repeat_count : undefined,
      ignore_fields: launchForm.value.ignore_fields.length ? launchForm.value.ignore_fields : undefined,
      diff_rules: launchForm.value.diff_rules.filter((rule) => rule.type && (rule.path || rule.type === 'ignore')),
      assertions: launchForm.value.assertions.filter((rule) => rule.type),
      header_transforms: launchForm.value.header_transforms.filter((item) => item.key.trim()),
    }
    const res = await replayApi.create(payload)
    message.success(`回放任务 #${res.data.id} 已启动`)
    launchForm.value.case_ids = []
    launchForm.value.name = ''
    await loadJobs()
    void router.push(`/results/${res.data.id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '启动回放任务失败')
  } finally {
    launching.value = false
  }
}

onMounted(async () => {
  const queryAppId = typeof route.query.application_id === 'string' ? Number(route.query.application_id) : null
  const queryCaseIds =
    typeof route.query.case_ids === 'string'
      ? route.query.case_ids
          .split(',')
          .map((item) => Number(item))
          .filter((item) => !Number.isNaN(item))
      : typeof route.query.case_id === 'string'
        ? [Number(route.query.case_id)].filter((item) => !Number.isNaN(item))
        : []
  if (queryAppId != null && !Number.isNaN(queryAppId)) {
    launchForm.value.application_id = queryAppId
  }
  if (queryCaseIds.length > 0) {
    launchForm.value.case_ids = queryCaseIds
  }
  try {
    const [appsRes, casesRes] = await Promise.all([
      applicationApi.list({ limit: 100 }),
      testCaseApi.list({ limit: 1000, status: 'active' }),
    ])
    const appsPage = unpackPagedResponse<{ id: number; name: string }>(appsRes.data)
    const casesPage = unpackPagedResponse<CaseCatalogItem>(casesRes.data)
    appOptions.value = appsPage.items.map((app) => ({ label: app.name, value: app.id }))
    caseCatalog.value = casesPage.items.map((testCase) => ({
      id: testCase.id,
      name: testCase.name,
      request_method: testCase.request_method,
      request_uri: testCase.request_uri,
      application_id: testCase.application_id,
    }))
    inferApplicationIdFromCases()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '初始化回放页面失败')
  }
  await loadJobs()
})
</script>

<style scoped>
.hint-text {
  font-size: 13px;
  color: #666;
}
</style>
