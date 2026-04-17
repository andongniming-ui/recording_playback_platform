<template>
  <n-space vertical :size="16">
    <n-space justify="space-between">
      <n-h2 style="margin:0">用户管理</n-h2>
      <n-button type="primary" @click="openCreate">+ 新增用户</n-button>
    </n-space>
    <n-data-table :columns="columns" :data="users" :loading="loading" :pagination="{ pageSize: 10 }" />
  </n-space>

  <n-modal v-model:show="showModal" :title="editingId ? '编辑用户' : '新增用户'" preset="card" style="width:440px">
    <n-form :model="form" label-placement="left" label-width="80px">
      <n-form-item v-if="!editingId" label="用户名">
        <n-input v-model:value="form.username" placeholder="登录用户名" />
      </n-form-item>
      <n-form-item label="角色">
        <n-select v-model:value="form.role" :options="roleOpts" />
      </n-form-item>
      <n-form-item label="密码">
        <n-input v-model:value="form.password" type="password" :placeholder="editingId ? '留空不修改' : '设置密码'" />
      </n-form-item>
      <n-form-item v-if="editingId" label="状态">
        <n-switch v-model:value="form.is_active" />
        <n-text style="margin-left:8px">{{ form.is_active ? '启用' : '停用' }}</n-text>
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
import { NSpace, NH2, NButton, NDataTable, NTag, NModal, NForm, NFormItem, NInput, NSelect, NSwitch, NText, NPopconfirm, useMessage } from 'naive-ui'
import { userApi } from '@/api/users'
import { formatDateTime } from '@/utils/format'

const message = useMessage()
const users = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref({ username: '', role: 'viewer', password: '', is_active: true })

const roleOpts = [
  { label: '管理员', value: 'admin' },
  { label: '编辑者', value: 'editor' },
  { label: '只读', value: 'viewer' },
]
const roleColors: Record<string, any> = { admin: 'error', editor: 'warning', viewer: 'default' }

const columns = [
  { title: '用户名', key: 'username' },
  {
    title: '角色', key: 'role', width: 90,
    render: (r: any) => h(NTag, { type: roleColors[r.role] || 'default', size: 'small' }, () => r.role),
  },
  {
    title: '状态', key: 'is_active', width: 80,
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '启用' : '停用'),
  },
  { title: '创建时间', key: 'created_at', width: 155, render: (r: any) => formatDateTime(r.created_at) },
  {
    title: '操作', key: 'actions', width: 120,
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => openEdit(r) }, () => '编辑'),
      h(NPopconfirm, { onPositiveClick: () => deleteUser(r.id) }, {
        default: () => '确认删除?',
        trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
      }),
    ]),
  },
]

async function load() {
  loading.value = true
  try {
    users.value = (await userApi.list()).data
  } catch (error: any) {
    users.value = []
    message.error(error.response?.data?.detail || '加载用户列表失败')
  } finally { loading.value = false }
}

function openCreate() {
  editingId.value = null
  form.value = { username: '', role: 'viewer', password: '', is_active: true }
  showModal.value = true
}

function openEdit(u: any) {
  editingId.value = u.id
  form.value = { username: u.username, role: u.role, password: '', is_active: u.is_active }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    const payload: any = { role: form.value.role, is_active: form.value.is_active }
    if (form.value.password) payload.password = form.value.password
    if (editingId.value) {
      await userApi.update(editingId.value, payload)
    } else {
      await userApi.create({ username: form.value.username, role: form.value.role, password: form.value.password })
    }
    message.success('保存成功')
    showModal.value = false
    await load()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally { saving.value = false }
}

async function deleteUser(id: number) {
  try {
    await userApi.delete(id)
    message.success('已删除')
    await load()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(load)
</script>
