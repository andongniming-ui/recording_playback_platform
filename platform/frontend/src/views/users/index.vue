<template>
  <n-space vertical :size="16">
    <n-space justify="space-between">
      <n-h2 style="margin:0">用户管理</n-h2>
      <n-space>
        <n-button
          v-if="selectedUserIds.length > 0"
          type="error"
          @click="deleteSelectedUsers"
        >
          批量删除{{ selectedUserIds.length > 0 ? ` (${selectedUserIds.length})` : '' }}
        </n-button>
        <n-button type="primary" @click="openCreate">+ 新增用户</n-button>
      </n-space>
    </n-space>
    <n-data-table
      :columns="columns"
      :data="users"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row: any) => row.id"
      remote
      v-model:checked-row-keys="selectedUserIds"
      @update:sorter="handleSorterChange"
    />
  </n-space>

  <n-modal v-model:show="showModal" :title="editingId ? '编辑用户' : '新增用户'" preset="card" style="width:440px">
    <n-form ref="formRef" :model="form" :rules="formRules" label-placement="left" label-width="80px">
      <n-form-item v-if="!editingId" label="用户名" path="username">
        <n-input v-model:value="form.username" placeholder="登录用户名" />
      </n-form-item>
      <n-form-item label="角色">
        <n-select v-model:value="form.role" :options="roleOpts" />
      </n-form-item>
      <n-form-item label="密码" path="password">
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
import { computed, reactive, ref, onMounted, h } from 'vue'
import { NSpace, NH2, NButton, NDataTable, NTag, NModal, NForm, NFormItem, NInput, NSelect, NSwitch, NText, NPopconfirm, useMessage } from 'naive-ui'
import { userApi } from '@/api/users'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'
import { defaultSortState, resolveSortOrder, toApiSortOrder, updateSortState } from '@/utils/tableSort'
import { lastValidPage, loadPagedData } from '@/utils/pagination'

const message = useMessage()
const userStore = useUserStore()
const users = ref<any[]>([])
const loading = ref(false)
const selectedUserIds = ref<(string | number)[]>([])
const sortState = ref(defaultSortState('created_at'))
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 个用户`,
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
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()
const form = ref({ username: '', role: 'viewer', password: '', is_active: true })

const formRules = computed(() => ({
  username: editingId.value ? [] : [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: editingId.value ? [] : [{ required: true, message: '请设置密码', trigger: 'blur' }],
}))

const roleOpts = [
  { label: '管理员', value: 'admin' },
  { label: '编辑者', value: 'editor' },
  { label: '只读', value: 'viewer' },
]
const roleColors: Record<string, any> = { admin: 'error', editor: 'warning', viewer: 'default' }

const columns = computed(() => [
  { type: 'selection' as const, disabled: (row: any) => row.username === userStore.username },
  { title: '用户名', key: 'username' },
  {
    title: '角色', key: 'role', width: 90,
    render: (r: any) => h(NTag, { type: roleColors[r.role] || 'default', size: 'small' }, () => r.role),
  },
  {
    title: '状态', key: 'is_active', width: 80,
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '启用' : '停用'),
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 155,
    sorter: true,
    sortOrder: resolveSortOrder(sortState.value, 'created_at'),
    render: (r: any) => formatDateTime(r.created_at),
  },
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
])

async function load() {
  loading.value = true
  try {
    const page = await loadPagedData<any>(userApi.list, {
      sort_by: sortState.value.columnKey,
      sort_order: toApiSortOrder(sortState.value.order),
    }, pagination.page, pagination.pageSize, 100)
    users.value = page.items
    pagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && pagination.page > 1) {
      pagination.page = lastValidPage(page.total, pagination.pageSize)
      void load()
      return
    }
    selectedUserIds.value = []
  } catch (error: any) {
    users.value = []
    pagination.itemCount = 0
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
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
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

async function deleteSelectedUsers() {
  if (selectedUserIds.value.length === 0) return
  try {
    const res = await userApi.bulkDelete({ ids: selectedUserIds.value.map(Number) })
    message.success(`已删除 ${res.data.deleted} 个用户`)
    await load()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '批量删除失败')
  }
}

function handleSorterChange(sorter: any) {
  sortState.value = updateSortState(sorter, 'created_at')
  pagination.page = 1
  void load()
}

onMounted(load)
</script>
