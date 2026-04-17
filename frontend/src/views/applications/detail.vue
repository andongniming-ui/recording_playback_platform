<template>
  <n-space vertical :size="16" class="application-detail-page">
    <n-space justify="space-between" align="center" class="page-toolbar">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/applications')">应用管理</n-breadcrumb-item>
        <n-breadcrumb-item>{{ app?.name || `应用 #${appId}` }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button @click="router.push(`/recording?application_id=${appId}`)">查看录制</n-button>
        <n-button @click="router.push(`/replay?application_id=${appId}`)">发起回放</n-button>
        <n-button v-if="canEdit" type="primary" @click="quickCreateSession" :loading="creatingSession">+ 新建会话</n-button>
      </n-space>
    </n-space>

    <div v-if="app" class="detail-stack">
      <n-grid :cols="4" :x-gap="12" :y-gap="12">
        <n-grid-item>
          <n-card>
            <n-statistic label="最近会话数" :value="sessions.length" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="已完成会话">
              <template #default>
                <span style="color:#18a058">{{ doneCount }}</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="异常会话">
              <template #default>
                <span style="color:#d03050">{{ errorCount }}</span>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card>
            <n-statistic label="最新回放任务" :value="replayJobs.length" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <n-card title="应用概览">
        <template #header-extra>
          <n-space>
            <n-tag :type="statusTypeMap[normalizedStatus] || 'default'">
              {{ statusLabelMap[normalizedStatus] || '未知' }}
            </n-tag>
            <n-button v-if="canEdit" size="small" @click="testConnection" :loading="testing">测试连接</n-button>
            <n-button
              v-if="canEdit && normalizedStatus !== 'online'"
              size="small"
              type="primary"
              @click="mountAgent"
              :loading="mounting"
            >
              挂载 Agent
            </n-button>
            <n-button
              v-if="canEdit && normalizedStatus === 'online'"
              size="small"
              type="warning"
              @click="unmountAgent"
              :loading="unmounting"
            >
              卸载 Agent
            </n-button>
          </n-space>
        </template>
        <n-descriptions bordered :column="2" label-placement="left">
          <n-descriptions-item label="应用名称">{{ app.name }}</n-descriptions-item>
          <n-descriptions-item label="描述">{{ app.description || '-' }}</n-descriptions-item>
          <n-descriptions-item label="采样率">{{ app.sample_rate ?? '-' }}</n-descriptions-item>
          <n-descriptions-item label="创建时间">{{ formatDateTime(app.created_at) }}</n-descriptions-item>
        </n-descriptions>
      </n-card>

      <n-card title="接入信息">
        <n-descriptions bordered :column="2" label-placement="left">
          <n-descriptions-item label="宿主机">{{ app.ssh_user }}@{{ app.ssh_host }}:{{ app.ssh_port }}</n-descriptions-item>
          <n-descriptions-item label="服务端口">{{ app.service_port }}</n-descriptions-item>
        </n-descriptions>
        <n-collapse arrow-placement="right" style="margin-top: 12px">
          <n-collapse-item title="更多接入信息" name="more-access">
            <n-descriptions bordered :column="2" label-placement="left">
              <n-descriptions-item label="启动模式">{{ launchModeLabel }}</n-descriptions-item>
              <n-descriptions-item label="JVM 进程名">{{ app.jvm_process_name || '-' }}</n-descriptions-item>
              <n-descriptions-item label="AREX App ID">{{ app.arex_app_id || app.name }}</n-descriptions-item>
              <n-descriptions-item label="AREX Storage">{{ app.arex_storage_url || '使用全局配置' }}</n-descriptions-item>
              <n-descriptions-item label="Docker 工作目录">{{ app.docker_workdir || '-' }}</n-descriptions-item>
              <n-descriptions-item label="Compose 文件">{{ app.docker_compose_file || 'docker-compose.yml' }}</n-descriptions-item>
              <n-descriptions-item label="Compose 服务名">{{ app.docker_service_name || '-' }}</n-descriptions-item>
              <n-descriptions-item label="Docker Storage">{{ app.docker_storage_url || '使用平台默认 Docker storage URL' }}</n-descriptions-item>
              <n-descriptions-item label="Agent 挂载路径">{{ app.docker_agent_path || '/opt/arex/arex-agent.jar' }}</n-descriptions-item>
              <n-descriptions-item label="Agent 状态">{{ statusLabelMap[normalizedStatus] || '未知' }}</n-descriptions-item>
            </n-descriptions>
          </n-collapse-item>
          <n-collapse-item title="交易码映射" name="tx-mappings">
            <n-space vertical :size="12">
              <n-alert type="info" :show-icon="false">
                回放时会按当前应用配置自动加载这份交易码映射。每个交易码一组规则，主要用于 SAT -> UAT 的字段适配。
                字段路径支持 <code>name</code>、<code>customer.name</code>、<code>items.0.name</code>、<code>*.name</code> 这种写法。
              </n-alert>
              <n-alert type="warning" :show-icon="false">
                规则类型支持 <code>rename</code>、<code>delete</code>、<code>default</code>、<code>set</code>、<code>copy</code>。
                如果映射规则比较多，建议直接参考 <code>docs/交易码映射模板.md</code> 的示例模板再填写。
              </n-alert>
              <div class="mapping-preview">
                <pre>{{ mappingPreview }}</pre>
              </div>
            </n-space>
          </n-collapse-item>
        </n-collapse>
        <n-alert type="info" :show-icon="false" style="margin-top: 16px">
          录制数据由目标 JVM 中的 AREX Agent 采集后同步到平台，页面仅展示已同步结果。
        </n-alert>
      </n-card>

      <n-card v-if="app.launch_mode === 'docker_compose'" title="Docker 启动模板">
        <n-space vertical :size="12">
          <n-alert type="info" :show-icon="false">
            这个模板由平台生成，目标容器只需要接受标准 Compose 约定，不需要修改业务代码或 start.sh。
          </n-alert>
          <div class="mapping-preview">
            <pre>{{ dockerTemplatePreview }}</pre>
          </div>
        </n-space>
      </n-card>

      <n-card title="快捷操作">
        <n-grid :cols="3" :x-gap="12" :y-gap="12">
          <n-grid-item>
            <n-button block @click="router.push(`/recording?application_id=${appId}`)">进入录制中心</n-button>
          </n-grid-item>
          <n-grid-item>
            <n-button block @click="router.push(`/replay?application_id=${appId}`)">发起回放</n-button>
          </n-grid-item>
          <n-grid-item>
            <n-button block v-if="canEdit" type="primary" @click="quickCreateSession" :loading="creatingSession">
              新建会话
            </n-button>
          </n-grid-item>
          <n-grid-item>
            <n-button block @click="router.push('/replay/history')">查看回放历史</n-button>
          </n-grid-item>
          <n-grid-item>
            <n-button block @click="router.push(`/testcases?application_id=${appId}`)">查看测试用例</n-button>
          </n-grid-item>
          <n-grid-item>
            <n-button block @click="loadPage">刷新当前页</n-button>
          </n-grid-item>
        </n-grid>
      </n-card>

      <n-tabs v-model:value="recentTab" type="line" animated>
        <n-tab-pane name="sessions" tab="最近录制会话">
          <n-card>
            <template #header-extra>
              <n-button size="small" @click="router.push(`/recording?application_id=${appId}`)">进入录制中心</n-button>
            </template>
            <n-data-table
              :columns="sessionColumns"
              :data="sessions"
              :loading="sessionsLoading"
              :pagination="{ pageSize: 8 }"
            />
          </n-card>
        </n-tab-pane>
        <n-tab-pane name="cases" tab="最近测试用例">
          <n-card>
            <template #header-extra>
              <n-button size="small" @click="router.push(`/testcases?application_id=${appId}`)">全部用例</n-button>
            </template>
            <n-data-table
              :columns="caseColumns"
              :data="testCases"
              :loading="casesLoading"
              :pagination="{ pageSize: 6 }"
            />
          </n-card>
        </n-tab-pane>
        <n-tab-pane name="replays" tab="最近回放任务">
          <n-card>
            <template #header-extra>
              <n-button size="small" @click="router.push('/replay/history')">回放历史</n-button>
            </template>
            <n-data-table
              :columns="jobColumns"
              :data="replayJobs"
              :loading="jobsLoading"
              :pagination="{ pageSize: 6 }"
            />
          </n-card>
        </n-tab-pane>
      </n-tabs>
    </div>
  </n-space>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NAlert,
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NCollapse,
  NCollapseItem,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NGrid,
  NGridItem,
  NSpace,
  NStatistic,
  NTabPane,
  NTabs,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { recordingApi } from '@/api/recordings'
import { replayApi } from '@/api/replays'
import { testCaseApi } from '@/api/testcases'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'

type ApplicationDetail = {
  id: number
  name: string
  description?: string | null
  ssh_host: string
  ssh_user: string
  ssh_port: number
  launch_mode?: 'ssh_script' | 'docker_compose' | string | null
  docker_workdir?: string | null
  docker_compose_file?: string | null
  docker_service_name?: string | null
  docker_storage_url?: string | null
  docker_agent_path?: string | null
  service_port: number
  jvm_process_name?: string | null
  arex_app_id?: string | null
  arex_storage_url?: string | null
  sample_rate?: number
  agent_status?: string | null
  transaction_mappings?: Array<Record<string, unknown>> | null
  created_at?: string
}

type SessionRow = {
  id: number
  name: string
  status: string
  total_count: number
  error_message?: string | null
  created_at: string
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const appId = Number(route.params.id)

const app = ref<ApplicationDetail | null>(null)
const sessions = ref<SessionRow[]>([])
const testCases = ref<any[]>([])
const replayJobs = ref<any[]>([])
const recentTab = ref('sessions')
const sessionsLoading = ref(false)
const casesLoading = ref(false)
const jobsLoading = ref(false)
const testing = ref(false)
const mounting = ref(false)
const unmounting = ref(false)
const creatingSession = ref(false)

const statusTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  online: 'success',
  offline: 'error',
  mounting: 'warning',
  error: 'error',
  unknown: 'default',
}

const statusLabelMap: Record<string, string> = {
  online: '已挂载',
  offline: '未挂载',
  mounting: '挂载中',
  error: '挂载失败',
  unknown: '未知',
}

const launchModeLabelMap: Record<string, string> = {
  ssh_script: '宿主机脚本',
  docker_compose: 'Docker Compose',
}

const normalizedStatus = computed(() => {
  const value = (app.value?.agent_status || 'unknown').toLowerCase()
  if (value === 'attached' || value === 'online' || value === 'already_injected') return 'online'
  if (value === 'detached' || value === 'offline') return 'offline'
  if (value === 'mounting') return 'mounting'
  if (value === 'error') return 'error'
  return 'unknown'
})

const launchModeLabel = computed(() => {
  const value = (app.value?.launch_mode || 'ssh_script').toLowerCase()
  return launchModeLabelMap[value] || value
})

const mappingPreview = computed(() => {
  if (!app.value?.transaction_mappings || !Array.isArray(app.value.transaction_mappings) || app.value.transaction_mappings.length === 0) {
    return '暂无交易码映射配置'
  }
  return JSON.stringify(app.value.transaction_mappings, null, 2)
})

const DEFAULT_DOCKER_STORAGE_PORT = '8093'

function parseStorageHostPort(rawUrl: string | undefined | null): { host: string; port: string } {
  const fallback = { host: 'host.docker.internal', port: DEFAULT_DOCKER_STORAGE_PORT }
  const raw = (rawUrl || '').trim()
  if (!raw) return fallback

  try {
    const normalized = /^https?:\/\//i.test(raw) ? raw : `http://${raw}`
    const url = new URL(normalized)
    return {
      host: url.hostname || fallback.host,
      port: url.port || DEFAULT_DOCKER_STORAGE_PORT,
    }
  } catch {
    const stripped = raw.replace(/^https?:\/\//i, '')
    const [hostPart, portPart] = stripped.split(':')
    return {
      host: hostPart || fallback.host,
      port: portPart || DEFAULT_DOCKER_STORAGE_PORT,
    }
  }
}

const dockerTemplatePreview = computed(() => {
  if (!app.value || (app.value.launch_mode || 'ssh_script').toLowerCase() !== 'docker_compose') {
    return '当前应用不是 Docker Compose 模式。'
  }
  const serviceName = app.value.docker_service_name || app.value.name
  const workdir = app.value.docker_workdir || '.'
  const composeFile = app.value.docker_compose_file || 'docker-compose.yml'
  const agentHostPath = `${workdir.replace(/\/$/, '')}/.arex-recorder/arex-agent.jar`
  const agentPath = app.value.docker_agent_path || '/opt/arex/arex-agent.jar'
  const { host: storageHost, port: storagePort } = parseStorageHostPort(
    app.value.docker_storage_url || 'http://host.docker.internal:8093',
  )
  const serviceNameSafe = serviceName
  const appIdSafe = app.value.arex_app_id || app.value.name
  const sampleRate = Math.max(0, Math.min(100, Math.round((app.value.sample_rate ?? 1) * 100)))
  return [
    '# Docker Compose AREX 启动模板',
    `workdir: ${workdir}`,
    `compose_file: ${composeFile}`,
    `service_name: ${serviceNameSafe}`,
    '',
    'override:',
    '  services:',
    `    ${serviceNameSafe}:`,
    '      extra_hosts:',
    '        - "host.docker.internal:host-gateway"',
    '      environment:',
    `        JAVA_TOOL_OPTIONS: "-javaagent:${agentPath} -Darex.service.name=${appIdSafe} -Darex.storage.service.host=${storageHost} -Darex.storage.service.port=${storagePort} -Darex.record.rate=${sampleRate}"`,
    '      volumes:',
    `        - "${agentHostPath}:${agentPath}:ro"`,
    '',
    'platform command:',
    `  cd ${workdir} && docker compose -f ${composeFile} -f .arex-recorder/docker-compose.arex.override.yml up -d --force-recreate ${serviceNameSafe}`,
  ].join('\n')
})

const doneCount = computed(() => sessions.value.filter((item) => item.status === 'done').length)
const errorCount = computed(() => sessions.value.filter((item) => item.status === 'error').length)

const sessionStatusTagType: Record<string, NonNullable<TagProps['type']>> = {
  idle: 'default',
  active: 'info',
  collecting: 'warning',
  done: 'success',
  error: 'error',
}

const sessionStatusLabelMap: Record<string, string> = {
  idle: '待开始',
  active: '录制中',
  collecting: '收集中',
  done: '已完成',
  error: '异常',
}

const sessionColumns: DataTableColumns<SessionRow> = [
  { title: '会话名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) =>
      h(
        NTag,
        { type: sessionStatusTagType[row.status] ?? 'default', size: 'small' },
        () => sessionStatusLabelMap[row.status] || row.status,
      ),
  },
  { title: '录制数', key: 'total_count', width: 90 },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/sessions/${row.id}`) }, () => '查看详情'),
        ...(canEdit && row.status === 'idle'
          ? [h(NButton, { size: 'tiny', type: 'primary', onClick: () => startSession(row.id) }, () => '开始录制')]
          : []),
        ...(canEdit && row.status === 'active'
          ? [h(NButton, { size: 'tiny', type: 'warning', onClick: () => stopSession(row.id) }, () => '停止录制')]
          : []),
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording?application_id=${appId}`) }, () => '全部会话'),
      ]),
  },
]

