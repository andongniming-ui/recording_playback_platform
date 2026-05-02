<template>
  <n-space vertical :size="16">
    <n-space justify="space-between">
      <n-h2 style="margin:0">定时任务</n-h2>
      <n-space>
        <n-button
          v-if="canEdit && selectedScheduleIds.length > 0"
          type="error"
          @click="deleteSelectedSchedules"
        >
          批量删除{{ selectedScheduleIds.length > 0 ? ` (${selectedScheduleIds.length})` : '' }}
        </n-button>
        <n-button v-if="canEdit" type="primary" @click="openCreate">+ 新增任务</n-button>
      </n-space>
    </n-space>

    <n-data-table
      :columns="columns"
      :data="schedules"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row: any) => row.id"
      remote
      v-model:checked-row-keys="selectedScheduleIds"
      @update:sorter="handleSorterChange"
    />
  </n-space>

  <n-modal v-model:show="showModal" :title="editingId ? '编辑定时任务' : '新增定时任务'" preset="card" style="width:560px">
    <n-form :model="form" label-placement="left" label-width="120px">
      <n-form-item label="任务名称"><n-input v-model:value="form.name" /></n-form-item>
      <n-form-item label="关联套件">
        <n-select v-model:value="form.suite_id" :options="suiteOptions" clearable placeholder="选择套件" />
      </n-form-item>
      <n-form-item label="Cron 表达式">
        <n-input v-model:value="form.cron_expr" placeholder="如: 0 9 * * * (每天9点)" />
      </n-form-item>
      <n-form-item label="通知类型">
        <n-select v-model:value="form.notify_type" :options="notifyOpts" clearable />
      </n-form-item>
      <n-form-item label="Webhook URL">
        <n-input v-model:value="form.notify_webhook" placeholder="钉钉/企微 Webhook 地址" />
      </n-form-item>
      <n-form-item label="是否启用">
        <n-switch v-model:value="form.is_active" />
      </n-form-item>
    </n-form>
    <n-alert type="info" style="margin-top:8px">
      Cron 格式：分 时 日 月 周，例：<br/>
      <code>0 9 * * *</code> — 每天9点<br/>
      <code>0 */2 * * *</code> — 每2小时<br/>
      <code>0 9 * * 1</code> — 每周一9点
    </n-alert>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="save">保存</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NSpace, NH2, NButton, NDataTable, NModal, NForm, NFormItem, NInput, NSelect, NSwitch, NAlert, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { scheduleApi } from '@/api/schedules'
