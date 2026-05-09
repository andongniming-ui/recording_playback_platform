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
          @update:value="reloadJobsFromFirstPage"
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
          <n-button size="small" @click="router.push('/replay/history')">回放任务</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="columns"
        :data="jobs"
        :loading="loading"
        :pagination="pagination"
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
        :pagination="drawerPagination"
        remote
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
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 个任务`,
  onUpdatePage: (page: number) => {
    pagination.page = page
    void loadJobs()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    void loadJobs()
  },
})
const drawerPagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  pageSizes: [20, 50, 100, 200],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条结果`,
  onUpdatePage: (page: number) => {
    drawerPagination.page = page
    if (drawerJobId.value != null) {
      void loadDrawerResults(drawerJobId.value)
    }
  },
  onUpdatePageSize: (pageSize: number) => {
    drawerPagination.pageSize = pageSize
    drawerPagination.page = 1
    if (drawerJobId.value != null) {
      void loadDrawerResults(drawerJobId.value)
    }
  },
})

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
    const params: Record<string, string | number | boolean> = {}
    if (filterAppId.value != null) {
      params.application_id = filterAppId.value
    }
    params.sort_by = sortState.value.columnKey
    params.sort_order = toApiSortOrder(sortState.value.order)
    const page = await loadPagedData<JobRow>(replayApi.list, params, pagination.page, pagination.pageSize, 100)
    jobs.value = page.items
    pagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && pagination.page > 1) {
      pagination.page = lastValidPage(page.total, pagination.pageSize)
      void loadJobs()
      return
    }
    selectedJobIds.value = []

    const finishedJobs = page.items.filter((job: JobRow) => job.status === 'DONE' || job.status === 'FAILED')
    stats.jobs = finishedJobs.length
    stats.total = finishedJobs.reduce((acc: number, job: JobRow) => acc + (job.total || 0), 0)
    stats.passed = finishedJobs.reduce((acc: number, job: JobRow) => acc + (job.passed || 0), 0)
    stats.passRate = stats.total > 0 ? (stats.passed / stats.total) * 100 : 0
  } catch (error: any) {
    jobs.value = []
    pagination.itemCount = 0
    stats.jobs = 0
    stats.total = 0
    stats.passed = 0
    stats.passRate = 0
    message.error(error.response?.data?.detail || '加载回放结果失败')
  } finally {
    loading.value = false
  }
}

function reloadJobsFromFirstPage() {
  pagination.page = 1
  void loadJobs()
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
  pagination.page = 1
  void loadJobs()
}

async function openDrawer(jobId: number) {
  drawerJobId.value = jobId
  showDrawer.value = true
  drawerPagination.page = 1
  await loadDrawerResults(jobId)
}

async function loadDrawerResults(jobId: number) {
  drawerLoading.value = true
  try {
    const page = await loadPagedData<ResultRow>(
      (params) => replayApi.getResults(jobId, params),
      {},
      drawerPagination.page,
      drawerPagination.pageSize,
      200,
    )
    drawerResults.value = page.items
    drawerPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && drawerPagination.page > 1) {
      drawerPagination.page = lastValidPage(page.total, drawerPagination.pageSize)
      void loadDrawerResults(jobId)
    }
  } catch (error: any) {
    drawerResults.value = []
    drawerPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载任务详情失败')
  } finally {
    drawerLoading.value = false
  }
}

onMounted(async () => {
  try {
    const appsRes = await applicationApi.list({ limit: 100 })
    const page = unpackPagedResponse<{ id: number; name: string }>(appsRes.data)
    appOptions.value = page.items.map((app) => ({ label: app.name, value: app.id }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载应用列表失败')
  }
  await loadJobs()
})
</script>
