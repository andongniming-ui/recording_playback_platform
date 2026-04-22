<template>
  <n-space vertical :size="16">
    <n-card>
      <n-space>
        <n-select
          v-model:value="filterAppId"
          :options="appOptions"
          clearable
          placeholder="全部应用"
          style="width: 220px"
          @update:value="loadJobs"
        />
        <n-button @click="loadJobs">刷新</n-button>
      </n-space>
    </n-card>

    <n-grid cols="1 s:2 l:4" responsive="screen" :x-gap="16">
      <n-grid-item>
        <n-card><n-statistic label="回放任务数" :value="stats.jobs" /></n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card><n-statistic label="执行用例数" :value="stats.total" /></n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="通过用例数">
            <template #default><span style="color: #18a058">{{ stats.passed }}</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="平均通过率">
            <template #default>
              <span :style="{ color: stats.passRate >= 90 ? '#18a058' : '#d03050' }">{{ stats.passRate.toFixed(1) }}%</span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="回放任务列表">
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
          <n-button size="small" @click="router.push('/replay/history')">回放历史</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="columns"
        :data="jobs"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        :row-key="(row: JobRow) => row.id"
        remote
        v-model:checked-row-keys="selectedJobIds"
        @update:sorter="handleSorterChange"
      />
    </n-card>
  </n-space>

  <n-drawer v-model:show="showDrawer" :width="760" placement="right">
    <n-drawer-content :title="`任务 #${drawerJobId} 结果详情`" closable>
      <n-data-table
        :columns="resultColumns"
        :data="drawerResults"
        :loading="drawerLoading"
        size="small"
        :pagination="{ pageSize: 20 }"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NDataTable, NDrawer, NDrawerContent, NGrid, NGridItem, NPopconfirm, NSpace, NSelect, NStatistic, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import { useUserStore } from '@/store/user'
import { formatDateTime } from '@/utils/format'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'

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
  actual_status_code: number | null
  status: string
  is_pass: boolean
  latency_ms: number | null
  failure_reason: string | null
}

const router = useRouter()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const jobStatusTagType: Record<string, NonNullable<TagProps['type']>> = {
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

const resultStatusTagType: Record<string, NonNullable<TagProps['type']>> = {
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

const message = useMessage()
const filterAppId = ref<number | null>(null)
const jobs = ref<JobRow[]>([])
const loading = ref(false)
const appOptions = ref<SelectOption[]>([])
const selectedJobIds = ref<(string | number)[]>([])
const showDrawer = ref(false)
const drawerJobId = ref<number | null>(null)
const drawerResults = ref<ResultRow[]>([])
const drawerLoading = ref(false)
const stats = reactive({ jobs: 0, total: 0, passed: 0, passRate: 0 })
const sortState = ref(defaultSortState('created_at'))

const columns = computed<DataTableColumns<JobRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const, disabled: (row: JobRow) => ['RUNNING', 'PENDING'].includes(row.status) }] : []),
  { title: 'ID', key: 'id', width: 60 },
  { title: '任务名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(
      NTag,
      { type: jobStatusTagType[row.status] ?? 'default', size: 'small' },
      () => jobStatusLabelMap[row.status] || row.status,
    ),
  },
  {
    title: '通过率',
    key: 'pass_rate',
    width: 100,
    render: (row) => {
      if (!row.total) {
        return '-'
      }
      const rate = (row.passed / row.total) * 100
      return h(
        'span',
        { style: `color:${rate >= 90 ? '#18a058' : '#d03050'};font-weight:bold` },
        `${rate.toFixed(1)}%`,
      )
    },
  },
  { title: '总数/通过/失败/异常', key: 'counts', render: (row) => `${row.total}/${row.passed}/${row.failed}/${row.errored}` },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    sorter: true,
    sortOrder: resolveSortOrder(sortState.value, 'created_at'),
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: canEdit ? 290 : 220,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/results/${row.id}`) }, () => '查看详情'),
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
  { title: '响应码', key: 'actual_status_code', width: 70 },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (row) => h(
      NTag,
      { type: resultStatusTagType[row.status] ?? 'default', size: 'small' },
      () => resultStatusLabelMap[row.status] || row.status,
    ),
  },
  {
    title: '耗时',
    key: 'latency_ms',
    width: 90,
    render: (row) => (row.latency_ms != null ? `${row.latency_ms}ms` : '-'),
  },
  { title: '失败原因', key: 'failure_reason', ellipsis: { tooltip: true } },
]


async function openReport(jobId: number) {
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

async function loadJobs() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { limit: 50 }
    if (filterAppId.value != null) {
      params.application_id = filterAppId.value
    }
    params.sort_by = sortState.value.columnKey
    params.sort_order = toApiSortOrder(sortState.value.order)
    const res = await replayApi.list(params)
    jobs.value = res.data
    selectedJobIds.value = []

    const finishedJobs = res.data.filter((job: JobRow) => job.status === 'DONE' || job.status === 'FAILED')
    stats.jobs = finishedJobs.length
    stats.total = finishedJobs.reduce((acc: number, job: JobRow) => acc + (job.total || 0), 0)
    stats.passed = finishedJobs.reduce((acc: number, job: JobRow) => acc + (job.passed || 0), 0)
    stats.passRate = stats.total > 0 ? (stats.passed / stats.total) * 100 : 0
  } catch (error: any) {
    jobs.value = []
    stats.jobs = 0
    stats.total = 0
    stats.passed = 0
    stats.passRate = 0
    message.error(error.response?.data?.detail || '加载回放结果失败')
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

function handleSorterChange(sorter: any) {
  sortState.value = updateSortState(sorter, 'created_at')
  void loadJobs()
}

async function openDrawer(jobId: number) {
  drawerJobId.value = jobId
  showDrawer.value = true
  drawerLoading.value = true
  try {
    const res = await replayApi.getResults(jobId, { limit: 200 })
    drawerResults.value = res.data
  } catch (error: any) {
    drawerResults.value = []
    message.error(error.response?.data?.detail || '加载任务详情失败')
  } finally {
    drawerLoading.value = false
  }
}

onMounted(async () => {
  try {
    const appsRes = await applicationApi.list()
    appOptions.value = appsRes.data.map((app: { id: number; name: string }) => ({ label: app.name, value: app.id }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载应用列表失败')
  }
  await loadJobs()
})
</script>
