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
      <n-select
        v-model:value="filterStatus"
        :options="statusOptions"
        clearable
        placeholder="会话状态"
        style="width: 160px"
        @update:value="loadSessions"
      />
      <n-date-picker
        v-model:value="filterDateRange"
        type="daterange"
        clearable
        style="width: 260px"
        @update:value="loadSessions"
      />
      <n-input
        v-model:value="sessionSearch"
        clearable
        placeholder="搜索会话名称或应用"
        style="width: 240px"
        @keyup.enter="loadSessions"
      />
      <n-button @click="loadSessions">查询</n-button>
      <n-button quaternary @click="resetFilters">重置</n-button>
    </n-space>

    <n-data-table
      :columns="sessionColumns"
      :data="filteredSessions"
      :loading="sessionsLoading"
      :pagination="{ pageSize: 10 }"
    />

    <n-card title="样本治理视图">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="groupGovernanceStatus"
            clearable
            :options="governanceOptions"
            placeholder="治理状态"
            style="width: 150px"
            @update:value="loadRecordingGroups"
          />
          <n-input
            v-model:value="groupSearch"
            clearable
            placeholder="交易码 / 场景键 / URI"
            style="width: 240px"
            @keyup.enter="loadRecordingGroups"
          />
          <n-button @click="loadRecordingGroups">查询</n-button>
          <n-button
            v-if="canEdit"
            type="primary"
            :disabled="selectedRecordingIds.length === 0"
            @click="openBatchModal"
          >
            批量生成用例{{ selectedRecordingIds.length > 0 ? ` (${selectedRecordingIds.length})` : '' }}
          </n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="groupColumns"
        :data="recordingGroups"
        :loading="groupsLoading"
        :pagination="{ pageSize: 8 }"
        :row-key="(row: RecordingGroupRow) => row.representative_recording_id"
        v-model:checked-row-keys="selectedRecordingIds"
      />
    </n-card>
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
          placeholder="按请求路径或交易码搜索"
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

  <!-- 批量生成用例 Modal（两步：前缀输入 → 冲突检测结果） -->
  <n-modal
    v-model:show="showBatchModal"
    :title="batchStep === 'prefix' ? '批量生成测试用例' : '冲突检测结果'"
    preset="card"
    style="width: 480px"
    :closable="!batchGenerating"
    :mask-closable="!batchGenerating"
  >
    <template v-if="batchStep === 'prefix'">
      <n-space vertical>
        <span>已选 {{ selectedRecordingIds.length }} 个分组</span>
        <n-form label-placement="left" label-width="100px">
          <n-form-item label="用例名称前缀">
            <n-input
              v-model:value="batchPrefix"
              placeholder="如：银行服务"
              @keyup.enter="doBatchCheck"
            />
          </n-form-item>
        </n-form>
      </n-space>
    </template>
    <template v-else>
      <n-space vertical>
        <n-alert
          v-if="batchCheckItems.filter(i => !i.has_existing).length > 0"
          type="success"
          :show-icon="true"
        >
          {{ batchCheckItems.filter(i => !i.has_existing).length }} 条可生成
        </n-alert>
        <n-alert
          v-if="batchCheckItems.filter(i => i.has_existing).length > 0"
          type="warning"
          :show-icon="true"
        >
          {{ batchCheckItems.filter(i => i.has_existing).length }} 条已有用例（{{
            batchCheckItems.filter(i => i.has_existing).map(i => i.transaction_code || `#${i.recording_id}`).join('、')
          }}），将自动跳过
        </n-alert>
        <n-alert
          v-if="batchCheckItems.filter(i => !i.has_existing).length === 0"
          type="info"
        >
          所有选中分组均已有对应用例，无需重复生成
        </n-alert>
      </n-space>
    </template>
    <template #footer>
      <n-space justify="end">
        <template v-if="batchStep === 'prefix'">
          <n-button @click="showBatchModal = false">取消</n-button>
          <n-button type="primary" :loading="batchChecking" @click="doBatchCheck">
            检测冲突 →
          </n-button>
        </template>
        <template v-else>
          <n-button @click="batchStep = 'prefix'">返回</n-button>
          <n-button
            v-if="batchCheckItems.filter(i => !i.has_existing).length > 0"
            type="primary"
            :loading="batchGenerating"
            @click="doBatchGenerate"
          >
            确认生成 →
          </n-button>
        </template>
      </n-space>
    </template>
  </n-modal>

  <!-- 批量生成结果 Modal -->
  <n-modal
    v-model:show="showBatchResultModal"
    title="生成完成"
    preset="card"
    style="width: 420px"
  >
    <n-space vertical v-if="batchResult">
      <n-alert v-if="batchResult.created > 0" type="success" :show-icon="true">成功 {{ batchResult.created }} 条</n-alert>
      <n-alert v-if="batchResult.skipped > 0" type="warning" :show-icon="true">
        跳过 {{ batchResult.skipped }} 条（已有用例）
      </n-alert>
      <n-alert v-if="batchResult.failed > 0" type="error" :show-icon="true">
        失败 {{ batchResult.failed }} 条
        <ul style="margin: 4px 0 0; padding-left: 16px; font-size: 12px">
          <li v-for="r in batchResult.results.filter(x => x.status === 'failed')" :key="r.recording_id">
            录制 #{{ r.recording_id }}：{{ r.error }}
          </li>
        </ul>
      </n-alert>
    </n-space>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showBatchResultModal = false">关闭</n-button>
        <n-button type="primary" @click="() => { showBatchResultModal = false; router.push('/test-cases') }">
          前往测试用例库 →
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NDataTable, NDatePicker, NDrawer, NDrawerContent, NH2, NForm, NFormItem, NInput, NModal, NPopconfirm, NSpace, NSelect, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { formatDateTime } from '@/utils/format'
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
  transaction_code?: string | null
  governance_status: string
  duplicate_count?: number | null
  response_status: number | null
  latency_ms: number | null
  recorded_at: string
}

