<template>
  <n-space vertical :size="12">
    <n-space justify="space-between">
      <n-h2 style="margin: 0">录制中心</n-h2>
      <n-button v-if="canEdit" type="primary" @click="openCreateSession">+ 新建会话</n-button>
    </n-space>

    <n-space>
      <n-select
        v-model:value="filterApplicationId"
        :options="appOptions"
        clearable
        placeholder="请选择应用"
        style="width: 220px"
        @update:value="loadSessions"
      />
      <n-input
        v-model:value="sessionSearch"
        clearable
        placeholder="搜索会话名称或应用"
        style="width: 240px"
      />
    </n-space>

    <n-data-table
      :columns="sessionColumns"
      :data="filteredSessions"
      :loading="sessionsLoading"
      :pagination="{ pageSize: 10 }"
    />
  </n-space>

  <n-modal v-model:show="showSessionModal" title="新建录制会话" preset="card" style="width: 480px">
    <n-form :model="sessionForm" label-placement="left" label-width="120px">
      <n-form-item label="会话名称">
        <n-input v-model:value="sessionForm.name" placeholder="可选，便于识别" />
      </n-form-item>
      <n-form-item label="所属应用">
        <n-select
          v-model:value="sessionForm.application_id"
          :options="appOptions"
          placeholder="请选择应用"
        />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showSessionModal = false">取消</n-button>
        <n-button type="primary" :loading="creatingSession" @click="createSession">创建</n-button>
      </n-space>
    </template>
  </n-modal>

  <n-drawer v-model:show="showRecordingDrawer" :width="760" placement="right">
    <n-drawer-content :title="`会话 #${selectedSession?.id} 的录制数据`" closable>
      <n-space vertical :size="8">
        <n-input
          v-model:value="recordingSearch"
          clearable
          placeholder="按请求路径搜索"
          style="width: 100%"
        />
        <n-data-table
          :columns="recordingColumns"
          :data="filteredRecordings"
          :loading="recordingsLoading"
          :pagination="{ pageSize: 15 }"
          size="small"
        />
      </n-space>
    </n-drawer-content>
  </n-drawer>

  <n-modal v-model:show="showConvertModal" title="由录制生成测试用例" preset="card" style="width: 420px">
    <n-form :model="convertForm" label-placement="left" label-width="100px">
      <n-form-item label="用例名称">
        <n-input v-model:value="convertForm.name" placeholder="留空则自动生成" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showConvertModal = false">取消</n-button>
        <n-button type="primary" :loading="converting" @click="doConvert">生成</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { NButton, NDataTable, NDrawer, NDrawerContent, NH2, NForm, NFormItem, NInput, NModal, NSpace, NSelect, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'

type SessionRow = {
  id: number
  application_id: number
  name: string
  status: string
  total_count: number
  error_message?: string | null
  created_at: string
}

type RecordingRow = {
  id: number
  request_method: string
  request_uri: string
  response_status: number | null
  latency_ms: number | null
  recorded_at: string
}

const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'

const sessions = ref<SessionRow[]>([])
const sessionsLoading = ref(false)
const filterApplicationId = ref<number | null>(null)
const sessionSearch = ref('')
const appOptions = ref<SelectOption[]>([])
const appNameMap = ref<Record<number, string>>({})

const showSessionModal = ref(false)
const creatingSession = ref(false)
const sessionForm = ref({
  name: '',
  application_id: null as number | null,
})

const showRecordingDrawer = ref(false)
const selectedSession = ref<SessionRow | null>(null)
const recordings = ref<RecordingRow[]>([])
const recordingsLoading = ref(false)
const recordingSearch = ref('')

const showConvertModal = ref(false)
const convertingRecordingId = ref<number | null>(null)
const converting = ref(false)
const convertForm = ref({ name: '' })

const sessionStatusTagType: Record<string, NonNullable<TagProps['type']>> = {
  idle: 'default',
  collecting: 'info',
  done: 'success',
  error: 'error',
}

const sessionStatusLabelMap: Record<string, string> = {
  idle: '待同步',
  collecting: '采集中',
  done: '已完成',
  error: '异常',
}

const filteredSessions = computed(() => {
  const keyword = sessionSearch.value.trim().toLowerCase()
  if (!keyword) {
    return sessions.value
  }
  return sessions.value.filter((session) => {
    const appName = appNameMap.value[session.application_id] || ''
    return session.name.toLowerCase().includes(keyword) || appName.toLowerCase().includes(keyword)
  })
})

const filteredRecordings = computed(() => {
  const keyword = recordingSearch.value.trim().toLowerCase()
  if (!keyword) {
    return recordings.value
  }
  return recordings.value.filter((recording) =>
    recording.request_uri?.toLowerCase().includes(keyword),
  )
})

const sessionColumns: DataTableColumns<SessionRow> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '会话名称', key: 'name', ellipsis: { tooltip: true } },
  {
    title: '所属应用',
    key: 'application_id',
    render: (row) => appNameMap.value[row.application_id] || `#${row.application_id}`,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(
      NTag,
      {
        type: sessionStatusTagType[row.status] ?? 'default',
        size: 'small',
        title: row.status === 'error' ? (row.error_message || '同步失败') : undefined,
      },
      () => sessionStatusLabelMap[row.status] || row.status,
    ),
  },
  { title: '录制数', key: 'total_count', width: 100 },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        ...(canEdit ? [h(NButton, { size: 'tiny', type: 'info', onClick: () => syncSession(row.id) }, () => '同步')] : []),
        h(NButton, { size: 'tiny', onClick: () => viewRecordings(row) }, () => '查看录制'),
      ]),
  },
]