import { formatDateTime } from '@/utils/format'
import { suiteApi } from '@/api/suites'
import { useUserStore } from '@/store/user'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData } from '@/utils/pagination'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const schedules = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const suiteOptions = ref<any[]>([])
const selectedScheduleIds = ref<(string | number)[]>([])
const sortState = ref(defaultSortState('last_run_at'))
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 个任务`,
  onUpdatePage: (page: number) => {
    pagination.page = page
    void load()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    void load()
  },
})

const notifyOpts = [
  { label: '钉钉', value: 'dingtalk' },
  { label: '企业微信', value: 'wecom' },
  { label: '不通知', value: 'none' },
]
const notifyLabelMap: Record<string, string> = {
  dingtalk: '钉钉', wecom: '企业微信', none: '不通知', generic: '通用',
}
const lastRunStatusTypeMap: Record<string, any> = {
  DONE: 'success', FAILED: 'error', RUNNING: 'info', PENDING: 'default', CANCELLED: 'warning',
}
const lastRunStatusLabelMap: Record<string, string> = {
  DONE: '已完成', FAILED: '存在失败', RUNNING: '运行中', PENDING: '待执行', CANCELLED: '已取消',
}

const form = ref({ name: '', suite_id: null as number | null, cron_expr: '0 9 * * *', is_active: true, notify_type: null as string | null, notify_webhook: '' })

const columns = computed(() => [
  ...(canEdit ? [{ type: 'selection' as const }] : []),
  { title: '名称', key: 'name' },
  { title: 'Cron', key: 'cron_expr', width: 140 },
  {
    title: '状态', key: 'is_active', width: 80,
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '启用' : '停用'),
  },
  { title: '通知', key: 'notify_type', width: 80, render: (r: any) => notifyLabelMap[r.notify_type] || r.notify_type || '-' },
  {
    title: '上次运行',
    key: 'last_run_at',
    width: 155,
    sorter: true,
    sortOrder: resolveSortOrder(sortState.value, 'last_run_at'),
    render: (r: any) => formatDateTime(r.last_run_at),
  },
  {
    title: '上次结果', key: 'last_run_status', width: 90,
    render: (r: any) => r.last_run_status
      ? h(NTag, { type: lastRunStatusTypeMap[r.last_run_status] || 'default', size: 'small' }, () => lastRunStatusLabelMap[r.last_run_status] || r.last_run_status)
      : '-',
  },
  {
    title: '操作', key: 'actions', width: 180,
    render: (r: any) => canEdit ? h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', type: 'info', onClick: () => triggerNow(r.id) }, () => '立即触发'),
      h(NButton, { size: 'tiny', onClick: () => openEdit(r) }, () => '编辑'),
      h(NPopconfirm, { onPositiveClick: () => deleteSchedule(r.id) }, {
        default: () => '确认删除?',
        trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
      }),
    ]) : null,
  },
])

async function load() {
  loading.value = true
  try {
    const page = await loadPagedData<any>(scheduleApi.list, {
      sort_by: sortState.value.columnKey,
      sort_order: toApiSortOrder(sortState.value.order),
    }, pagination.page, pagination.pageSize, 100)
    schedules.value = page.items
    pagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && pagination.page > 1) {
      pagination.page = lastValidPage(page.total, pagination.pageSize)
      void load()
      return
    }
    selectedScheduleIds.value = []
  } catch (error: any) {
    schedules.value = []
    pagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载定时任务失败')
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  Object.assign(form.value, { name: '', suite_id: null, cron_expr: '0 9 * * *', is_active: true, notify_type: null, notify_webhook: '' })
  showModal.value = true
}

function openEdit(s: any) {
  editingId.value = s.id
  Object.assign(form.value, s)
  showModal.value = true
}

async function save() {
  if (!form.value.suite_id) {
    message.warning('请选择关联套件')
    return
  }
  saving.value = true
  try {
    if (editingId.value) await scheduleApi.update(editingId.value, form.value)
    else await scheduleApi.create(form.value)
    message.success('保存成功')
    showModal.value = false
    await load()
  } catch (error: any) { message.error(error.response?.data?.detail || '保存失败') } finally { saving.value = false }
}

async function deleteSchedule(id: number) {
  try { await scheduleApi.delete(id); message.success('已删除'); await load() } catch (error: any) { message.error(error.response?.data?.detail || '删除失败') }
}

async function deleteSelectedSchedules() {
  if (selectedScheduleIds.value.length === 0) return
  try {
    const res = await scheduleApi.bulkDelete({ ids: selectedScheduleIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 个定时任务`)
    await load()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
  }
}

function handleSorterChange(sorter: any) {
  sortState.value = updateSortState(sorter, 'last_run_at')
  pagination.page = 1
  void load()
}

async function triggerNow(id: number) {
  try {
    await scheduleApi.trigger(id)
    message.success('已触发，可到回放历史查看执行进度')
    router.push('/replay/history')
  } catch (error: any) { message.error(error.response?.data?.detail || '触发失败') }
}

onMounted(async () => {
  try {
    const suitesRes = await suiteApi.list({ limit: 100 })
    suiteOptions.value = suitesRes.data.map((s: any) => ({ label: s.name, value: s.id }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载套件列表失败')
  }
  await load()
})
</script>