type RecordingGroupRow = {
  application_id: number
  transaction_code?: string | null
  scene_key?: string | null
  total_count: number
  approved_count: number
  candidate_count: number
  raw_count: number
  latest_recorded_at: string
  representative_recording_id: number
  representative_governance_status: string
  representative_request_method: string
  representative_request_uri: string
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'

const sessions = ref<SessionRow[]>([])
const sessionsLoading = ref(false)
const filterApplicationId = ref<number | null>(null)
const filterStatus = ref<string | null>(null)
const filterDateRange = ref<[number, number] | null>(null)
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
const recordingGroups = ref<RecordingGroupRow[]>([])
const groupsLoading = ref(false)
const groupGovernanceStatus = ref<string | null>(null)
const groupSearch = ref('')

const showConvertModal = ref(false)
// 批量生成用例
const selectedRecordingIds = ref<(string | number)[]>([])
const showBatchModal = ref(false)
const batchStep = ref<'prefix' | 'check'>('prefix')
const batchPrefix = ref('')
const batchChecking = ref(false)
const batchCheckItems = ref<Array<{
  recording_id: number
  transaction_code: string | null
  has_existing: boolean
  existing_case_id: number | null
  existing_case_name: string | null
}>>([])
const batchGenerating = ref(false)
const showBatchResultModal = ref(false)
const batchResult = ref<{
  total: number
  created: number
  failed: number
  skipped: number
  results: Array<{ recording_id: number; status: string; name?: string; error?: string }>
} | null>(null)
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

const statusOptions: SelectOption[] = [
  { label: '待同步', value: 'idle' },
  { label: '采集中', value: 'collecting' },
  { label: '已完成', value: 'done' },
  { label: '异常', value: 'error' },
]

const governanceOptions: SelectOption[] = [
  { label: '原始录制', value: 'raw' },
  { label: '候选样本', value: 'candidate' },
  { label: '已批准', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已归档', value: 'archived' },
]

const governanceLabelMap: Record<string, string> = {
  raw: '原始录制',
  candidate: '候选样本',
  approved: '已批准',
  rejected: '已拒绝',
  archived: '已归档',
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
    recording.request_uri?.toLowerCase().includes(keyword)
    || recording.transaction_code?.toLowerCase().includes(keyword),
  )
})

const sessionColumns: DataTableColumns<SessionRow> = [
  { title: 'ID', key: 'id', width: 60 },
  {
    title: '会话名称',
    key: 'name',
    ellipsis: { tooltip: true },
    render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => router.push(`/recording/sessions/${row.id}`) }, () => row.name),
  },
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
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/sessions/${row.id}`) }, () => '会话详情'),
        ...(canEdit ? [h(NButton, { size: 'tiny', type: 'info', onClick: () => syncSession(row.id) }, () => '同步')] : []),
        h(NButton, { size: 'tiny', onClick: () => viewRecordings(row) }, () => '查看录制'),
        ...(canEdit ? [
          h(NPopconfirm, { onPositiveClick: () => deleteSession(row.id) }, {
            default: () => '确认删除该会话及其所有录制数据？',
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
          }),
        ] : []),
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
  { title: '交易码', key: 'transaction_code', width: 140, render: (row) => row.transaction_code || '-' },
  { title: '治理状态', key: 'governance_status', width: 100, render: (row) => governanceLabelMap[row.governance_status] || row.governance_status || '-' },
  { title: '重复', key: 'duplicate_count', width: 70, render: (row) => row.duplicate_count ?? 1 },
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
    width: 250,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/recordings/${row.id}`) }, () => '详情'),
        ...(canEdit ? [
          h(NButton, { size: 'tiny', onClick: () => quickGovernance(row.id, 'candidate') }, () => '标候选'),
          h(NButton, { size: 'tiny', type: 'primary', onClick: () => openConvert(row.id) }, () => '生成用例'),
        ] : []),
      ]),
  },
]

