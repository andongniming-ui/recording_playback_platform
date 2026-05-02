<template>
  <n-space vertical :size="16" class="recording-page">
    <n-space justify="space-between" align="center">
      <div>
        <n-h2 style="margin: 0">录制中心</n-h2>
        <n-text depth="3">按会话查看录制结果，按样本治理视图做批量处理。</n-text>
      </div>
      <n-button v-if="canEdit" type="primary" @click="openCreateSession">+ 新建会话</n-button>
    </n-space>

    <n-grid cols="1 s:2 l:4" responsive="screen" :x-gap="12" :y-gap="12" class="recording-summary">
      <n-grid-item>
        <n-card>
          <n-statistic label="会话总数" :value="sessionPagination.itemCount" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="已完成会话" :value="sessions.filter(item => item.status === 'done').length" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="治理分组" :value="groupPagination.itemCount" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="已选分组" :value="selectedGroupRecordingIds.length" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="查询条件">
      <div class="recording-filter-grid">
        <n-select
          v-model:value="filterApplicationId"
          :options="appOptions"
          clearable
          placeholder="请选择应用"
          @update:value="handleApplicationFilterChange"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="会话状态"
          @update:value="reloadSessionsFromFirstPage"
        />
        <n-date-picker
          v-model:value="filterDateRange"
          type="daterange"
          clearable
          @update:value="reloadSessionsFromFirstPage"
        />
        <n-input
          v-model:value="sessionSearch"
          clearable
          placeholder="搜索会话名称或应用"
          @keyup.enter="reloadSessionsFromFirstPage"
        />
        <div class="recording-filter-actions">
          <n-button type="primary" @click="reloadSessionsFromFirstPage">查询</n-button>
          <n-button quaternary @click="resetFilters">重置</n-button>
        </div>
      </div>
    </n-card>

    <n-card title="录制会话">
      <template #header-extra>
        <n-space>
          <n-tag type="info" size="small">共 {{ sessionPagination.itemCount }} 条</n-tag>
          <n-button
            v-if="canEdit"
            size="small"
            type="error"
            :disabled="selectedSessionIds.length === 0"
            @click="deleteSelectedSessions"
          >
            批量删除{{ selectedSessionIds.length > 0 ? ` (${selectedSessionIds.length})` : '' }}
          </n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="sessionColumns"
        :data="filteredSessions"
        :loading="sessionsLoading"
        :row-key="(row: SessionRow) => row.id"
        :pagination="sessionPagination"
        remote
        v-model:checked-row-keys="selectedSessionIds"
        @update:sorter="handleSessionSorterChange"
      />
    </n-card>

    <n-card title="样本治理视图">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="groupGovernanceStatus"
            clearable
            :options="governanceOptions"
            placeholder="治理状态"
            style="width: 150px"
            @update:value="reloadRecordingGroupsFromFirstPage"
          />
          <n-input
            v-model:value="groupSearch"
            clearable
            placeholder="交易码 / 场景键 / URI"
            style="width: 240px"
            @keyup.enter="reloadRecordingGroupsFromFirstPage"
          />
          <n-button @click="reloadRecordingGroupsFromFirstPage">查询</n-button>
          <n-button
            v-if="canEdit"
            type="error"
            :disabled="selectedGroupRecordingIds.length === 0"
            @click="deleteSelectedGroupRecordings"
          >
            批量删除代表样本{{ selectedGroupRecordingIds.length > 0 ? ` (${selectedGroupRecordingIds.length})` : '' }}
          </n-button>
          <n-button
            v-if="canEdit"
            type="primary"
            :disabled="selectedGroupRecordingIds.length === 0"
            @click="openBatchModal('groups')"
          >
            批量生成用例{{ selectedGroupRecordingIds.length > 0 ? ` (${selectedGroupRecordingIds.length})` : '' }}
          </n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="groupColumns"
        :data="recordingGroups"
        :loading="groupsLoading"
        :pagination="groupPagination"
        :row-key="(row: RecordingGroupRow) => row.representative_recording_id"
        remote
        v-model:checked-row-keys="selectedGroupRecordingIds"
        @update:sorter="handleGroupSorterChange"
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
      <n-form-item label="交易码过滤">
        <n-input
          v-model:value="sessionForm.recording_filter_prefixes_text"
          type="textarea"
          :autosize="{ minRows: 3, maxRows: 6 }"
          placeholder="例如：car001\n=car001_open\nre:^car001.*$"
        />
      </n-form-item>
      <n-form-item label="说明">
        <n-text depth="3">推荐一行一条规则，支持前缀、精确和正则；空白表示不过滤。</n-text>
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
        <n-space justify="space-between">
          <n-input
            v-model:value="recordingSearch"
            clearable
            placeholder="按请求路径或交易码搜索"
            style="width: 100%"
            @keyup.enter="reloadCurrentRecordingsFromFirstPage"
          />
          <n-space v-if="canEdit">
            <n-button
              size="small"
              type="error"
              :disabled="selectedSessionRecordingIds.length === 0"
              @click="deleteSelectedSessionRecordings"
            >
              批量删除{{ selectedSessionRecordingIds.length > 0 ? ` (${selectedSessionRecordingIds.length})` : '' }}
            </n-button>
            <n-button
              size="small"
              type="primary"
              :disabled="selectedSessionRecordingIds.length === 0"
              @click="openBatchModal('recordings')"
            >
              批量生成用例{{ selectedSessionRecordingIds.length > 0 ? ` (${selectedSessionRecordingIds.length})` : '' }}
            </n-button>
          </n-space>
        </n-space>
        <n-data-table
          :columns="recordingColumns"
          :data="filteredRecordings"
          :loading="recordingsLoading"
          :pagination="recordingPagination"
          size="small"
          :row-key="(row: RecordingRow) => row.id"
          remote
          v-model:checked-row-keys="selectedSessionRecordingIds"
          @update:sorter="handleRecordingSorterChange"
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
        <span>{{ batchSource === 'groups' ? `已选 ${selectedGroupRecordingIds.length} 个分组` : `已选 ${selectedSessionRecordingIds.length} 条录制` }}</span>
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
        <n-button type="primary" @click="() => { showBatchResultModal = false; router.push('/testcases') }">
          前往测试用例库 →
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, h, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NDataTable, NDatePicker, NDrawer, NDrawerContent, NGrid, NGridItem, NH2, NForm, NFormItem, NInput, NModal, NPopconfirm, NSpace, NSelect, NStatistic, NTag, NText, useMessage } from 'naive-ui'
import type { DataTableColumns, SelectOption, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { formatDateTime } from '@/utils/format'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'
import type { RecordingSubCall } from '@/utils/recording'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData } from '@/utils/pagination'

