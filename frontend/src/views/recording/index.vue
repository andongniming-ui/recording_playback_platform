<template>
  <n-space vertical :size="12">
    <n-space justify="space-between">
      <n-h2 style="margin:0">录制中心</n-h2>
      <n-button type="primary" @click="openCreateSession">+ 新建会话</n-button>
    </n-space>

    <!-- 过滤 -->
    <n-space>
      <n-select
        v-model:value="filterAppId"
        :options="appOptions"
        clearable
        placeholder="选择应用"
        style="width:200px"
        @update:value="loadSessions"
      />
      <n-input
        v-model:value="filterUri"
        clearable
        placeholder="URI 搜索"
        style="width:220px"
        @input="loadSessions"
      />
    </n-space>

    <!-- 会话列表 -->
    <n-data-table
      :columns="sessionColumns"
      :data="sessions"
      :loading="sessionsLoading"
      :pagination="{ pageSize: 10 }"
    />
  </n-space>

  <!-- 新建会话弹窗 -->
  <n-modal v-model:show="showSessionModal" title="新建录制会话" preset="card" style="width:480px">
    <n-form :model="sessionForm" label-placement="left" label-width="100px">
      <n-form-item label="会话名称">
        <n-input v-model:value="sessionForm.name" placeholder="可选" />
      </n-form-item>
      <n-form-item label="应用" :rule="{ required: true }">
        <n-select v-model:value="sessionForm.app_id" :options="appOptions" placeholder="选择应用" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showSessionModal = false">取消</n-button>
        <n-button type="primary" :loading="creatingSession" @click="createSession">创建</n-button>
      </n-space>
    </template>
  </n-modal>

  <!-- 录制详情抽屉 -->
  <n-drawer v-model:show="showRecordingDrawer" :width="700" placement="right">
    <n-drawer-content :title="`会话 #${selectedSession?.id} 录制列表`" closable>
      <n-space vertical :size="8">
        <n-input
          v-model:value="recSearchUri"
          clearable
          placeholder="搜索 URI"
          style="width:100%"
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

  <!-- 转为用例确认弹窗 -->
  <n-modal v-model:show="showConvertModal" title="转为测试用例" preset="card" style="width:400px">
    <n-form :model="convertForm" label-placement="left" label-width="100px">
      <n-form-item label="用例名称">
        <n-input v-model:value="convertForm.name" placeholder="留空自动生成" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showConvertModal = false">取消</n-button>
        <n-button type="primary" :loading="converting" @click="doConvert">转换</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NSpace, NH2, NButton, NDataTable, NSelect, NInput, NModal, NForm, NFormItem,
  NDrawer, NDrawerContent, NTag, NPopconfirm, useMessage
} from 'naive-ui'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { applicationApi } from '@/api/applications'

const message = useMessage()

const sessions = ref<any[]>([])
const sessionsLoading = ref(false)
const filterAppId = ref<number | null>(null)
const filterUri = ref('')
const appOptions = ref<any[]>([])

const showSessionModal = ref(false)
const creatingSession = ref(false)
const sessionForm = ref({ name: '', app_id: null as number | null })

const showRecordingDrawer = ref(false)
const selectedSession = ref<any>(null)
const recordings = ref<any[]>([])
const recordingsLoading = ref(false)
const recSearchUri = ref('')

const showConvertModal = ref(false)
const convertingRecordingId = ref<number | null>(null)
const convertForm = ref({ name: '' })
const converting = ref(false)

const filteredRecordings = computed(() =>
  recSearchUri.value
    ? recordings.value.filter(r => r.uri?.includes(recSearchUri.value))
    : recordings.value
)

const sessionColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '会话名', key: 'name', ellipsis: { tooltip: true } },
  { title: '应用', key: 'app_name' },
  {
    title: '状态', key: 'status', width: 90,
    render: (r: any) => h(NTag, {
      type: r.status === 'active' ? 'success' : 'default',
      size: 'small',
    }, () => r.status || '-'),
  },
  { title: '录制数', key: 'recording_count', width: 80 },
  {
    title: '创建时间', key: 'created_at', width: 160,
    render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' '),
  },
  {
    title: '操作', key: 'actions',
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', type: 'info', onClick: () => syncSession(r.id) }, () => '同步'),
      h(NButton, { size: 'tiny', onClick: () => viewRecordings(r) }, () => '查看录制'),
    ]),
  },
]

const recordingColumns = [
  {
    title: '请求', key: 'uri',
    render: (r: any) => h('span', [
      h('b', r.method || 'GET'),
      ' ',
      r.uri,
    ]),
  },
  { title: '状态码', key: 'status_code', width: 75 },
  { title: '延迟(ms)', key: 'latency_ms', width: 85 },
  {
    title: '时间', key: 'created_at', width: 150,
    render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' '),
  },
  {
    title: '操作', key: 'actions', width: 90,
    render: (r: any) => h(NButton, { size: 'tiny', type: 'primary', onClick: () => openConvert(r.id) }, () => '转为用例'),
  },
]

async function loadApps() {
  try {
    const res = await applicationApi.list()
    appOptions.value = res.data.map((a: any) => ({ label: a.name, value: a.id }))
  } catch {
    // ignore
  }
}

async function loadSessions() {
  sessionsLoading.value = true
  try {
    const params: any = {}
    if (filterAppId.value) params.app_id = filterAppId.value
    const res = await recordingApi.listSessions(params)
    sessions.value = res.data
  } catch {
    message.error('加载会话失败')
  } finally {
    sessionsLoading.value = false
  }
}

function openCreateSession() {
  sessionForm.value = { name: '', app_id: null }
  showSessionModal.value = true
}

async function createSession() {
  if (!sessionForm.value.app_id) {
    message.warning('请选择应用')
    return
  }
  creatingSession.value = true
  try {
    await recordingApi.createSession(sessionForm.value)
    message.success('会话创建成功')
    showSessionModal.value = false
    await loadSessions()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '创建失败')
  } finally {
    creatingSession.value = false
  }
}

async function syncSession(id: number) {
  try {
    await recordingApi.syncSession(id, {})
    message.success('同步已触发')
    await loadSessions()
  } catch {
    message.error('同步失败')
  }
}

async function viewRecordings(session: any) {
  selectedSession.value = session
  showRecordingDrawer.value = true
  recordingsLoading.value = true
  recSearchUri.value = ''
  try {
    const res = await recordingApi.listRecordings(session.id)
    recordings.value = res.data
  } catch {
    message.error('加载录制列表失败')
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
  if (!convertingRecordingId.value) return
  converting.value = true
  try {
    await testCaseApi.fromRecording({
      recording_id: convertingRecordingId.value,
      name: convertForm.value.name || undefined,
    })
    message.success('已转为测试用例')
    showConvertModal.value = false
  } catch (e: any) {
    message.error(e.response?.data?.detail || '转换失败')
  } finally {
    converting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadApps(), loadSessions()])
})
</script>
