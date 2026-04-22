<template>
  <n-space vertical :size="16">
    <n-card title="API Token 管理">
      <template #header-extra>
        <n-button type="primary" size="small" @click="openCreate">+ 生成 Token</n-button>
      </template>
      <n-data-table :columns="tokenColumns" :data="tokens" :loading="loading" :pagination="{ pageSize: 10 }" />
    </n-card>

    <n-card title="CI/CD 使用说明">
      <n-space vertical :size="8">
        <n-text strong>1. 触发套件回放</n-text>
        <pre style="background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;font-size:13px;overflow-x:auto">curl -X POST {{ baseUrl }}/api/v1/ci/trigger \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"suite_id": 1, "concurrency": 5}'</pre>

        <n-text strong>2. 查询回放结果</n-text>
        <pre style="background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;font-size:13px;overflow-x:auto">curl {{ baseUrl }}/api/v1/ci/result/{job_id} \
  -H "Authorization: Token YOUR_TOKEN"</pre>

        <n-text strong>3. 返回值示例</n-text>
        <pre style="background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;font-size:13px;overflow-x:auto">{
  "job_id": 42,
  "status": "DONE",
  "total": 100,
  "passed": 95,
  "failed": 5,
  "errored": 0,
  "pass_rate": 0.95
}</pre>
      </n-space>
    </n-card>
  </n-space>

  <!-- 创建 Token 弹窗 -->
  <n-modal v-model:show="showModal" title="生成 API Token" preset="card" style="width:440px">
    <n-form :model="form" label-placement="left" label-width="100px">
      <n-form-item label="Token 名称"><n-input v-model:value="form.name" placeholder="如: jenkins-ci" /></n-form-item>
      <n-form-item label="权限范围">
        <n-select v-model:value="form.scope" :options="[{label:'触发回放',value:'trigger'},{label:'只读',value:'read_only'}]" />
      </n-form-item>
      <n-form-item label="有效期(天)">
        <n-input-number v-model:value="form.expires_days" placeholder="留空永不过期" clearable />
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="createToken">生成</n-button>
      </n-space>
    </template>
  </n-modal>

  <!-- 显示新 Token -->
  <n-modal v-model:show="showToken" title="Token 已生成" preset="card" style="width:500px">
    <n-alert type="warning" title="请立即保存！Token 仅显示一次">
      <n-input :value="newToken" readonly type="text" style="font-family:monospace;margin-top:8px" />
    </n-alert>
    <template #footer>
      <n-button type="primary" @click="copyToken">复制 Token</n-button>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, h } from 'vue'
import { NSpace, NCard, NButton, NDataTable, NTag, NModal, NForm, NFormItem, NInput, NInputNumber, NSelect, NAlert, NText, NPopconfirm, useMessage } from 'naive-ui'
import { ciApi } from '@/api/ci'
import { formatDateTime } from '@/utils/format'
import { API_ORIGIN } from '@/config'

const message = useMessage()
const tokens = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const showToken = ref(false)
const saving = ref(false)
const newToken = ref('')
const form = ref({ name: '', scope: 'trigger', expires_days: null as number | null })
const baseUrl = computed(() => {
  if (import.meta.env.DEV && API_ORIGIN === window.location.origin) {
    return `${window.location.protocol}//${window.location.hostname}:8000`
  }
  return API_ORIGIN
})

const tokenColumns = [
  { title: '名称', key: 'name' },
  { title: '权限', key: 'scope', width: 90 },
  {
    title: '状态', key: 'is_active', width: 70,
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small' }, () => r.is_active ? '有效' : '已撤销'),
  },
  { title: '过期时间', key: 'expires_at', width: 155, render: (r: any) => r.expires_at?.slice(0, 10) || '永不过期' },
  { title: '最后使用', key: 'last_used_at', width: 155, render: (r: any) => formatDateTime(r.last_used_at) },
  {
    title: '操作', key: 'actions', width: 80,
    render: (r: any) => h(NPopconfirm, { onPositiveClick: () => revokeToken(r.id) }, {
      default: () => '确认撤销?',
      trigger: () => h(NButton, { size: 'tiny', type: 'error', disabled: !r.is_active }, () => '撤销'),
    }),
  },
]

async function load() {
  loading.value = true
  try {
    tokens.value = (await ciApi.listTokens()).data
  } catch (error: any) {
    tokens.value = []
    message.error(error.response?.data?.detail || '加载 Token 列表失败')
  } finally { loading.value = false }
}

function openCreate() {
  form.value = { name: '', scope: 'trigger', expires_days: null }
  showModal.value = true
}

async function createToken() {
  saving.value = true
  try {
    const res = await ciApi.createToken(form.value)
    newToken.value = res.data.plain_token
    showModal.value = false
    showToken.value = true
    await load()
  } catch (error: any) { message.error(error.response?.data?.detail || '创建失败') } finally { saving.value = false }
}

async function revokeToken(id: number) {
  try { await ciApi.revokeToken(id); message.success('已撤销'); await load() } catch (error: any) { message.error(error.response?.data?.detail || '撤销失败') }
}

function copyToken() {
  navigator.clipboard
    .writeText(newToken.value)
    .then(() => message.success('已复制到剪贴板'))
    .catch(() => message.error('复制失败，请手动复制'))
}

onMounted(load)
</script>