const caseColumns: DataTableColumns<any> = [
  {
    title: '名称',
    key: 'name',
    render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => router.push(`/testcases/${row.id}`) }, () => row.name),
  },
  {
    title: '请求',
    key: 'request_uri',
    render: (row) => h('span', [h('b', { style: 'margin-right:4px' }, row.request_method || 'GET'), row.request_uri || '-']),
  },
  { title: '状态', key: 'status', width: 90 },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/testcases/${row.id}`) }, () => '详情'),
        ...(canEdit
          ? [h(NButton, { size: 'tiny', type: 'primary', onClick: () => router.push(`/replay?application_id=${appId}&case_id=${row.id}`) }, () => '回放')]
          : []),
      ]),
  },
]

const jobStatusTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  DONE: 'success',
  RUNNING: 'info',
  FAILED: 'error',
  PENDING: 'default',
  CANCELLED: 'warning',
}

const jobStatusLabelMap: Record<string, string> = {
  DONE: '已完成',
  RUNNING: '运行中',
  FAILED: '失败',
  PENDING: '待执行',
  CANCELLED: '已取消',
}

const jobColumns: DataTableColumns<any> = [
  {
    title: '任务名称',
    key: 'name',
    render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => router.push(`/results/${row.id}`) }, () => row.name || `任务 #${row.id}`),
  },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (row) =>
      h(
        NTag,
        { type: jobStatusTypeMap[row.status] ?? 'default', size: 'small' },
        () => jobStatusLabelMap[row.status] || row.status,
      ),
  },
  {
    title: '通过率',
    key: 'pass_rate',
    width: 90,
    render: (row) => {
      const total = row.total || 0
      if (!total) return '-'
      return `${(((row.passed || 0) / total) * 100).toFixed(1)}%`
    },
  },
  {
    title: '统计',
    key: 'counts',
    width: 120,
    render: (row) => `${row.total || 0}/${row.passed || 0}/${row.failed || 0}`,
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/results/${row.id}`) }, () => '结果'),
        h(NButton, { size: 'tiny', type: 'info', onClick: () => openReport(row.id) }, () => '报告'),
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

async function loadPage() {
  await Promise.all([loadApplication(), loadSessions(), loadCases(), loadReplayJobs()])
}

async function loadApplication() {
  try {
    const res = await applicationApi.get(appId)
    app.value = res.data
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载应用详情失败')
  }
}

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const res = await recordingApi.listSessions({ application_id: appId, limit: 20 })
    sessions.value = res.data
  } catch (error: any) {
    sessions.value = []
    message.error(error.response?.data?.detail || '加载录制会话失败')
  } finally {
    sessionsLoading.value = false
  }
}

async function loadCases() {
  casesLoading.value = true
  try {
    const res = await testCaseApi.list({ application_id: appId, limit: 10 })
    testCases.value = res.data
  } catch (error: any) {
    testCases.value = []
    message.error(error.response?.data?.detail || '加载测试用例失败')
  } finally {
    casesLoading.value = false
  }
}

async function loadReplayJobs() {
  jobsLoading.value = true
  try {
    const res = await replayApi.list({ application_id: appId, limit: 10 })
    replayJobs.value = res.data
  } catch (error: any) {
    replayJobs.value = []
    message.error(error.response?.data?.detail || '加载回放任务失败')
  } finally {
    jobsLoading.value = false
  }
}

async function startSession(sessionId: number) {
  try {
    await recordingApi.startSession(sessionId)
    message.success('录制已开始')
    await loadSessions()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '开始录制失败')
  }
}

async function stopSession(sessionId: number) {
  try {
    await recordingApi.stopSession(sessionId, {})
    message.success('已停止录制，平台开始收集数据')
    await loadSessions()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '停止录制失败')
  }
}

async function testConnection() {
  testing.value = true
  try {
    const res = await applicationApi.testConnection(appId)
    if (res.data.success) {
      message.success('连接成功')
    } else {
      message.error(`连接失败：${res.data.message}`)
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '连接测试失败')
  } finally {
    testing.value = false
  }
}

async function mountAgent() {
  mounting.value = true
  try {
    await applicationApi.mountAgent(appId)
    message.info('Agent 挂载已启动，请稍候刷新状态')
    setTimeout(() => void loadApplication(), 3000)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '挂载失败')
  } finally {
    mounting.value = false
  }
}

async function unmountAgent() {
  unmounting.value = true
  try {
    await applicationApi.unmountAgent(appId)
    message.success('Agent 已卸载')
    await loadApplication()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '卸载失败')
  } finally {
    unmounting.value = false
  }
}

async function quickCreateSession() {
  creatingSession.value = true
  try {
    const res = await recordingApi.createSession({
      application_id: appId,
      name: `${app.value?.name || '应用'}-${new Date().toLocaleString('zh-CN', { hour12: false }).replace(/[/: ]/g, '-')}`,
    })
    message.success('录制会话已创建')
    router.push(`/recording/sessions/${res.data.id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建录制会话失败')
  } finally {
    creatingSession.value = false
  }
}

onMounted(() => {
  void loadPage()
})
</script>

<style scoped>
.application-detail-page {
  width: 100%;
}

.page-toolbar {
  align-items: center;
}

.detail-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.detail-stack :deep(.n-card) {
  border-radius: 16px;
}

.detail-stack :deep(.n-data-table) {
  overflow: hidden;
}

.detail-stack :deep(.n-tabs-nav) {
  margin-bottom: 12px;
}

.mapping-preview {
  max-height: 320px;
  overflow: auto;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.mapping-preview pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.6;
}
</style>
