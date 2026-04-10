<template>
  <n-space vertical :size="16">
    <n-space justify="space-between">
      <n-h2 style="margin:0">定时任务</n-h2>
      <n-button v-if="canEdit" type="primary" @click="openCreate">+ 新增任务</n-button>
    </n-space>

    <n-data-table :columns="columns" :data="schedules" :loading="loading" :pagination="{ pageSize: 10 }" />
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
import { ref, onMounted, h } from 'vue'
import { NSpace, NH2, NButton, NDataTable, NModal, NForm, NFormItem, NInput, NSelect, NSwitch, NAlert, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { scheduleApi } from '@/api/schedules'
import { suiteApi } from '@/api/suites'
import { useUserStore } from '@/store/user'

const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const schedules = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const suiteOptions = ref<any[]>([])

const notifyOpts = [
  { label: '钉钉', value: 'dingtalk' },
  { label: '企业微信', value: 'wecom' },
  { label: '不通知', value: 'none' },
]

const form = ref({ name: '', suite_id: null as number | null, cron_expr: '0 9 * * *', is_active: true, notify_type: null as string | null, notify_webhook: '' })

const columns = [
  { title: '名称', key: 'name' },
  { title: 'Cron', key: 'cron_expr', width: 140 },
  {
    title: '状态', key: 'is_active', width: 80,
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '启用' : '停用'),
  },
  { title: '通知', key: 'notify_type', width: 80, render: (r: any) => r.notify_type || '-' },
  { title: '上次运行', key: 'last_run_at', width: 155, render: (r: any) => r.last_run_at?.slice(0, 19).replace('T', ' ') || '-' },
  {
    title: '上次结果', key: 'last_run_status', width: 90,
    render: (r: any) => r.last_run_status ? h(NTag, { type: r.last_run_status === 'DONE' ? 'success' : 'error', size: 'small' }, () => r.last_run_status) : '-',
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
]

async function load() {
  loading.value = true
  try {
    schedules.value = (await scheduleApi.list()).data
  } catch (error: any) {
    schedules.value = []
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

async function triggerNow(id: number) {
  try { await scheduleApi.trigger(id); message.success('已触发') } catch (error: any) { message.error(error.response?.data?.detail || '触发失败') }
}

onMounted(async () => {
  try {
    const suitesRes = await suiteApi.list()
    suiteOptions.value = suitesRes.data.map((s: any) => ({ label: s.name, value: s.id }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载套件列表失败')
  }
  await load()
})
</script>
