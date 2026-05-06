<template>
  <n-space vertical :size="16">
    <n-card title="系统配置说明">
      <n-alert type="info">
        系统配置通过环境变量或 <code>.env</code> 文件设置，修改后需重启后端服务。
      </n-alert>
      <n-descriptions bordered :column="1" style="margin-top:16px">
        <n-descriptions-item label="AREX Storage URL">
          <n-text code>AR_AREX_STORAGE_URL</n-text> — 默认 http://127.0.0.1:8000
        </n-descriptions-item>
        <n-descriptions-item label="数据库类型">
          <n-text code>AR_DB_TYPE</n-text> — sqlite / mysql
        </n-descriptions-item>
        <n-descriptions-item label="数据库 URL">
          <n-text code>AR_DB_URL</n-text> — 完整连接字符串
        </n-descriptions-item>
        <n-descriptions-item label="JWT 密钥">
          <n-text code>AR_SECRET_KEY</n-text> — 生产环境务必修改
        </n-descriptions-item>
        <n-descriptions-item label="默认 Agent JAR">
          <n-text code>AR_AREX_AGENT_JAR_PATH</n-text> — 默认 /opt/arex/arex-agent.jar
        </n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="脱敏规则管理">
      <template #header-extra>
        <n-button v-if="canEdit" size="small" type="primary" @click="openCreate">+ 新增规则</n-button>
      </template>
      <n-data-table :columns="columns" :data="rules" :loading="loading" size="small" :pagination="pagination" remote />
    </n-card>
  </n-space>

  <n-modal v-model:show="showModal" title="新增脱敏规则" preset="card" style="width:480px">
    <n-form :model="form" label-placement="left" label-width="100px">
      <n-form-item label="规则名称"><n-input v-model:value="form.name" /></n-form-item>
      <n-form-item label="字段名称">
        <n-input v-model:value="form.config" placeholder='如: {"key": "password"} 或 {"key_regex": ".*secret.*"}' type="textarea" :rows="3" />
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
import { reactive, ref, onMounted, h } from 'vue'
import { NSpace, NCard, NAlert, NDescriptions, NDescriptionsItem, NText, NButton, NDataTable, NTag, NModal, NForm, NFormItem, NInput, NPopconfirm, useMessage } from 'naive-ui'
import { compareApi } from '@/api/compare'
import { useUserStore } from '@/store/user'
import { lastValidPage, loadPagedData } from '@/utils/pagination'

const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const rules = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const form = ref({ name: '', scope: 'global', rule_type: 'ignore', config: '', is_active: true })
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条规则`,
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

const columns = [
  { title: '规则名称', key: 'name' },
  { title: '配置', key: 'config', ellipsis: { tooltip: true } },
  {
    title: '状态', key: 'is_active', width: 70,
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '启用' : '停用'),
  },
  {
    title: '操作', key: 'actions', width: 80,
    render: (r: any) => canEdit ? h(NPopconfirm, { onPositiveClick: () => deleteRule(r.id) }, {
      default: () => '确认删除?',
      trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
    }) : null,
  },
]

async function load() {
  loading.value = true
  try {
    const page = await loadPagedData<any>(compareApi.list, { rule_type: 'ignore' }, pagination.page, pagination.pageSize, 100)
    rules.value = page.items
    pagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && pagination.page > 1) {
      pagination.page = lastValidPage(page.total, pagination.pageSize)
      void load()
      return
    }
  } catch (error: any) {
    rules.value = []
    pagination.itemCount = 0
    message.error(error.response?.data?.detail || '加载脱敏规则失败')
  } finally { loading.value = false }
}

function openCreate() {
  form.value = { name: '', scope: 'global', rule_type: 'ignore', config: '', is_active: true }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    await compareApi.create(form.value)
    message.success('规则已创建')
    showModal.value = false
    await load()
  } catch (error: any) { message.error(error.response?.data?.detail || '创建失败') } finally { saving.value = false }
}

async function deleteRule(id: number) {
  try { await compareApi.delete(id); message.success('已删除'); await load() } catch (error: any) { message.error(error.response?.data?.detail || '删除失败') }
}

onMounted(load)
</script>
