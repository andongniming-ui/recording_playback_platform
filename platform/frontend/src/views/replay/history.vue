<template>
  <n-space vertical :size="16">
    <n-card title="回放历史">
      <template #header-extra>
        <n-space>
          <n-button @click="loadJobs">刷新</n-button>
          <n-button
            v-if="canEdit && selectedJobIds.length > 0"
            type="error"
            @click="deleteSelectedJobs"
          >
            批量删除{{ selectedJobIds.length > 0 ? ` (${selectedJobIds.length})` : '' }}
          </n-button>
          <n-button @click="router.push('/replay')">发起回放</n-button>
        </n-space>
      </template>

      <n-space wrap>
        <n-input
          v-model:value="filterSearch"
          clearable
          placeholder="搜索任务名称或任务 ID"
          style="width: 220px"
          @update:value="reloadJobsFromFirstPage"
        />
        <n-select
          v-model:value="filterAppId"
          :options="appOptions"
          clearable
          placeholder="全部应用"
          style="width: 220px"
          @update:value="reloadJobsFromFirstPage"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="全部状态"
          style="width: 160px"
          @update:value="reloadJobsFromFirstPage"
        />
        <n-date-picker
          v-model:value="dateRange"
          type="datetimerange"
          clearable
          style="width: 360px"
          @update:value="reloadJobsFromFirstPage"
        />
      </n-space>

      <n-data-table
        style="margin-top: 16px"
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
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDataTable,
  NDatePicker,
  NInput,
  NPopconfirm,
  NSpace,
  NSelect,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import { useUserStore } from '@/store/user'
import { formatDateTime } from '@/utils/format'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData, unpackPagedResponse } from '@/utils/pagination'

type JobRow = {
  id: number
  name?: string | null
  application_id?: number | null
  status: string
  total: number
  passed: number
  failed: number
  errored: number
  created_at: string
}

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'

const jobs = ref<JobRow[]>([])
const loading = ref(false)
const filterSearch = ref('')
const filterAppId = ref<number | null>(null)
const filterStatus = ref<string | null>(null)
const dateRange = ref<[number, number] | null>(null)
const appOptions = ref<SelectOption[]>([])
const appNameMap = ref<Record<number, string>>({})
const selectedJobIds = ref<(string | number)[]>([])
const sortState = ref(defaultSortState('created_at'))
const pagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
  pageSizes: [12, 24, 50, 100],
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

const statusTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  DONE: 'success',
  RUNNING: 'info',
  FAILED: 'error',
  PENDING: 'default',
  CANCELLED: 'warning',
}

const statusLabelMap: Record<string, string> = {
  DONE: '已完成',
  RUNNING: '运行中',
  FAILED: '存在失败',
  PENDING: '待执行',
  CANCELLED: '已取消',
}

const statusOptions: SelectOption[] = [
  { label: '已完成', value: 'DONE' },
  { label: '运行中', value: 'RUNNING' },
  { label: '存在失败', value: 'FAILED' },
  { label: '待执行', value: 'PENDING' },
]

const columns = computed<DataTableColumns<JobRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const, disabled: (row: JobRow) => ['RUNNING', 'PENDING'].includes(row.status) }] : []),
  { title: 'ID', key: 'id', width: 70 },
  { title: '任务名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '应用',
    key: 'application_id',
    width: 150,
    render: (row) => (row.application_id != null ? (appNameMap.value[row.application_id] || `#${row.application_id}`) : '-'),
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(NTag, { type: statusTypeMap[row.status] ?? 'default', size: 'small' }, () => statusLabelMap[row.status] || row.status),
  },
  {
    title: '通过率',
    key: 'passRate',
    width: 120,
    render: (row) => {
      const total = row.total || 0
      if (!total) return '-'
      const rate = ((row.passed || 0) / total) * 100
      return `${rate.toFixed(1)}%`
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
    width: canEdit ? 250 : 180,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/results/${row.id}`) }, () => '查看结果'),
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

async function loadApps() {
  try {
    const res = await applicationApi.list({ limit: 100 })
    const page = unpackPagedResponse<{ id: number; name: string }>(res.data)
    appOptions.value = page.items.map((item) => ({ label: item.name, value: item.id }))
    appNameMap.value = Object.fromEntries(page.items.map((item) => [item.id, item.name]))
  } catch (error: any) {
    appOptions.value = []
    appNameMap.value = {}
    message.error(error.response?.data?.detail || '加载应用列表失败')
  }
}

async function loadJobs() {
  loading.value = true
  try {
    const params: Record<string, string | number | boolean> = {}
    if (filterSearch.value.trim()) params.search = filterSearch.value.trim()
    if (filterAppId.value != null) params.application_id = filterAppId.value
    if (filterStatus.value) params.status = filterStatus.value
    if (dateRange.value) {
      params.created_after = new Date(dateRange.value[0]).toISOString()
      params.created_before = new Date(dateRange.value[1]).toISOString()
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
  } catch (error: any) {
    jobs.value = []
    pagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载回放历史失败')
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

onMounted(async () => {
  await loadApps()
  await loadJobs()
})
</script>
