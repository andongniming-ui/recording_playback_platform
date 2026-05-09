<template>
  <n-space vertical :size="16">
    <n-grid cols="1 l:2" responsive="screen" :x-gap="16">
      <!-- 左：对比规则管理 -->
      <n-grid-item>
        <n-card title="对比规则管理">
          <template #header-extra>
            <n-button v-if="canEdit" size="small" type="primary" @click="openCreate">+ 新增规则</n-button>
          </template>
          <n-data-table :columns="ruleColumns" :data="rules" :loading="ruleLoading" size="small" :pagination="rulePagination" remote />
        </n-card>
      </n-grid-item>

      <!-- 右：Diff 查看器 -->
      <n-grid-item>
      <n-card title="响应差异查看">
        <n-space vertical :size="8">
          <n-input v-model:value="resultId" placeholder="输入回放结果 ID" style="width:200px" />
          <n-button type="primary" @click="loadDiff">查看 Diff</n-button>
          <n-alert v-if="!diffData" type="info" :show-icon="false" style="font-size:13px;line-height:2">
            <strong>使用步骤：</strong><br />
            ① 在「结果明细」页找到某条回放记录，复制其 <strong>结果 ID</strong>（Result ID）<br />
            ② 将 ID 填入上方输入框，点击「查看 Diff」<br />
            ③ 即可对比期望响应与实际响应，并查看差异字段详情
          </n-alert>
          <template v-if="diffData">
              <n-grid cols="1 l:2" responsive="screen" :x-gap="8" style="margin-top:8px">
                <n-grid-item>
                  <n-text strong>期望响应</n-text>
                  <pre style="background:#f5f5f5;padding:8px;border-radius:4px;font-size:12px;max-height:400px;overflow:auto;white-space:pre-wrap">{{ rawText(diffData.expected_response) }}</pre>
                </n-grid-item>
                <n-grid-item>
                  <n-text strong>实际响应</n-text>
                  <pre style="background:#fff0f0;padding:8px;border-radius:4px;font-size:12px;max-height:400px;overflow:auto;white-space:pre-wrap">{{ rawText(diffData.actual_response) }}</pre>
                </n-grid-item>
              </n-grid>
              <n-card v-if="diffData.diff_result" title="差异详情" size="small" style="margin-top:8px">
                <pre style="background:#fffbe6;padding:8px;border-radius:4px;font-size:12px;max-height:300px;overflow:auto;white-space:pre-wrap;color:#d03050">{{ formatJson(diffData.diff_result) }}</pre>
              </n-card>
              <n-card v-if="sourceRecording" title="来源录制链路" size="small" style="margin-top:8px">
                <template #header-extra>
                  <n-space align="center" :size="8">
                    <n-tag type="info" size="small">来源用例 #{{ sourceTestCase?.id || '-' }}</n-tag>
                    <n-button v-if="sourceRecording.id" size="small" @click="router.push(`/recording/recordings/${sourceRecording.id}`)">
                      打开录制详情
                    </n-button>
                  </n-space>
                </template>
                <n-descriptions bordered :column="2" size="small">
                  <n-descriptions-item label="请求">{{ sourceRecording.request_method }} {{ sourceRecording.request_uri }}</n-descriptions-item>
                  <n-descriptions-item label="交易码">{{ sourceRecording.transaction_code || '-' }}</n-descriptions-item>
                  <n-descriptions-item label="治理状态">{{ sourceRecording.governance_status }}</n-descriptions-item>
                  <n-descriptions-item label="子调用概览">{{ sourceRecordingSubCallSummary || '-' }}</n-descriptions-item>
                </n-descriptions>
                <div style="margin-top:12px">
                  <SubCallPanel :sub-calls="sourceRecording.sub_calls" />
                </div>
              </n-card>
              <n-alert v-else-if="sourceLookupState === 'missing'" type="warning">已查询到回放结果，但未找到对应的来源录制</n-alert>
              <n-alert v-else-if="sourceLookupState === 'empty'" type="info">该回放结果未关联来源录制</n-alert>
            </template>
          </n-space>
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-space>

  <!-- 新增规则弹窗 -->
  <n-modal v-model:show="showModal" title="新增对比规则" preset="card" style="width:520px">
    <n-form :model="ruleForm" label-placement="left" label-width="100px">
      <n-form-item label="规则名称"><n-input v-model:value="ruleForm.name" /></n-form-item>
      <n-form-item label="作用范围">
        <n-select v-model:value="ruleForm.scope" :options="[{label:'全局',value:'global'},{label:'应用',value:'app'}]" />
      </n-form-item>
      <n-form-item label="规则类型">
        <n-select v-model:value="ruleForm.rule_type" :options="[{label:'忽略字段',value:'ignore'},{label:'断言',value:'assert'}]" />
      </n-form-item>
      <n-form-item label="规则配置">
        <n-input v-model:value="ruleForm.config" type="textarea" :rows="4" placeholder='示例: {"path": "data.timestamp", "type": "ignore"}' />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" @click="saveRule">保存</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NSpace, NGrid, NGridItem, NCard, NDataTable, NButton, NModal, NForm, NFormItem, NInput, NSelect, NText, NAlert, NPopconfirm, NDescriptions, NDescriptionsItem, NTag, useMessage } from 'naive-ui'
