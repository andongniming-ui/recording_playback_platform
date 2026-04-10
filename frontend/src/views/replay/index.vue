<template>
  <n-space vertical :size="16">
    <n-card v-if="canEdit" title="发起回放">
      <n-form :model="launchForm" label-placement="left" label-width="120px">
        <n-form-item label="所属应用">
          <n-select
            v-model:value="launchForm.application_id"
            :options="appOptions"
            clearable
            placeholder="当所选用例都属于同一应用时可留空"
            style="width: 320px"
          />
        </n-form-item>
        <n-form-item label="测试用例">
          <n-select
            v-model:value="launchForm.case_ids"
            multiple
            filterable
            :options="caseOptions"
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
        <n-form-item>
          <n-button type="primary" :loading="launching" :disabled="launchForm.case_ids.length === 0" @click="launchReplay">
            开始回放
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="回放历史">
      <template #header-extra>
        <n-button size="small" @click="loadJobs">刷新</n-button>
      </template>
      <n-data-table :columns="jobColumns" :data="jobs" :loading="loading" :pagination="{ pageSize: 10 }" />
    </n-card>
  </n-space>

  <n-drawer v-model:show="showDrawer" :width="760" placement="right">
    <n-drawer-content :title="`回放结果 - 任务 #${selectedJobId}`" closable>
      <n-space style="margin-bottom: 12px">
        <n-select
          v-model:value="resultFilter"
          :options="resultFilterOptions"
          clearable
          placeholder="按执行结果筛选"
          style="width: 180px"
          @update:value="loadResults"
        />
      </n-space>
      <n-data-table
        :columns="resultColumns"
        :data="results"
        :loading="resultsLoading"
        :pagination="{ pageSize: 20 }"
        size="small"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { NButton, NCard, NDataTable, NDrawer, NDrawerContent, NForm, NFormItem, NInput, NInputNumber, NSpace, NSelect, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'

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
}

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
const caseOptions = ref<SelectOption[]>([])

const tagTypeByJobStatus: Record<string, NonNullable<TagProps['type']>> = {
  DONE: 'success',
  RUNNING: 'info',
  FAILED: 'error',
  PENDING: 'default',
}

const jobStatusLabelMap: Record<string, string> = {
  DONE: '已完成',
  RUNNING: '运行中',
  FAILED: '失败',
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
})

const resultFilterOptions: SelectOption[] = [
  { label: '通过', value: 'PASS' },
  { label: '失败', value: 'FAIL' },
  { label: '异常', value: 'ERROR' },
  { label: '超时', value: 'TIMEOUT' },
]

const jobColumns: DataTableColumns<JobRow> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '任务名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(
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
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 170,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => openDrawer(row.id) }, () => '查看结果'),
        h(NButton, { size: 'tiny', type: 'info', onClick: () => openReport(row.id) }, () => '查看报告'),
      ]),
  },
]

const resultColumns: DataTableColumns<ResultRow> = [
  { title: '请求路径', key: 'request_uri', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (row) => h(
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

function formatDateTime(value?: string) {
  return value ? value.slice(0, 19).replace('T', ' ') : '-'
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
    const params: Record<string, number> = {}
    if (launchForm.value.application_id != null) {
      params.application_id = launchForm.value.application_id
    }
    const res = await replayApi.list(params)
    jobs.value = res.data
  } catch (error: any) {
    jobs.value = []
    message.error(error.response?.data?.detail || '加载回放任务失败')
  } finally {
    loading.value = false
  }
}

async function openDrawer(jobId: number) {
  selectedJobId.value = jobId
  showDrawer.value = true
  await loadResults()
}

async function loadResults() {
  if (selectedJobId.value == null) {
    return
  }
  resultsLoading.value = true
  try {
    const params: Record<string, string | number> = { limit: 100 }
    if (resultFilter.value) {
      params.status = resultFilter.value
    }
    const res = await replayApi.getResults(selectedJobId.value, params)
    results.value = res.data
  } catch (error: any) {
    results.value = []
    message.error(error.response?.data?.detail || '加载回放结果失败')
  } finally {
    resultsLoading.value = false
  }
}

async function launchReplay() {
  launching.value = true
  try {
    const res = await replayApi.create(launchForm.value)
    message.success(`回放任务 #${res.data.id} 已启动`)
    launchForm.value.case_ids = []
    launchForm.value.name = ''
    await loadJobs()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '启动回放任务失败')
  } finally {
    launching.value = false
  }
}

onMounted(async () => {
  try {
    const [appsRes, casesRes] = await Promise.all([
      applicationApi.list(),
      testCaseApi.list({ limit: 100, status: 'active' }),
    ])
    appOptions.value = appsRes.data.map((app: { id: number; name: string }) => ({ label: app.name, value: app.id }))
    caseOptions.value = casesRes.data.map((testCase: { id: number; request_method: string; request_uri: string; name: string }) => ({
      label: `[${testCase.request_method}] ${testCase.request_uri} - ${testCase.name}`,
      value: testCase.id,
    }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '初始化回放页面失败')
  }
  await loadJobs()
})
</script>