type SessionRow = {
  id: number
  application_id: number
  name: string
  status: string
  total_count: number
  error_message?: string | null
  recording_filter_prefixes?: string[] | null
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
  sub_calls?: RecordingSubCall[] | string | null
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
  recording_filter_prefixes_text: '',
})

const showRecordingDrawer = ref(false)
const selectedSession = ref<SessionRow | null>(null)
const recordings = ref<RecordingRow[]>([])
const recordingsLoading = ref(false)
const recordingSearch = ref('')
const selectedSessionRecordingIds = ref<(string | number)[]>([])
const recordingGroups = ref<RecordingGroupRow[]>([])
const groupsLoading = ref(false)
const groupGovernanceStatus = ref<string | null>(null)
const groupSearch = ref('')
const selectedSessionIds = ref<(string | number)[]>([])
const selectedGroupRecordingIds = ref<(string | number)[]>([])
const sessionSort = ref(defaultSortState('created_at'))
const recordingSort = ref(defaultSortState('recorded_at'))
const groupSort = ref(defaultSortState('latest_recorded_at'))
const sessionCountPollingTimer = ref<number | null>(null)
const sessionPagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条`,
  onUpdatePage: (page: number) => {
    sessionPagination.page = page
    void loadSessions()
  },
  onUpdatePageSize: (pageSize: number) => {
    sessionPagination.pageSize = pageSize
    sessionPagination.page = 1
    void loadSessions()
  },
})
const groupPagination = reactive({
  page: 1,
  pageSize: 8,
  itemCount: 0,
  pageSizes: [8, 16, 32, 64],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 组`,
  onUpdatePage: (page: number) => {
    groupPagination.page = page
    void loadRecordingGroups()
  },
  onUpdatePageSize: (pageSize: number) => {
    groupPagination.pageSize = pageSize
    groupPagination.page = 1
    void loadRecordingGroups()
  },
})
const recordingPagination = reactive({
  page: 1,
  pageSize: 15,
  itemCount: 0,
  pageSizes: [15, 30, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条录制`,
  onUpdatePage: (page: number) => {
    recordingPagination.page = page
    void reloadCurrentRecordings()
  },
  onUpdatePageSize: (pageSize: number) => {
    recordingPagination.pageSize = pageSize
    recordingPagination.page = 1
    void reloadCurrentRecordings()
  },
})

const showConvertModal = ref(false)
// 批量生成用例
const batchSource = ref<'groups' | 'recordings'>('groups')
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

const statusOptions: SelectOption[] = [
  { label: '待开始', value: 'idle' },
  { label: '录制中', value: 'active' },
  { label: '收集中', value: 'collecting' },
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
  return sessions.value
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

const sessionColumns = computed<DataTableColumns<SessionRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const, disabled: (row: SessionRow) => row.status === 'active' || row.status === 'collecting' }] : []),
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
    title: '交易码过滤',
    key: 'recording_filter_prefixes',
    width: 180,
    render: (row) => formatPrefixSummary(row.recording_filter_prefixes),
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
    sorter: true,
    sortOrder: resolveSortOrder(sessionSort.value, 'created_at'),
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/recording/sessions/${row.id}`) }, () => '会话详情'),
        ...(canEdit && row.status === 'idle'
          ? [h(NButton, { size: 'tiny', type: 'primary', onClick: () => startSession(row.id) }, () => '开始录制')]
          : []),
        ...(canEdit && row.status === 'active'
          ? [h(NButton, { size: 'tiny', type: 'warning', onClick: () => stopSession(row.id) }, () => '停止录制')]
          : []),
        h(NButton, { size: 'tiny', onClick: () => viewRecordings(row) }, () => '查看录制'),
        ...(canEdit && row.status !== 'active' && row.status !== 'collecting' ? [
          h(NPopconfirm, { onPositiveClick: () => deleteSession(row.id) }, {
            default: () => '确认删除该会话及其所有录制数据？',
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
          }),
        ] : []),
      ]),
  },
])