import { compareApi } from '@/api/compare'
import { replayApi } from '@/api/replays'
import { testCaseApi } from '@/api/testcases'
import { recordingApi } from '@/api/recordings'
import { useUserStore } from '@/store/user'
import SubCallPanel from '@/components/recording/SubCallPanel.vue'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'
import { lastValidPage, loadPagedData } from '@/utils/pagination'

const message = useMessage()
const router = useRouter()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const rules = ref<any[]>([])
const ruleLoading = ref(false)
const showModal = ref(false)
const resultId = ref('')
const diffData = ref<any>(null)
const sourceTestCase = ref<any | null>(null)
const sourceRecording = ref<any | null>(null)
const sourceRecordingSubCallSummary = ref('')
const sourceLookupState = ref<'idle' | 'found' | 'empty' | 'missing'>('idle')
const ruleForm = ref({ name: '', scope: 'global', rule_type: 'ignore', config: '{}', is_active: true })
const rulePagination = reactive({
  page: 1,
  pageSize: 8,
  itemCount: 0,
  pageSizes: [8, 16, 32, 64],
  showSizePicker: true,
  prefix: ({ itemCount }: { itemCount?: number }) => `共 ${itemCount || 0} 条规则`,
  onUpdatePage: (page: number) => {
    rulePagination.page = page
    void loadRules()
  },
  onUpdatePageSize: (pageSize: number) => {
    rulePagination.pageSize = pageSize
    rulePagination.page = 1
    void loadRules()
  },
})

const ruleColumns = [
  { title: '名称', key: 'name', ellipsis: true },
  { title: '范围', key: 'scope', width: 70 },
  { title: '类型', key: 'rule_type', width: 80 },
  { title: '状态', key: 'is_active', width: 60, render: (r: any) => r.is_active ? '启用' : '停用' },
  {
    title: '操作', key: 'actions', width: 80,
    render: (r: any) => canEdit ? h(NPopconfirm, { onPositiveClick: () => deleteRule(r.id) }, {
      default: () => '确认删除?',
      trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
    }) : null,
  },
]

function formatJson(s: string | null) {
  if (!s) return '-'
  try { return JSON.stringify(JSON.parse(s), null, 2) } catch { return s }
}

function rawText(s: string | null) {
  return s || '-'
}

async function loadRules() {
  ruleLoading.value = true
  try {
    const page = await loadPagedData<any>(compareApi.list, {}, rulePagination.page, rulePagination.pageSize, 100)
    rules.value = page.items
    rulePagination.itemCount = page.total
    if (page.items.length === 0 && page.total > 0 && rulePagination.page > 1) {
      rulePagination.page = lastValidPage(page.total, rulePagination.pageSize)
      void loadRules()
      return
    }
  } catch {
    rules.value = []
    rulePagination.itemCount = 0
    message.error('加载对比规则失败')
  } finally { ruleLoading.value = false }
}

function openCreate() {
  Object.assign(ruleForm.value, { name: '', scope: 'global', rule_type: 'ignore', config: '{}' })
  showModal.value = true
}

async function saveRule() {
  try {
    await compareApi.create(ruleForm.value)
    message.success('规则已创建')
    showModal.value = false
    await loadRules()
  } catch (error: any) { message.error(error.response?.data?.detail || '创建失败') }
}

async function deleteRule(id: number) {
  try {
    await compareApi.delete(id)
    message.success('已删除')
    await loadRules()
  } catch (error: any) { message.error(error.response?.data?.detail || '删除失败') }
}

async function loadDiff() {
  if (!resultId.value) return
  try {
    const parsedId = parseInt(resultId.value, 10)
    if (isNaN(parsedId)) {
      message.error('请输入有效的回放结果 ID')
      return
    }
    const res = await replayApi.getResult(parsedId)
    diffData.value = res.data
    await loadSourceRecording(res.data)
  } catch (error: any) {
    diffData.value = null
    sourceTestCase.value = null
    sourceRecording.value = null
    sourceRecordingSubCallSummary.value = ''
    sourceLookupState.value = 'idle'
    message.error(error.response?.data?.detail || '查询失败')
  }
}

async function loadSourceRecording(result: any) {
  sourceTestCase.value = null
  sourceRecording.value = null
  sourceRecordingSubCallSummary.value = ''
  sourceLookupState.value = 'empty'
  if (!result?.test_case_id) {
    return
  }
  try {
    const caseRes = await testCaseApi.get(result.test_case_id)
    sourceTestCase.value = caseRes.data
    if (caseRes.data.source_recording_id) {
      const recordingRes = await recordingApi.getRecording(caseRes.data.source_recording_id)
      sourceRecording.value = recordingRes.data
      sourceRecordingSubCallSummary.value = buildRecordingSubCallSummary(
        parseRecordingSubCalls(recordingRes.data.sub_calls),
      )
      sourceLookupState.value = 'found'
    } else {
      sourceLookupState.value = 'empty'
    }
  } catch {
    sourceTestCase.value = null
    sourceRecording.value = null
    sourceRecordingSubCallSummary.value = ''
    sourceLookupState.value = 'missing'
  }
}

onMounted(loadRules)
</script>