const recordingColumns: DataTableColumns<RecordingRow> = [
  {
    title: '请求信息',
    key: 'request_uri',
    render: (row) =>
      h('span', [
        h('b', row.request_method || 'GET'),
        ' ',
        row.request_uri,
      ]),
  },
  { title: '响应码', key: 'response_status', width: 80 },
  {
    title: '耗时',
    key: 'latency_ms',
    width: 90,
    render: (row) => (row.latency_ms != null ? `${row.latency_ms}ms` : '-'),
  },
  {
    title: '录制时间',
    key: 'recorded_at',
    width: 170,
    render: (row) => formatDateTime(row.recorded_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => canEdit ? h(NButton, { size: 'tiny', type: 'primary', onClick: () => openConvert(row.id) }, () => '生成用例') : null,
  },
]

function formatDateTime(value?: string) {
  return value ? value.slice(0, 19).replace('T', ' ') : '-'
}

async function loadApps() {
  try {
    const res = await applicationApi.list()
    appOptions.value = res.data.map((app: { id: number; name: string }) => ({
      label: app.name,
      value: app.id,
    }))
    appNameMap.value = Object.fromEntries(res.data.map((app: { id: number; name: string }) => [app.id, app.name]))
  } catch (error: any) {
    appOptions.value = []
    appNameMap.value = {}
    message.error(error.response?.data?.detail || '加载应用列表失败')
  }
}

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const params: Record<string, number> = {}
    if (filterApplicationId.value != null) {
      params.application_id = filterApplicationId.value
    }
    const res = await recordingApi.listSessions(params)
    sessions.value = res.data
  } catch (error: any) {
    sessions.value = []
    message.error(error.response?.data?.detail || '加载录制会话失败')
  } finally {
    sessionsLoading.value = false
  }
}

function openCreateSession() {
  sessionForm.value = {
    name: '',
    application_id: null,
  }
  showSessionModal.value = true
}

async function createSession() {
  if (sessionForm.value.application_id == null) {
    message.warning('请先选择应用')
    return
  }

  creatingSession.value = true
  try {
    await recordingApi.createSession(sessionForm.value)
    message.success('录制会话创建成功')
    showSessionModal.value = false
    await loadSessions()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建录制会话失败')
  } finally {
    creatingSession.value = false
  }
}

async function syncSession(sessionId: number) {
  try {
    await recordingApi.syncSession(sessionId, {})
    message.success('已开始同步录制数据')
    await loadSessions()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '启动录制同步失败')
  }
}

async function viewRecordings(session: SessionRow) {
  selectedSession.value = session
  showRecordingDrawer.value = true
  recordingsLoading.value = true
  recordingSearch.value = ''
  try {
    const res = await recordingApi.listRecordings(session.id)
    recordings.value = res.data
  } catch (error: any) {
    recordings.value = []
    message.error(error.response?.data?.detail || '加载录制数据失败')
  } finally {
    recordingsLoading.value = false
  }
}

function openConvert(recordingId: number) {
  convertingRecordingId.value = recordingId
  convertForm.value = { name: '' }
  showConvertModal.value = true
}

async function doConvert() {
  if (convertingRecordingId.value == null) {
    return
  }

  converting.value = true
  try {
    await testCaseApi.fromRecording({
      recording_id: convertingRecordingId.value,
      name: convertForm.value.name || undefined,
    })
    message.success('已由录制生成测试用例')
    showConvertModal.value = false
  } catch (error: any) {
    message.error(error.response?.data?.detail || '生成测试用例失败')
  } finally {
    converting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadApps(), loadSessions()])
})
</script>
