<template>
  <n-space vertical :size="16">
    <n-card title="回放历史">
      <template #header-extra>
        <n-space>
          <n-button @click="loadJobs">刷新</n-button>
          <n-button @click="router.push('/replay')">发起回放</n-button>
        </n-space>
      </template>

      <n-space wrap>
        <n-input
          v-model:value="filterSearch"
          clearable
          placeholder="搜索任务名称或任务 ID"
          style="width: 220px"
          @update:value="loadJobs"
        />
        <n-select
          v-model:value="filterAppId"
          :options="appOptions"
          clearable
          placeholder="全部应用"
          style="width: 220px"
          @update:value="loadJobs"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="全部状态"
          style="width: 160px"
          @update:value="loadJobs"
        />
        <n-date-picker
          v-model:value="dateRange"
          type="datetimerange"
          clearable
          style="width: 360px"
          @update:value="loadJobs"
        />
      </n-space>

      <n-data-table
        style="margin-top: 16px"
        :columns="columns"
        :data="jobs"
        :loading="loading"
        :pagination="{ pageSize: 12 }"
      />
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDataTable,
  NDatePicker,
  NInput,
  NSpace,
  NSelect,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { replayApi } from '@/api/replays'
import { formatDateTime } from '@/utils/format'

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

const jobs = ref<JobRow[]>([])
const loading = ref(false)
const filterSearch = ref('')
const filterAppId = ref<number | null>(null)
const filterStatus = ref<string | null>(null)
const dateRange = ref<[number, number] | null>(null)
const appOptions = ref<SelectOption[]>([])
const appNameMap = ref<Record<number, string>>({})

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
  FAILED: '失败',
  PENDING: '待执行',
  CANCELLED: '已取消',
}

const statusOptions: SelectOption[] = [
  { label: '已完成', value: 'DONE' },
  { label: '运行中', value: 'RUNNING' },
  { label: '失败', value: 'FAILED' },
  { label: '待执行', value: 'PENDING' },
]

const columns: DataTableColumns<JobRow> = [
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
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/results/${row.id}`) }, () => '查看结果'),
        h(NButton, { size: 'tiny', type: 'info', onClick: () => openReport(row.id) }, () => '查看报告'),
      ]),
  },
]

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
    appOptions.value = res.data.map((item: { id: number; name: string }) => ({ label: item.name, value: item.id }))
    appNameMap.value = Object.fromEntries(res.data.map((item: { id: number; name: string }) => [item.id, item.name]))
  } catch (error: any) {
    appOptions.value = []
    appNameMap.value = {}
    message.error(error.response?.data?.detail || '加载应用列表失败')
  }
}

async function loadJobs() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { limit: 100 }
    if (filterSearch.value.trim()) params.search = filterSearch.value.trim()
    if (filterAppId.value != null) params.application_id = filterAppId.value
    if (filterStatus.value) params.status = filterStatus.value
    if (dateRange.value) {
      params.created_after = new Date(dateRange.value[0]).toISOString()
      params.created_before = new Date(dateRange.value[1]).toISOString()
    }
    const res = await replayApi.list(params)
    jobs.value = res.data
  } catch (error: any) {
    jobs.value = []
    message.error(error.response?.data?.detail || '加载回放历史失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadApps()
  await loadJobs()
})
</script>
