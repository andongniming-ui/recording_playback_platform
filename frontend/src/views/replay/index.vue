<template>
  <n-space vertical :size="16">
    <n-card title="发起回放">
      <n-form :model="launchForm" label-placement="left" label-width="100px">
        <n-form-item label="关联应用">
          <n-select v-model:value="launchForm.application_id" :options="appOptions" clearable placeholder="可选" style="width:280px" />
        </n-form-item>
        <n-form-item label="选择用例">
          <n-select
            v-model:value="launchForm.case_ids"
            multiple
            filterable
            :options="caseOptions"
            placeholder="请选择测试用例（可多选）"
            style="width:100%"
          />
        </n-form-item>
        <n-form-item label="并发数">
          <n-input-number v-model:value="launchForm.concurrency" :min="1" :max="50" />
        </n-form-item>
        <n-form-item label="超时(ms)">
          <n-input-number v-model:value="launchForm.timeout_ms" :min="500" :max="60000" :step="500" />
        </n-form-item>
        <n-form-item label="任务名称">
          <n-input v-model:value="launchForm.name" placeholder="可选" style="width:280px" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" :loading="launching" :disabled="!launchForm.case_ids.length" @click="launchReplay">
            开始回放
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="回放任务历史">
      <template #header-extra>
        <n-button size="small" @click="loadJobs">刷新</n-button>
      </template>
      <n-data-table :columns="jobColumns" :data="jobs" :loading="loading" :pagination="{ pageSize: 10 }" />
    </n-card>
  </n-space>

  <!-- 结果详情抽屉 -->
  <n-drawer v-model:show="showDrawer" :width="700" placement="right">
    <n-drawer-content :title="`回放结果 - Job #${selectedJobId}`" closable>
      <n-space style="margin-bottom:12px">
        <n-select v-model:value="resultFilter" :options="resultFilterOpts" clearable placeholder="状态过滤" style="width:150px" @update:value="loadResults" />
      </n-space>
      <n-data-table :columns="resultColumns" :data="results" :loading="resultsLoading" :pagination="{ pageSize: 20 }" size="small" />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import {
  NSpace, NCard, NForm, NFormItem, NSelect, NInputNumber, NInput, NButton,
  NDataTable, NTag, NDrawer, NDrawerContent, useMessage
} from 'naive-ui'
import { replayApi } from '@/api/replays'
import { applicationApi } from '@/api/applications'
import { testCaseApi } from '@/api/testcases'

const message = useMessage()
const jobs = ref<any[]>([])
const loading = ref(false)
const launching = ref(false)
const showDrawer = ref(false)
const selectedJobId = ref<number | null>(null)
const results = ref<any[]>([])
const resultsLoading = ref(false)
const resultFilter = ref<string | null>(null)
const appOptions = ref<any[]>([])
const caseOptions = ref<any[]>([])

const launchForm = ref({
  name: '',
  application_id: null as number | null,
  case_ids: [] as number[],
  concurrency: 5,
  timeout_ms: 5000,
})

const resultFilterOpts = [
  { label: '全部', value: null },
  { label: '通过', value: 'PASS' },
  { label: '失败', value: 'FAIL' },
  { label: '错误', value: 'ERROR' },
]

const jobColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态', key: 'status', width: 90,
    render: (r: any) => h(NTag, { type: { DONE: 'success', RUNNING: 'info', FAILED: 'error', PENDING: 'default' }[r.status as string] || 'default', size: 'small' }, () => r.status),
  },
  {
    title: '进度', key: 'progress', width: 120,
    render: (r: any) => r.total ? `${r.passed}/${r.total} (${((r.passed / r.total) * 100).toFixed(0)}%)` : '-',
  },
  { title: '失败', key: 'failed', width: 60, render: (r: any) => h('span', { style: r.failed > 0 ? 'color:#d03050' : '' }, r.failed || 0) },
  { title: '创建时间', key: 'created_at', width: 160, render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' ') },
  {
    title: '操作', key: 'actions', width: 160,
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => openDrawer(r.id) }, () => '查看结果'),
      h(NButton, { size: 'tiny', type: 'info', onClick: () => window.open(`/api/v1/replays/${r.id}/report`, '_blank') }, () => '报告'),
    ]),
  },
]

const resultColumns = [
  { title: 'URI', key: 'request_uri', ellipsis: { tooltip: true } },
  {
    title: '状态', key: 'status', width: 80,
    render: (r: any) => h(NTag, { type: r.status === 'PASS' ? 'success' : r.status === 'FAIL' ? 'error' : 'warning', size: 'small' }, () => r.status),
  },
  { title: 'HTTP', key: 'actual_status_code', width: 60 },
  { title: '延迟', key: 'latency_ms', width: 70, render: (r: any) => r.latency_ms ? `${r.latency_ms}ms` : '-' },
  { title: '失败原因', key: 'failure_reason', ellipsis: { tooltip: true } },
]

async function loadJobs() {
  loading.value = true
  try {
    const res = await replayApi.list()
    jobs.value = res.data
  } finally { loading.value = false }
}

async function openDrawer(jobId: number) {
  selectedJobId.value = jobId
  showDrawer.value = true
  await loadResults()
}

async function loadResults() {
  if (!selectedJobId.value) return
  resultsLoading.value = true
  try {
    const params: any = { limit: 100 }
    if (resultFilter.value) params.status = resultFilter.value
    const res = await replayApi.getResults(selectedJobId.value, params)
    results.value = res.data
  } finally { resultsLoading.value = false }
}

async function launchReplay() {
  launching.value = true
  try {
    const res = await replayApi.create(launchForm.value)
    message.success(`回放任务 #${res.data.id} 已启动`)
    launchForm.value.case_ids = []
    launchForm.value.name = ''
    await loadJobs()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '启动失败')
  } finally { launching.value = false }
}

onMounted(async () => {
  const [appsRes, casesRes] = await Promise.all([
    applicationApi.list(),
    testCaseApi.list({ limit: 100, status: 'active' }),
  ])
  appOptions.value = appsRes.data.map((a: any) => ({ label: a.name, value: a.id }))
  caseOptions.value = casesRes.data.map((c: any) => ({ label: `[${c.request_method}] ${c.request_uri} - ${c.name}`, value: c.id }))
  await loadJobs()
})
</script>
