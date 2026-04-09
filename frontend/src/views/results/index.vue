<template>
  <n-space vertical :size="16">
    <!-- 过滤 -->
    <n-card>
      <n-space>
        <n-select v-model:value="filterAppId" :options="appOptions" clearable placeholder="全部应用" style="width:200px" @update:value="loadJobs" />
        <n-button @click="loadJobs">刷新</n-button>
      </n-space>
    </n-card>

    <!-- 汇总卡片 -->
    <n-grid :cols="4" :x-gap="16">
      <n-grid-item>
        <n-card><n-statistic label="回放任务(近30天)" :value="stats.jobs" /></n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card><n-statistic label="总用例执行" :value="stats.total" /></n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="通过用例">
            <template #default><span style="color:#18a058">{{ stats.passed }}</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="平均通过率">
            <template #default>
              <span :style="{color: stats.passRate >= 90 ? '#18a058' : '#d03050'}">{{ stats.passRate.toFixed(1) }}%</span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 任务列表 -->
    <n-card title="回放任务列表">
      <n-data-table
        :columns="columns"
        :data="jobs"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
      />
    </n-card>
  </n-space>

  <!-- 结果详情抽屉 -->
  <n-drawer v-model:show="showDrawer" :width="720" placement="right">
    <n-drawer-content :title="`Job #${drawerJobId} 结果详情`" closable>
      <n-data-table :columns="resultCols" :data="drawerResults" :loading="drawerLoading" size="small" :pagination="{ pageSize: 20 }" />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { NSpace, NCard, NSelect, NButton, NGrid, NGridItem, NStatistic, NDataTable, NTag, NDrawer, NDrawerContent } from 'naive-ui'
import { replayApi } from '@/api/replays'
import { applicationApi } from '@/api/applications'

const filterAppId = ref<number | null>(null)
const jobs = ref<any[]>([])
const loading = ref(false)
const appOptions = ref<any[]>([])
const showDrawer = ref(false)
const drawerJobId = ref<number | null>(null)
const drawerResults = ref<any[]>([])
const drawerLoading = ref(false)
const stats = reactive({ jobs: 0, total: 0, passed: 0, passRate: 0 })

const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态', key: 'status', width: 90,
    render: (r: any) => h(NTag, { type: { DONE: 'success', RUNNING: 'info', FAILED: 'error' }[r.status as string] || 'default', size: 'small' }, () => r.status),
  },
  {
    title: '通过率', key: 'pass_rate', width: 90,
    render: (r: any) => {
      if (!r.total) return '-'
      const rate = (r.passed / r.total * 100).toFixed(1)
      return h('span', { style: `color:${r.passed / r.total >= 0.9 ? '#18a058' : '#d03050'};font-weight:bold` }, `${rate}%`)
    },
  },
  { title: '总/通过/失败', key: 'counts', render: (r: any) => `${r.total}/${r.passed}/${r.failed}` },
  { title: '时间', key: 'created_at', width: 155, render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' ') },
  {
    title: '操作', key: 'actions', width: 160,
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => openDrawer(r.id) }, () => '查看详情'),
      h(NButton, { size: 'tiny', type: 'info', onClick: () => window.open(`/api/v1/replays/${r.id}/report`, '_blank') }, () => 'HTML报告'),
    ]),
  },
]

const resultCols = [
  { title: '用例URI', key: 'request_uri', ellipsis: { tooltip: true } },
  { title: 'HTTP', key: 'actual_status_code', width: 60 },
  {
    title: '结果', key: 'status', width: 80,
    render: (r: any) => h(NTag, { type: r.is_pass ? 'success' : 'error', size: 'small' }, () => r.status),
  },
  { title: '延迟', key: 'latency_ms', width: 70, render: (r: any) => r.latency_ms ? `${r.latency_ms}ms` : '-' },
  { title: '失败原因', key: 'failure_reason', ellipsis: { tooltip: true } },
]

async function loadJobs() {
  loading.value = true
  try {
    const params: any = { limit: 50 }
    if (filterAppId.value) params.application_id = filterAppId.value
    const res = await replayApi.list(params)
    jobs.value = res.data
    // Compute stats
    const done = res.data.filter((j: any) => j.status === 'DONE')
    stats.jobs = done.length
    stats.total = done.reduce((a: number, j: any) => a + (j.total || 0), 0)
    stats.passed = done.reduce((a: number, j: any) => a + (j.passed || 0), 0)
    stats.passRate = stats.total > 0 ? (stats.passed / stats.total * 100) : 0
  } finally { loading.value = false }
}

async function openDrawer(jobId: number) {
  drawerJobId.value = jobId
  showDrawer.value = true
  drawerLoading.value = true
  try {
    const res = await replayApi.getResults(jobId, { limit: 200 })
    drawerResults.value = res.data
  } finally { drawerLoading.value = false }
}

onMounted(async () => {
  const appsRes = await applicationApi.list()
  appOptions.value = appsRes.data.map((a: any) => ({ label: a.name, value: a.id }))
  await loadJobs()
})
</script>
