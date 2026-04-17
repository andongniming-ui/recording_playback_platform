<template>
  <n-space vertical :size="16">
    <n-space justify="space-between">
      <n-h2 style="margin:0">测试套件</n-h2>
      <n-space>
        <n-select v-model:value="filterSuiteType" clearable :options="suiteTypeOptions" placeholder="套件类型" style="width: 140px" @update:value="load" />
        <n-button v-if="canEdit" @click="openAutoSmoke">按应用生成冒烟套件</n-button>
        <n-button v-if="canEdit" type="primary" @click="openCreate">+ 新建套件</n-button>
      </n-space>
    </n-space>

    <n-empty v-if="!loading && suites.length === 0" description="暂无测试套件，可先创建一个套件" style="padding: 48px 0" />
    <n-data-table v-else :columns="columns" :data="suites" :loading="loading" :pagination="{ pageSize: 10 }" />
  </n-space>

  <!-- 新建套件弹窗 -->
  <n-modal v-model:show="showCreateModal" title="新建套件" preset="card" style="width:400px">
    <n-form :model="createForm" label-placement="left" label-width="80px">
      <n-form-item label="名称"><n-input v-model:value="createForm.name" /></n-form-item>
      <n-form-item label="类型"><n-select v-model:value="createForm.suite_type" :options="suiteTypeOptions" /></n-form-item>
      <n-form-item label="描述"><n-input v-model:value="createForm.description" type="textarea" :rows="2" /></n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showCreateModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="createSuite">创建</n-button>
      </n-space>
    </template>
  </n-modal>

  <n-modal v-model:show="showAutoSmokeModal" title="按应用生成冒烟套件" preset="card" style="width:460px">
    <n-form :model="autoSmokeForm" label-placement="left" label-width="90px">
      <n-form-item label="所属应用">
        <n-select v-model:value="autoSmokeForm.application_id" :options="appOptions" filterable placeholder="请选择应用" />
      </n-form-item>
      <n-form-item label="套件名称">
        <n-input v-model:value="autoSmokeForm.name" placeholder="可选，默认按应用生成" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="autoSmokeForm.description" type="textarea" :rows="2" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showAutoSmokeModal = false">取消</n-button>
        <n-button type="primary" :loading="autoSmoking" @click="createAutoSmoke">生成</n-button>
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
    <n-select
      v-model:value="selectedCaseIds"
      multiple
      filterable
      :loading="casesLoading"
      :options="caseOptions"
      placeholder="选择用例（可多选）"
    />
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
import { useRouter } from 'vue-router'
import { NSpace, NH2, NButton, NDataTable, NEmpty, NModal, NForm, NFormItem, NInput, NSelect, NTag, NText, NDrawer, NDrawerContent, NPopconfirm, useMessage } from 'naive-ui'
import { suiteApi } from '@/api/suites'
import { formatDateTime } from '@/utils/format'
import { testCaseApi } from '@/api/testcases'
import { applicationApi } from '@/api/applications'
import { useUserStore } from '@/store/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const suites = ref<any[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const showAutoSmokeModal = ref(false)
const showDrawer = ref(false)
const showAddCase = ref(false)
const saving = ref(false)
const running = ref(false)
const autoSmoking = ref(false)
const filterSuiteType = ref<string | null>(null)
const selectedSuite = ref<any>(null)
const suiteDetail = ref<any>(null)
const caseOptions = ref<any[]>([])
const casesLoading = ref(false)
const selectedCaseIds = ref<number[]>([])
const createForm = ref({ name: '', description: '', suite_type: 'regression' })
const autoSmokeForm = ref({ application_id: null as number | null, name: '', description: '' })
const appOptions = ref<any[]>([])

const suiteTypeOptions = [
  { label: '冒烟', value: 'smoke' },
  { label: '回归', value: 'regression' },
]

const suiteTypeLabelMap: Record<string, string> = {
  smoke: '冒烟',
  regression: '回归',
}

const columns = [
  {
    title: '名称',
    key: 'name',
    render: (r: any) => h(NButton, { text: true, type: 'primary', onClick: () => router.push(`/suites/${r.id}`) }, () => r.name),
  },
  { title: '类型', key: 'suite_type', width: 100, render: (r: any) => h(NTag, { size: 'small', type: r.suite_type === 'smoke' ? 'warning' : 'info' }, () => suiteTypeLabelMap[r.suite_type] || r.suite_type || '-') },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '创建时间', key: 'created_at', width: 155, render: (r: any) => formatDateTime(r.created_at) },
  {
    title: '操作', key: 'actions', width: 200,
    render: (r: any) => h(NSpace, { size: 4 }, () => [
      h(NButton, { size: 'tiny', onClick: () => router.push(`/suites/${r.id}`) }, () => '详情'),
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
    suites.value = (await suiteApi.list({ suite_type: filterSuiteType.value || undefined })).data
  } catch (error: any) {
    suites.value = []
    message.error(error.response?.data?.detail || '加载套件失败')
  } finally { loading.value = false }
}

async function loadApps() {
  try {
    const res = await applicationApi.list()
    appOptions.value = res.data.map((app: any) => ({ label: app.name, value: app.id }))
  } catch {
    appOptions.value = []
  }
}

function openCreate() {
  createForm.value = { name: '', description: '', suite_type: 'regression' }
  showCreateModal.value = true
}

async function openAutoSmoke() {
  if (!appOptions.value.length) {
    await loadApps()
  }
  autoSmokeForm.value = { application_id: null, name: '', description: '' }
  showAutoSmokeModal.value = true
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

async function createAutoSmoke() {
  if (!autoSmokeForm.value.application_id) {
    message.warning('请选择应用')
    return
  }
  autoSmoking.value = true
  try {
    const res = await suiteApi.autoSmoke(autoSmokeForm.value)
    message.success(`已生成冒烟套件，包含 ${res.data.added_case_ids.length} 个代表样本`)
    showAutoSmokeModal.value = false
    await load()
    router.push(`/suites/${res.data.suite_id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '生成冒烟套件失败')
  } finally {
    autoSmoking.value = false
  }
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

async function loadCaseOptions() {
  casesLoading.value = true
  try {
    const casesRes = await testCaseApi.list({ limit: 500 })
    caseOptions.value = casesRes.data.map((c: any) => ({
      label: `[${c.request_method}] ${c.name}${c.transaction_code ? ` [${c.transaction_code}]` : ''}`,
      value: c.id,
    }))
  } catch (error: any) {
    caseOptions.value = []
    message.error(error.response?.data?.detail || '加载测试用例失败')
  } finally {
    casesLoading.value = false
  }
}

async function openAddCase() {
  await loadCaseOptions()
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
    showDrawer.value = false
    router.push(`/results/${res.data.job_id}`)
  } catch (error: any) { message.error(error.response?.data?.detail || '运行失败') } finally { running.value = false }
}

async function deleteSuite(id: number) {
  try { await suiteApi.delete(id); message.success('已删除'); await load() } catch (error: any) { message.error(error.response?.data?.detail || '删除失败') }
}

onMounted(async () => {
  await Promise.all([load(), loadApps()])
})
</script>
