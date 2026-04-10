<template>
  <n-space vertical :size="12">
    <n-space justify="space-between">
      <n-h2 style="margin: 0">应用管理</n-h2>
      <n-button v-if="canEdit" type="primary" @click="openCreate">+ 新增应用</n-button>
    </n-space>

    <n-data-table
      :columns="columns"
      :data="apps"
      :loading="loading"
      :pagination="{ pageSize: 10 }"
    />
  </n-space>

  <n-modal
    v-model:show="showModal"
    :title="editingId ? '编辑应用' : '新增应用'"
    preset="card"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="form" label-placement="left" label-width="120px">
      <n-form-item label="应用名称" path="name" :rule="{ required: true, message: '请输入应用名称' }">
        <n-input v-model:value="form.name" placeholder="例如：demo-service" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="form.description" placeholder="可选" />
      </n-form-item>
      <n-form-item label="SSH 主机" path="ssh_host" :rule="{ required: true, message: '请输入 SSH 主机' }">
        <n-input v-model:value="form.ssh_host" placeholder="IP 或域名" />
      </n-form-item>
      <n-form-item label="SSH 用户" path="ssh_user" :rule="{ required: true, message: '请输入 SSH 用户' }">
        <n-input v-model:value="form.ssh_user" placeholder="例如：ubuntu" />
      </n-form-item>
      <n-form-item label="SSH 端口">
        <n-input-number v-model:value="form.ssh_port" />
      </n-form-item>
      <n-form-item label="SSH 密钥路径">
        <n-input v-model:value="form.ssh_key_path" placeholder="/path/to/key" />
      </n-form-item>
      <n-form-item label="SSH 密码">
        <n-input v-model:value="form.ssh_password" type="password" />
      </n-form-item>
      <n-form-item label="服务端口">
        <n-input-number v-model:value="form.service_port" />
      </n-form-item>
      <n-form-item label="JVM 进程名">
        <n-input v-model:value="form.jvm_process_name" placeholder="用于 pgrep 识别" />
      </n-form-item>
      <n-form-item label="AREX App ID">
        <n-input v-model:value="form.arex_app_id" />
      </n-form-item>
      <n-form-item label="AREX Storage 地址">
        <n-input v-model:value="form.arex_storage_url" placeholder="留空则使用全局配置" />
      </n-form-item>
      <n-form-item label="采样率">
        <n-slider v-model:value="form.sample_rate" :min="0" :max="1" :step="0.1" style="width: 200px" />
        <n-text style="margin-left: 12px">{{ form.sample_rate }}</n-text>
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="save">保存</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import {
  NButton,
  NDataTable,
  NForm,
  NFormItem,
  NH2,
  NInput,
  NInputNumber,
  NModal,
  NPopconfirm,
  NSlider,
  NSpace,
  NTag,
  NText,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { useUserStore } from '@/store/user'

type AppRow = {
  id: number
  name: string
  ssh_host: string
  service_port: number
  agent_status?: string | null
  created_at?: string
}

type AppForm = {
  name: string
  description: string
  ssh_host: string
  ssh_user: string
  ssh_port: number
  ssh_key_path: string
  ssh_password: string
  service_port: number
  jvm_process_name: string
  arex_app_id: string
  arex_storage_url: string
  sample_rate: number
}

const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const apps = ref<AppRow[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()
const form = ref<AppForm>(createEmptyForm())

function normalizeAgentStatus(status?: string | null) {
  const value = (status || 'unknown').toLowerCase()
  if (value === 'attached' || value === 'online' || value === 'already_injected') {
    return 'online'
  }
  if (value === 'detached' || value === 'offline') {
    return 'offline'
  }
  if (value === 'mounting') {
    return 'mounting'
  }
  if (value === 'error') {
    return 'error'
  }
  return 'unknown'
}

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

const columns: DataTableColumns<AppRow> = [
  { title: '名称', key: 'name' },
  { title: 'SSH 主机', key: 'ssh_host' },
  { title: '服务端口', key: 'service_port', width: 90 },
  {
    title: 'Agent 状态',
    key: 'agent_status',
    width: 110,
    render: (row) => {
      const normalizedStatus = normalizeAgentStatus(row.agent_status)
      return h(
        NTag,
        {
          type: statusTypeMap[normalizedStatus] || 'default',
          size: 'small',
        },
        () => statusLabelMap[normalizedStatus] || '未知',
      )
    },
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
    render: (row) => {
      const normalizedStatus = normalizeAgentStatus(row.agent_status)
      return h(NSpace, { size: 4 }, () => [
        ...(canEdit ? [
          h(NButton, { size: 'tiny', onClick: () => testConn(row.id) }, () => '连接测试'),
          normalizedStatus === 'online'
            ? h(NButton, { size: 'tiny', type: 'warning', onClick: () => unmount(row.id) }, () => '卸载 Agent')
            : h(NButton, { size: 'tiny', type: 'info', onClick: () => mount(row.id) }, () => '挂载 Agent'),
          h(NButton, { size: 'tiny', onClick: () => openEdit(row) }, () => '编辑'),
        ] : []),
        ...(userStore.role === 'admin'
          ? [h(
              NPopconfirm,
              { onPositiveClick: () => deleteApp(row.id) },
              {
                default: () => '确认删除？',
                trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
              },
            )]
          : []),
      ])
    },
  },
]

function createEmptyForm(): AppForm {
  return {
    name: '',
    description: '',
    ssh_host: '',
    ssh_user: '',
    ssh_port: 22,
    ssh_key_path: '',
    ssh_password: '',
    service_port: 8080,
    jvm_process_name: '',
    arex_app_id: '',
    arex_storage_url: '',
    sample_rate: 1.0,
  }
}

function formatDateTime(value?: string) {
  return value ? value.slice(0, 19).replace('T', ' ') : '-'
}

async function loadApps() {
  loading.value = true
  try {
    const res = await applicationApi.list()
    apps.value = res.data
  } catch (error: any) {
    apps.value = []
    message.error(error.response?.data?.detail || '加载应用列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = createEmptyForm()
}

function openCreate() {
  editingId.value = null
  resetForm()
  showModal.value = true
}

function openEdit(app: Record<string, any>) {
  editingId.value = app.id
  form.value = {
    ...createEmptyForm(),
    ...app,
  }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    if (editingId.value) {
      await applicationApi.update(editingId.value, form.value)
    } else {
      await applicationApi.create(form.value)
    }
    message.success('保存成功')
    showModal.value = false
    await loadApps()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function testConn(id: number) {
  try {
    const res = await applicationApi.testConnection(id)
    if (res.data.success) {
      message.success('SSH 连接成功')
    } else {
      message.error(`连接失败：${res.data.message}`)
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '连接测试失败')
  }
}

async function mount(id: number) {
  try {
    await applicationApi.mountAgent(id)
    message.info('Agent 挂载已启动，请稍候...')
    setTimeout(() => { void loadApps() }, 3000)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '挂载失败')
  }
}

async function unmount(id: number) {
  try {
    await applicationApi.unmountAgent(id)
    message.success('Agent 已卸载')
    await loadApps()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '卸载失败')
  }
}

async function deleteApp(id: number) {
  try {
    await applicationApi.delete(id)
    message.success('删除成功')
    await loadApps()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(loadApps)
</script>
