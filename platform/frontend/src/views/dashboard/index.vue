<template>
  <n-space vertical :size="16">
    <n-card title="快捷入口">
      <n-space wrap>
        <n-button type="primary" @click="router.push('/applications')">应用管理</n-button>
        <n-button @click="router.push('/recording')">录制中心</n-button>
        <n-button @click="router.push('/testcases')">测试用例</n-button>
        <n-button @click="router.push('/replay')">发起回放</n-button>
        <n-button @click="router.push('/replay/history')">回放历史</n-button>
        <n-button @click="router.push('/results')">执行结果</n-button>
      </n-space>
    </n-card>

    <!-- 统计卡片 -->
    <n-grid cols="1 s:2 l:4" responsive="screen" :x-gap="16">
      <n-grid-item>
        <n-card>
          <n-statistic label="应用数量" :value="summary?.apps || 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="测试用例" :value="summary?.test_cases || 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="近期任务(30天)" :value="summary?.recent_jobs || 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="平均通过率">
            <template #default>
              <span :style="{ color: passRateColor }">
                {{ summary?.avg_pass_rate != null ? (summary.avg_pass_rate * 100).toFixed(1) + '%' : '-' }}
              </span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 趋势图 + 饼图 -->
    <n-grid cols="1 l:2" responsive="screen" :x-gap="16">
      <n-grid-item :span="1">
        <n-card title="通过率趋势">
          <template #header-extra>
            <n-select
              v-model:value="days"
              :options="dayOptions"
              size="small"
              style="width:110px"
              @update:value="loadTrend"
            />
          </template>
          <v-chart :option="trendChartOption" style="height:280px" autoresize :loading="trendLoading" />
        </n-card>
      </n-grid-item>
      <n-grid-item :span="1">
        <n-card title="失败类型分布">
          <v-chart :option="pieChartOption" style="height:280px" autoresize :loading="failLoading" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 最近回放任务 -->
    <n-card title="最近回放任务">
      <n-data-table
        :columns="jobColumns"
        :data="recentJobs"
        :pagination="{ pageSize: 5 }"
        size="small"
      />
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton, NSpace, NGrid, NGridItem, NCard, NStatistic, NSelect, NDataTable, NTag, useMessage
} from 'naive-ui'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { statsApi } from '@/api/stats'
import { formatDateTime } from '@/utils/format'

use([CanvasRenderer, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const router = useRouter()
const message = useMessage()
const summary = ref<any>(null)
const trend = ref<any[]>([])
const failureTypes = ref<any[]>([])
const recentJobs = ref<any[]>([])
const days = ref(7)
const trendLoading = ref(false)
const failLoading = ref(false)

const dayOptions = [
  { label: '近7天', value: 7 },
  { label: '近14天', value: 14 },
  { label: '近30天', value: 30 },
]

const passRateColor = computed(() => {
  const r = summary.value?.avg_pass_rate
  if (r == null) return '#333'
  return r >= 0.9 ? '#18a058' : '#d03050'
})

const trendChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 30, bottom: 50 },
  xAxis: {
    type: 'category',
    data: trend.value.map(p => (p.date ?? '').slice(5)),
    axisLabel: { rotate: 45 },
  },
  yAxis: { type: 'value', name: '通过率(%)', min: 0, max: 100 },
  series: [{
    name: '通过率',
    type: 'line',
    data: trend.value.map(p => p.pass_rate != null ? +(p.pass_rate * 100).toFixed(1) : null),
    smooth: true,
    itemStyle: { color: '#18a058' },
    areaStyle: { color: 'rgba(24,160,88,0.1)' },
    connectNulls: true,
  }],
}))

const pieChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: failureTypes.value.map(f => ({ name: f.category || '未知', value: f.count })),
    label: { formatter: '{b}: {c}' },
  }],
}))

const jobColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '任务名', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态', key: 'status', width: 90,
    render: (r: any) => h(NTag, {
      type: r.status === 'DONE' ? 'success' : r.status === 'RUNNING' ? 'info' : 'error',
      size: 'small',
    }, () => r.status),
  },
  { title: '总数', key: 'total', width: 70 },
  {
    title: '通过率', key: 'pass_rate', width: 90,
    render: (r: any) => r.pass_rate != null
      ? h('span', { style: `color:${r.pass_rate >= 0.9 ? '#18a058' : '#d03050'}` },
          `${(r.pass_rate * 100).toFixed(1)}%`)
      : '-',
  },
  {
    title: '时间', key: 'created_at', width: 150,
    render: (r: any) => formatDateTime(r.created_at),
  },
  {
    title: '操作', key: 'actions', width: 100,
    render: (r: any) => h(NButton, { size: 'tiny', onClick: () => router.push(`/results/${r.id}`) }, () => '查看'),
  },
]

async function loadTrend() {
  trendLoading.value = true
  try {
    const res = await statsApi.trend({ days: days.value })
    trend.value = res.data
  } catch (error: any) {
    trend.value = []
    message.error(error.response?.data?.detail || '加载通过率趋势失败')
  } finally {
    trendLoading.value = false
  }
}

onMounted(async () => {
  failLoading.value = true
  try {
    const [sumRes, jobsRes, failRes] = await Promise.all([
      statsApi.summary(),
      statsApi.recentJobs({ limit: 10 }),
      statsApi.failureTypes({ days: 30 }),
    ])
    summary.value = sumRes.data
    recentJobs.value = jobsRes.data
    failureTypes.value = failRes.data
  } catch (error: any) {
    summary.value = null
    recentJobs.value = []
    failureTypes.value = []
    message.error(error.response?.data?.detail || '加载仪表盘统计失败')
  } finally {
    failLoading.value = false
  }
  await loadTrend()
})
</script>