const recordingColumns = computed<DataTableColumns<RecordingRow>>(() => [
  ...(canEdit ? [{ type: 'selection' as const }] : []),
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
  {
    title: '子调用',
    key: 'sub_calls',
    width: 140,
    render: (row) => {
      const summary = buildRecordingSubCallSummary(parseRecordingSubCalls(row.sub_calls))
      return summary === '无细分' ? '-' : summary
    },
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
    sorter: true,
    sortOrder: resolveSortOrder(recordingSort.value, 'recorded_at'),
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
          h(NPopconfirm, { onPositiveClick: () => deleteRecording(row.id) }, {
            default: () => '确认删除该录制?',
            trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
          }),
        ] : []),
      ]),
  },
])

const groupColumns = computed<DataTableColumns<RecordingGroupRow>>(() => [
  { type: 'selection' as const },
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
    sorter: true,
    sortOrder: resolveSortOrder(groupSort.value, 'latest_recorded_at'),
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
        h(NPopconfirm, { onPositiveClick: () => deleteRecording(row.representative_recording_id, true) }, {
          default: () => '确认删除代表样本?',
          trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除代表'),
        }),
      ] : []),
    ]),
  },
])

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

async function loadSessions(options: { silent?: boolean } = {}) {
  if (!options.silent) {
    sessionsLoading.value = true
  }
  try {
    const params: Record<string, number | string | boolean> = {}
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
    params.sort_by = sessionSort.value.columnKey
    params.sort_order = toApiSortOrder(sessionSort.value.order)
    params.refresh_active_count = true
    const page = await loadPagedData<SessionRow>(recordingApi.listSessions, params, sessionPagination.page, sessionPagination.pageSize, 100)
    sessions.value = page.items
    sessionPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && sessionPagination.page > 1) {
      sessionPagination.page = lastValidPage(page.total, sessionPagination.pageSize)
      void loadSessions()
      return
    }
    selectedSessionIds.value = []
    updateSessionCountPolling()
  } catch (error: any) {
    sessions.value = []
    sessionPagination.itemCount = 0
    updateSessionCountPolling()
    if (!options.silent) {
      message.error(error.response?.data?.detail || '加载录制会话失败')
    }
  } finally {
    if (!options.silent) {
      sessionsLoading.value = false
    }
  }
}

function reloadSessionsFromFirstPage() {
  sessionPagination.page = 1
  void loadSessions()
}

function shouldPollSessionList() {
  return sessions.value.some((session) => session.status === 'active' || session.status === 'collecting')
}

