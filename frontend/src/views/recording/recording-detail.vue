<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/recording')">录制中心</n-breadcrumb-item>
        <n-breadcrumb-item v-if="recording?.session_id" @click="router.push(`/recording/sessions/${recording.session_id}`)">
          会话 #{{ recording.session_id }}
        </n-breadcrumb-item>
        <n-breadcrumb-item>录制 #{{ recordingId }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button v-if="recording?.session_id" @click="router.push(`/recording/sessions/${recording.session_id}`)">返回会话</n-button>
        <n-button v-if="recording" @click="router.push(`/applications/${recording.application_id}`)">所属应用</n-button>
        <n-button v-if="canEdit" type="primary" @click="showConvertModal = true">生成测试用例</n-button>
      </n-space>
    </n-space>

    <n-card v-if="recording" title="录制概览">
      <n-descriptions bordered :column="2">
        <n-descriptions-item label="请求方法">{{ recording.request_method }}</n-descriptions-item>
        <n-descriptions-item label="响应码">{{ recording.response_status ?? '-' }}</n-descriptions-item>
        <n-descriptions-item label="请求路径" :span="2">{{ recording.request_uri }}</n-descriptions-item>
        <n-descriptions-item label="所属应用">{{ appName }}</n-descriptions-item>
        <n-descriptions-item label="录制时间">{{ formatDateTime(recording.recorded_at) }}</n-descriptions-item>
        <n-descriptions-item label="交易码">{{ recording.transaction_code || '-' }}</n-descriptions-item>
        <n-descriptions-item label="治理状态">{{ governanceLabelMap[recording.governance_status] || recording.governance_status }}</n-descriptions-item>
        <n-descriptions-item label="场景键" :span="2">{{ recording.scene_key || '-' }}</n-descriptions-item>
        <n-descriptions-item label="会话 ID">{{ recording.session_id ?? '-' }}</n-descriptions-item>
        <n-descriptions-item label="耗时">{{ recording.latency_ms != null ? `${recording.latency_ms}ms` : '-' }}</n-descriptions-item>
        <n-descriptions-item label="记录 ID">{{ recording.record_id || '-' }}</n-descriptions-item>
        <n-descriptions-item label="重复次数">{{ recording.duplicate_count ?? 1 }}</n-descriptions-item>
        <n-descriptions-item label="标签">{{ recording.tags || '-' }}</n-descriptions-item>
        <n-descriptions-item label="去重指纹" :span="2">{{ recording.dedupe_hash || '-' }}</n-descriptions-item>
        <n-descriptions-item label="子调用概览" :span="2">{{ subCallSummary }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card v-if="recording && canEdit" title="样本治理">
      <n-form :model="governanceForm" label-placement="left" label-width="90px" inline>
        <n-form-item label="交易码">
          <n-input v-model:value="governanceForm.transaction_code" placeholder="可手工修正" style="width: 240px" />
        </n-form-item>
        <n-form-item label="治理状态">
          <n-select v-model:value="governanceForm.governance_status" :options="governanceOptions" style="width: 180px" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" :loading="savingGovernance" @click="saveGovernance">保存治理信息</n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="主调用详情">
      <n-space vertical :size="16">
        <n-grid :cols="2" :x-gap="16">
          <n-grid-item>
            <n-card title="请求头" size="small">
              <pre class="code-block">{{ prettyText(recording?.request_headers) }}</pre>
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="请求体" size="small">
              <pre class="code-block">{{ prettyText(recording?.request_body) }}</pre>
            </n-card>
          </n-grid-item>
          <n-grid-item :span="2">
            <n-card title="响应体" size="small">
              <pre class="code-block">{{ prettyText(recording?.response_body) }}</pre>
            </n-card>
          </n-grid-item>
        </n-grid>

        <SubCallPanel :sub-calls="recording?.sub_calls" />
      </n-space>
    </n-card>
  </n-space>

  <n-modal v-model:show="showConvertModal" title="由录制生成测试用例" preset="card" style="width: 420px">
    <n-form :model="convertForm" label-placement="left" label-width="100px">
      <n-form-item label="用例名称">
        <n-input v-model:value="convertForm.name" placeholder="留空则自动生成" />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showConvertModal = false">取消</n-button>
        <n-button type="primary" :loading="converting" @click="doConvert">生成</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NModal,
  NSelect,
  NSpace,
  useMessage,
} from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { recordingApi } from '@/api/recordings'
import { testCaseApi } from '@/api/testcases'
import SubCallPanel from '@/components/recording/SubCallPanel.vue'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'
import type { RecordingSubCall } from '@/utils/recording'
import { buildRecordingSubCallSummary, parseRecordingSubCalls } from '@/utils/recording'

type RecordingDetail = {
  id: number
  session_id?: number | null
  application_id: number
  record_id?: string | null
  request_method: string
  request_uri: string
  request_headers?: string | null
  request_body?: string | null
  response_status?: number | null
  response_body?: string | null
  transaction_code?: string | null
  scene_key?: string | null
  dedupe_hash?: string | null
  governance_status: string
  duplicate_count?: number | null
  sub_calls?: RecordingSubCall[] | string | null
  latency_ms?: number | null
  tags?: string | null
  recorded_at: string
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const recordingId = Number(route.params.id)

const recording = ref<RecordingDetail | null>(null)
const appName = ref('-')
const showConvertModal = ref(false)
const converting = ref(false)
const savingGovernance = ref(false)
const convertForm = ref({ name: '' })
const governanceForm = ref({
  transaction_code: '',
  governance_status: 'raw',
})

const subCallSummary = computed(() => {
  if (!recording.value?.sub_calls) {
    return '-'
  }
  const subCalls = parseRecordingSubCalls(recording.value.sub_calls)
  return subCalls.length > 0 ? buildRecordingSubCallSummary(subCalls) : '-'
})

const governanceOptions = [
  { label: '原始录制', value: 'raw' },
  { label: '候选样本', value: 'candidate' },
  { label: '已批准', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已归档', value: 'archived' },
]

const governanceLabelMap: Record<string, string> = {
  raw: '原始录制',
  candidate: '候选样本',
  approved: '已批准',
  rejected: '已拒绝',
  archived: '已归档',
}

function prettyText(value?: string | null) {
  if (!value) return '-'
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

async function loadPage() {
  try {
    const res = await recordingApi.getRecording(recordingId)
    recording.value = res.data
    governanceForm.value = {
      transaction_code: res.data.transaction_code || '',
      governance_status: res.data.governance_status || 'raw',
    }
    const appRes = await applicationApi.get(res.data.application_id)
    appName.value = appRes.data.name
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载录制详情失败')
  }
}

async function saveGovernance() {
  savingGovernance.value = true
  try {
    await recordingApi.updateRecording(recordingId, governanceForm.value)
    message.success('样本治理信息已更新')
    await loadPage()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存治理信息失败')
  } finally {
    savingGovernance.value = false
  }
}

async function doConvert() {
  converting.value = true
  try {
    const res = await testCaseApi.fromRecording({
      recording_id: recordingId,
      name: convertForm.value.name || undefined,
    })
    message.success('已由录制生成测试用例')
    showConvertModal.value = false
    router.push(`/testcases/${res.data.id}`)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '生成测试用例失败')
  } finally {
    converting.value = false
  }
}

onMounted(() => {
  void loadPage()
})
</script>

<style scoped>
.code-block {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 420px;
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  background: #f8f8f8;
  font-family: monospace;
  font-size: 12px;
}
</style>