const groupColumns: DataTableColumns<RecordingGroupRow> = [
  { type: 'selection' },
  {
    title: '交易码 / 场景',
    key: 'transaction_code',
    render: (row) => h('div', [
      h('div', [h('b', row.transaction_code || '未识别交易码')]),
      h('div', { style: 'color:#666;font-size:12px' }, row.scene_key || '-'),
    ]),
  },
  {
    title: '代表样本',
    key: 'representative_recording_id',
    render: (row) => h('span', [h('b', { style: 'margin-right:4px' }, row.representative_request_method), row.representative_request_uri]),
  },
  { title: '总数', key: 'total_count', width: 70 },
  { title: '已批准', key: 'approved_count', width: 80 },
  { title: '候选', key: 'candidate_count', width: 70 },
  { title: '原始', key: 'raw_count', width: 70 },
  {
    title: '最新录制',
    key: 'latest_recorded_at',
    width: 170,
    render: (row) => formatDateTime(row.latest_recorded_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    render: (row) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/recordings/${row.representative_recording_id}`) }, () => '代表样本'),
      ...(canEdit ? [
        h(NButton, { size: 'tiny', type: 'success', onClick: () => quickGovernance(row.representative_recording_id, 'approved', true) }, () => '批准代表'),
        h(NButton, { size: 'tiny', onClick: () => openConvert(row.representative_recording_id) }, () => '生成用例'),
      ] : []),
    ]),
  },
]

function rangeStartIso(value: number) {
  return new Date(value).toISOString()
}

function rangeEndIso(value: number) {
  return new Date(value + 86_399_999).toISOString()
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
    const params: Record<string, number | string> = {}
    if (filterApplicationId.value != null) {
      params.application_id = filterApplicationId.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (sessionSearch.value.trim()) {
      params.search = sessionSearch.value.trim()
    }
    if (filterDateRange.value) {
      params.created_after = rangeStartIso(filterDateRange.value[0])
      params.created_before = rangeEndIso(filterDateRange.value[1])
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

async function loadRecordingGroups() {
  groupsLoading.value = true
  try {
    const res = await recordingApi.listRecordingGroups({
      application_id: filterApplicationId.value ?? undefined,
      governance_status: groupGovernanceStatus.value || undefined,
      search: groupSearch.value.trim() || undefined,
    })
    recordingGroups.value = res.data
    selectedRecordingIds.value = []
  } catch (error: any) {
    recordingGroups.value = []
    message.error(error.response?.data?.detail || '加载样本治理视图失败')
  } finally {
    groupsLoading.value = false
  }
}

function resetFilters() {
  filterApplicationId.value = null
  filterStatus.value = null
  filterDateRange.value = null
  sessionSearch.value = ''
  groupGovernanceStatus.value = null
  groupSearch.value = ''
  void Promise.all([loadSessions(), loadRecordingGroups()])
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
    await Promise.all([loadSessions(), loadRecordingGroups()])
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
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '启动录制同步失败')
  }
}

async function deleteSession(sessionId: number) {
  try {
    await recordingApi.deleteSession(sessionId)
    message.success('会话已删除')
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
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

async function quickGovernance(recordingId: number, governanceStatus: string, refreshGroups = false) {
  try {
    await recordingApi.updateRecording(recordingId, { governance_status: governanceStatus })
    message.success('治理状态已更新')
    if (selectedSession.value) {
      await viewRecordings(selectedSession.value)
    }
    if (refreshGroups) {
      await loadRecordingGroups()
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '更新治理状态失败')
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

function openBatchModal() {
  batchPrefix.value = ''
  batchStep.value = 'prefix'
  batchCheckItems.value = []
  showBatchModal.value = true
}

async function doBatchCheck() {
  if (!batchPrefix.value.trim()) {
    message.warning('请填写用例名称前缀')
    return
  }
  batchChecking.value = true
  try {
    const ids = selectedRecordingIds.value.map(Number)
    const res = await testCaseApi.batchCheck({ recording_ids: ids })
    batchCheckItems.value = res.data
    batchStep.value = 'check'
  } catch (error: any) {
    message.error(error.response?.data?.detail || '冲突检测失败')
  } finally {
    batchChecking.value = false
  }
}

async function doBatchGenerate() {
  const toGenerate = batchCheckItems.value
    .filter(i => !i.has_existing)
    .map(i => i.recording_id)
  if (toGenerate.length === 0) {
    message.warning('没有可生成的用例')
    return
  }
  const skippedCount = batchCheckItems.value.filter(i => i.has_existing).length

  batchGenerating.value = true
  try {
    const res = await testCaseApi.batchFromRecordings({
      recording_ids: toGenerate,
      prefix: batchPrefix.value.trim(),
    })
    batchResult.value = {
      ...res.data,
      skipped: skippedCount,
    }
    showBatchModal.value = false
    showBatchResultModal.value = true
    selectedRecordingIds.value = []
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量生成失败')
  } finally {
    batchGenerating.value = false
  }
}

onMounted(async () => {
  const queryAppId = typeof route.query.application_id === 'string' ? Number(route.query.application_id) : null
  if (queryAppId != null && !Number.isNaN(queryAppId)) {
    filterApplicationId.value = queryAppId
  }
  if (typeof route.query.status === 'string' && route.query.status) {
    filterStatus.value = route.query.status
  }
  if (typeof route.query.search === 'string' && route.query.search) {
    sessionSearch.value = route.query.search
  }
  await Promise.all([loadApps(), loadSessions(), loadRecordingGroups()])
})
</script>