function startSessionCountPolling() {
  if (sessionCountPollingTimer.value != null) {
    return
  }
  sessionCountPollingTimer.value = window.setInterval(() => {
    void loadSessions({ silent: true })
  }, 10_000)
}

function stopSessionCountPolling() {
  if (sessionCountPollingTimer.value == null) {
    return
  }
  window.clearInterval(sessionCountPollingTimer.value)
  sessionCountPollingTimer.value = null
}

function updateSessionCountPolling() {
  if (shouldPollSessionList()) {
    startSessionCountPolling()
  } else {
    stopSessionCountPolling()
  }
}

async function loadRecordingGroups() {
  groupsLoading.value = true
  try {
    const page = await loadPagedData<RecordingGroupRow>(recordingApi.listRecordingGroups, {
      application_id: filterApplicationId.value ?? undefined,
      governance_status: groupGovernanceStatus.value || undefined,
      search: groupSearch.value.trim() || undefined,
      sort_by: groupSort.value.columnKey,
      sort_order: toApiSortOrder(groupSort.value.order),
    }, groupPagination.page, groupPagination.pageSize, 200)
    recordingGroups.value = page.items
    groupPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && groupPagination.page > 1) {
      groupPagination.page = lastValidPage(page.total, groupPagination.pageSize)
      void loadRecordingGroups()
      return
    }
    selectedGroupRecordingIds.value = []
  } catch (error: any) {
    recordingGroups.value = []
    groupPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载样本治理视图失败')
  } finally {
    groupsLoading.value = false
  }
}

function reloadRecordingGroupsFromFirstPage() {
  groupPagination.page = 1
  void loadRecordingGroups()
}

function handleApplicationFilterChange() {
  sessionPagination.page = 1
  groupPagination.page = 1
  void Promise.all([loadSessions(), loadRecordingGroups()])
}

function resetFilters() {
  filterApplicationId.value = null
  filterStatus.value = null
  filterDateRange.value = null
  sessionSearch.value = ''
  groupGovernanceStatus.value = null
  groupSearch.value = ''
  sessionPagination.page = 1
  groupPagination.page = 1
  void Promise.all([loadSessions(), loadRecordingGroups()])
}

function openCreateSession() {
  sessionForm.value = {
    name: '',
    application_id: null,
    recording_filter_prefixes_text: '',
  }
  showSessionModal.value = true
}

