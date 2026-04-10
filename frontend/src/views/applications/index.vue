<template>
  <n-space vertical :size="12">
    <n-space justify="space-between">
      <n-h2 style="margin:0">应用管理</n-h2>
      <n-button type="primary" @click="openCreate">+ 新增应用</n-button>
    </n-space>

    <n-data-table
      :columns="columns"
      :data="apps"
      :loading="loading"
      :pagination="{ pageSize: 10 }"
    />
  </n-space>

  <!-- 新增/编辑弹窗 -->
  <n-modal
    v-model:show="showModal"
    :title="editingId ? '编辑应用' : '新增应用'"
    preset="card"
    style="width:600px"
  >
    <n-form ref="formRef" :model="form" label-placement="left" label-width="120px">
      <n-form-item label="应用名称" path="name" :rule="{ required: true, message: '请输入应用名称' }">
        <n-input v-model:value="form.name" placeholder="如: demo-service" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="form.description" placeholder="可选" />
      </n-form-item>
      <n-form-item label="SSH 主机" path="ssh_host" :rule="{ required: true, message: '请输入SSH主机' }">
        <n-input v-model:value="form.ssh_host" placeholder="IP或域名" />
      </n-form-item>
      <n-form-item label="SSH 用户" path="ssh_user" :rule="{ required: true, message: '请输入SSH用户' }">
        <n-input v-model:value="form.ssh_user" placeholder="如: ubuntu" />
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
      <n-form-item label="AREX Storage URL">
        <n-input v-model:value="form.arex_storage_url" placeholder="留空使用全局配置" />
      </n-form-item>
      <n-form-item label="采样率">
        <n-slider v-model:value="form.sample_rate" :min="0" :max="1" :step="0.1" style="width:200px" />
        <n-text style="margin-left:12px">{{ form.sample_rate }}</n-text>
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
import { ref, onMounted, h } from 'vue'
import {
  NSpace, NH2, NButton, NDataTable, NModal, NForm, NFormItem, NInput,
  NInputNumber, NSlider, NText, NTag, NPopconfirm, useMessage
} from 'naive-ui'
import { applicationApi } from '@/api/applications'

const message = useMessage()
const apps = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()
const form = ref({
  name: '', description: '', ssh_host: '', ssh_user: '', ssh_port: 22,
  ssh_key_path: '', ssh_password: '', service_port: 8080,
  jvm_process_name: '', arex_app_id: '', arex_storage_url: '', sample_rate: 1.0,
})

const statusTypeMap: Record<string, any> = {
  online: 'success', offline: 'error', mounting: 'warning', unknown: 'default',
}

const columns = [
  { title: '名称', key: 'name' },
  { title: 'SSH主机', key: 'ssh_host' },
  { title: '服务端口', key: 'service_port', width: 90 },
  {
    title: 'Agent状态', key: 'agent_status', width: 110,
    render: (r: any) => h(NTag, {
      type: statusTypeMap[r.agent_status] || 'default',
      size: 'small',
    }, () => r.agent_status || 'unknown'),
  },
  { title: '创建时间', key: 'created_at', width: 160, render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' ') },
  {
    title: '操作', key: 'actions',
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => testConn(r.id) }, () => '连接测试'),
      r.agent_status === 'online'
        ? h(NButton, { size: 'tiny', type: 'warning', onClick: () => unmount(r.id) }, () => '卸载Agent')
        : h(NButton, { size: 'tiny', type: 'info', onClick: () => mount(r.id) }, () => '挂载Agent'),
      h(NButton, { size: 'tiny', onClick: () => openEdit(r) }, () => '编辑'),
      h(NPopconfirm, { onPositiveClick: () => deleteApp(r.id) }, {
        default: () => '确认删除?',
        trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
      }),
    ]),
  },
]

async function loadApps() {
  loading.value = true
  try {
    const res = await applicationApi.list()
    apps.value = res.data
  } catch {
    message.error('加载应用列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    name: '', description: '', ssh_host: '', ssh_user: '', ssh_port: 22,
    ssh_key_path: '', ssh_password: '', service_port: 8080,
    jvm_process_name: '', arex_app_id: '', arex_storage_url: '', sample_rate: 1.0,
  }
}

function openCreate() {
  editingId.value = null
  resetForm()
  showModal.value = true
}

function openEdit(app: any) {
  editingId.value = app.id
  Object.assign(form.value, app)
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
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function testConn(id: number) {
  try {
    const res = await applicationApi.testConnection(id)
    if (res.data.success) message.success('SSH 连接成功')
    else message.error('连接失败: ' + res.data.message)
  } catch {
    message.error('连接测试失败')
  }
}

async function mount(id: number) {
  try {
    await applicationApi.mountAgent(id)
    message.info('Agent 挂载已启动，请稍候...')
    setTimeout(loadApps, 3000)
  } catch {
    message.error('挂载失败')
  }
}

async function unmount(id: number) {
  try {
    await applicationApi.unmountAgent(id)
    message.success('Agent 已卸载')
    await loadApps()
  } catch {
    message.error('卸载失败')
  }
}

async function deleteApp(id: number) {
  try {
    await applicationApi.delete(id)
    message.success('删除成功')
    await loadApps()
  } catch {
    message.error('删除失败')
  }
}

onMounted(loadApps)
</script>
