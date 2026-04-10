<template>
  <n-space vertical :size="16">
    <n-space justify="space-between">
      <n-h2 style="margin:0">测试套件</n-h2>
      <n-button v-if="canEdit" type="primary" @click="openCreate">+ 新建套件</n-button>
    </n-space>

    <n-data-table :columns="columns" :data="suites" :loading="loading" :pagination="{ pageSize: 10 }" />
  </n-space>

  <!-- 新建套件弹窗 -->
  <n-modal v-model:show="showCreateModal" title="新建套件" preset="card" style="width:400px">
    <n-form :model="createForm" label-placement="left" label-width="80px">
      <n-form-item label="名称"><n-input v-model:value="createForm.name" /></n-form-item>
      <n-form-item label="描述"><n-input v-model:value="createForm.description" type="textarea" :rows="2" /></n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showCreateModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="createSuite">创建</n-button>
      </n-space>
    </template>
  </n-modal>

  <!-- 套件详情抽屉 -->
  <n-drawer v-model:show="showDrawer" :width="680" placement="right">
    <n-drawer-content :title="`套件详情: ${selectedSuite?.name}`" closable>
      <n-space justify="space-between" style="margin-bottom:12px">
        <n-space>
          <n-button v-if="canEdit" size="small" type="primary" @click="openAddCase">添加用例</n-button>
          <n-button v-if="canEdit" size="small" type="success" :loading="running" @click="runSuite">运行套件</n-button>
        </n-space>
        <n-text>共 {{ suiteDetail?.cases?.length || 0 }} 个用例</n-text>
      </n-space>
      <n-data-table :columns="caseCols" :data="suiteDetail?.cases || []" size="small" />
    </n-drawer-content>
  </n-drawer>

  <!-- 添加用例弹窗 -->
  <n-modal v-model:show="showAddCase" title="添加用例到套件" preset="card" style="width:500px">
    <n-select v-model:value="selectedCaseIds" multiple filterable :options="caseOptions" placeholder="选择用例（可多选）" />
    <template #footer>
      <n-space justify="end">
        <n-button @click="showAddCase = false">取消</n-button>
        <n-button type="primary" @click="addCases">添加</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NSpace, NH2, NButton, NDataTable, NModal, NForm, NFormItem, NInput, NSelect, NText, NDrawer, NDrawerContent, NPopconfirm, useMessage } from 'naive-ui'
import { suiteApi } from '@/api/suites'
import { testCaseApi } from '@/api/testcases'
import { useUserStore } from '@/store/user'

const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const suites = ref<any[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const showDrawer = ref(false)
const showAddCase = ref(false)
const saving = ref(false)
const running = ref(false)
const selectedSuite = ref<any>(null)
const suiteDetail = ref<any>(null)
const caseOptions = ref<any[]>([])
const selectedCaseIds = ref<number[]>([])
const createForm = ref({ name: '', description: '' })

const columns = [
  { title: '名称', key: 'name' },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '创建时间', key: 'created_at', width: 155, render: (r: any) => r.created_at?.slice(0, 19).replace('T', ' ') },
  {
    title: '操作', key: 'actions', width: 140,
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => openDetail(r) }, () => '详情'),
      ...(canEdit ? [h(NPopconfirm, { onPositiveClick: () => deleteSuite(r.id) }, {
        default: () => '确认删除?',
        trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
      })] : []),
    ]),
  },
]

const caseCols = [
  { title: '顺序', key: 'order_index', width: 60 },
  { title: '用例ID', key: 'test_case_id', width: 80 },
]

async function load() {
  loading.value = true
  try {
    suites.value = (await suiteApi.list()).data
  } catch (error: any) {
    suites.value = []
    message.error(error.response?.data?.detail || '加载套件失败')
  } finally { loading.value = false }
}

function openCreate() {
  createForm.value = { name: '', description: '' }
  showCreateModal.value = true
}

async function createSuite() {
  saving.value = true
  try {
    await suiteApi.create(createForm.value)
    message.success('套件已创建')
    showCreateModal.value = false
    await load()
  } catch (error: any) { message.error(error.response?.data?.detail || '创建失败') } finally { saving.value = false }
}

async function openDetail(suite: any) {
  selectedSuite.value = suite
  showDrawer.value = true
  try {
    const res = await suiteApi.get(suite.id)
    suiteDetail.value = res.data
  } catch (error: any) {
    suiteDetail.value = null
    message.error(error.response?.data?.detail || '加载套件详情失败')
  }
}

function openAddCase() {
  selectedCaseIds.value = []
  showAddCase.value = true
}

async function addCases() {
  if (!selectedSuite.value || !selectedCaseIds.value.length) return
  const existing = suiteDetail.value?.cases?.map((c: any) => c.test_case_id) || []
  const newIds = [...new Set([...existing, ...selectedCaseIds.value])]
  try {
    await suiteApi.setCases(selectedSuite.value.id, { case_ids: newIds })
    message.success('用例已添加')
    showAddCase.value = false
    await openDetail(selectedSuite.value)
  } catch (error: any) { message.error(error.response?.data?.detail || '添加失败') }
}

async function runSuite() {
  if (!selectedSuite.value) return
  running.value = true
  try {
    const res = await suiteApi.run(selectedSuite.value.id)
    message.success(`回放任务 #${res.data.job_id} 已启动`)
  } catch (error: any) { message.error(error.response?.data?.detail || '运行失败') } finally { running.value = false }
}

async function deleteSuite(id: number) {
  try { await suiteApi.delete(id); message.success('已删除'); await load() } catch (error: any) { message.error(error.response?.data?.detail || '删除失败') }
}

onMounted(async () => {
  try {
    const casesRes = await testCaseApi.list({ limit: 200 })
    caseOptions.value = casesRes.data.map((c: any) => ({ label: `[${c.request_method}] ${c.name}`, value: c.id }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载测试用例失败')
  }
  await load()
})
</script>