function parsePrefixList(raw: string): string[] {
  const text = raw.trim()
  if (!text) {
    return []
  }

  const hasStructuredSeparator = /[\n;；]/.test(text)
  if (hasStructuredSeparator) {
    return text
      .split(/[\n;；]+/)
      .map((item) => item.trim())
      .filter(Boolean)
  }

  if (/^(?:re:|regex:|=|\/).*/i.test(text)) {
    return [text]
  }

  return text
    .split(/[，,]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function formatPrefixSummary(prefixes?: string[] | null) {
  if (!prefixes || prefixes.length === 0) {
    return '-'
  }
  return prefixes.join(', ')
}

async function createSession() {
  if (sessionForm.value.application_id == null) {
    message.warning('请先选择应用')
    return
  }

  creatingSession.value = true
  try {
    const prefixes = parsePrefixList(sessionForm.value.recording_filter_prefixes_text)
    await recordingApi.createSession({
      application_id: sessionForm.value.application_id,
      name: sessionForm.value.name,
      recording_filter_prefixes: prefixes.length > 0 ? prefixes : undefined,
    })
    message.success('录制会话创建成功')
    showSessionModal.value = false
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建录制会话失败')
  } finally {
    creatingSession.value = false
  }
}

async function startSession(sessionId: number) {
  try {
    await recordingApi.startSession(sessionId)
    message.success('录制已开始')
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '开始录制失败')
  }
}

async function stopSession(sessionId: number) {
  try {
    await recordingApi.stopSession(sessionId, {})
    message.success('已停止录制，平台开始收集数据')
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '停止录制失败')
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

async function deleteSelectedSessions() {
  if (selectedSessionIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteSessions({ ids: selectedSessionIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 个会话`)
    await Promise.all([loadSessions(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
  }
}

async function viewRecordings(session: SessionRow) {
  selectedSession.value = session
  showRecordingDrawer.value = true
  recordingsLoading.value = true
  recordingSearch.value = ''
  recordingPagination.page = 1
  selectedSessionRecordingIds.value = []
  try {
    const page = await loadPagedData<RecordingRow>((requestParams) => recordingApi.listRecordings(session.id, requestParams), {
      sort_by: recordingSort.value.columnKey,
      sort_order: toApiSortOrder(recordingSort.value.order),
      search: recordingSearch.value.trim() || undefined,
    }, recordingPagination.page, recordingPagination.pageSize, 200)
    recordings.value = page.items
    recordingPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && recordingPagination.page > 1) {
      recordingPagination.page = lastValidPage(page.total, recordingPagination.pageSize)
      void reloadCurrentRecordings()
      return
    }
  } catch (error: any) {
    recordings.value = []
    recordingPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载录制数据失败')
  } finally {
    recordingsLoading.value = false
  }
}

async function reloadCurrentRecordings() {
  if (!selectedSession.value) return
  recordingsLoading.value = true
  selectedSessionRecordingIds.value = []
  try {
    const page = await loadPagedData<RecordingRow>((requestParams) => recordingApi.listRecordings(selectedSession.value!.id, requestParams), {
      sort_by: recordingSort.value.columnKey,
      sort_order: toApiSortOrder(recordingSort.value.order),
      search: recordingSearch.value.trim() || undefined,
    }, recordingPagination.page, recordingPagination.pageSize, 200)
    recordings.value = page.items
    recordingPagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && recordingPagination.page > 1) {
      recordingPagination.page = lastValidPage(page.total, recordingPagination.pageSize)
      void reloadCurrentRecordings()
    }
  } catch (error: any) {
    recordings.value = []
    recordingPagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载录制数据失败')
  } finally {
    recordingsLoading.value = false
  }
}

function reloadCurrentRecordingsFromFirstPage() {
  recordingPagination.page = 1
  void reloadCurrentRecordings()
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

function openBatchModal(source: 'groups' | 'recordings') {
  batchSource.value = source
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
    const ids = (batchSource.value === 'groups' ? selectedGroupRecordingIds.value : selectedSessionRecordingIds.value).map(Number)
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
    if (batchSource.value === 'groups') {
      selectedGroupRecordingIds.value = []
    } else {
      selectedSessionRecordingIds.value = []
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量生成失败')
  } finally {
    batchGenerating.value = false
  }
}

async function deleteRecording(recordingId: number, refreshGroups = false) {
  try {
    await recordingApi.deleteRecording(recordingId)
    message.success('录制已删除')
    if (selectedSession.value) {
      await reloadCurrentRecordings()
    }
    if (refreshGroups) {
      await loadRecordingGroups()
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}

async function deleteSelectedSessionRecordings() {
  if (selectedSessionRecordingIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteRecordings({ ids: selectedSessionRecordingIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 条录制`)
    selectedSessionRecordingIds.value = []
    await Promise.all([reloadCurrentRecordings(), loadRecordingGroups()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
  }
}

async function deleteSelectedGroupRecordings() {
  if (selectedGroupRecordingIds.value.length === 0) return
  try {
    const res = await recordingApi.bulkDeleteRecordings({ ids: selectedGroupRecordingIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 条代表样本`)
    selectedGroupRecordingIds.value = []
    await Promise.all([loadRecordingGroups(), reloadCurrentRecordings()])
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
  }
}

function handleSessionSorterChange(sorter: any) {
  sessionSort.value = updateSortState(sorter, 'created_at')
  sessionPagination.page = 1
  void loadSessions()
}

function handleRecordingSorterChange(sorter: any) {
  recordingSort.value = updateSortState(sorter, 'recorded_at')
  recordingPagination.page = 1
  void reloadCurrentRecordings()
}

function handleGroupSorterChange(sorter: any) {
  groupSort.value = updateSortState(sorter, 'latest_recorded_at')
  groupPagination.page = 1
  void loadRecordingGroups()
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

onBeforeUnmount(() => {
  stopSessionCountPolling()
})
</script>

<style scoped>
.recording-page {
  width: 100%;
}

.recording-filter-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.9fr) minmax(0, 1.2fr) minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.recording-filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
}

.recording-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.95fr);
  gap: 16px;
  align-items: start;
}

.recording-grid :deep(.n-card) {
  border-radius: 16px;
}

.recording-grid :deep(.n-card-header) {
  align-items: center;
}

@media (max-width: 1280px) {
  .recording-filter-grid,
  .recording-grid {
    grid-template-columns: 1fr;
  }
}
</style>
