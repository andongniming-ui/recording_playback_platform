<template>
  <n-space vertical :size="16">
    <n-grid :cols="2" :x-gap="16">
      <!-- 左：对比规则管理 -->
      <n-grid-item>
        <n-card title="对比规则管理">
          <template #header-extra>
            <n-button v-if="canEdit" size="small" type="primary" @click="openCreate">+ 新增规则</n-button>
          </template>
          <n-data-table :columns="ruleColumns" :data="rules" :loading="ruleLoading" size="small" :pagination="{ pageSize: 8 }" />
        </n-card>
      </n-grid-item>

      <!-- 右：Diff 查看器 -->
      <n-grid-item>
        <n-card title="响应差异查看">
          <n-space vertical :size="8">
            <n-input v-model:value="resultId" placeholder="输入回放结果 ID" style="width:200px" />
            <n-button type="primary" @click="loadDiff">查看 Diff</n-button>
            <template v-if="diffData">
              <n-grid :cols="2" :x-gap="8" style="margin-top:8px">
                <n-grid-item>
                  <n-text strong>期望响应</n-text>
                  <pre style="background:#f5f5f5;padding:8px;border-radius:4px;font-size:12px;max-height:400px;overflow:auto;white-space:pre-wrap">{{ formatJson(diffData.expected_response) }}</pre>
                </n-grid-item>
                <n-grid-item>
                  <n-text strong>实际响应</n-text>
                  <pre style="background:#fff0f0;padding:8px;border-radius:4px;font-size:12px;max-height:400px;overflow:auto;white-space:pre-wrap">{{ formatJson(diffData.actual_response) }}</pre>
                </n-grid-item>
              </n-grid>
              <n-card v-if="diffData.diff_result" title="差异详情" size="small" style="margin-top:8px">
                <pre style="background:#fffbe6;padding:8px;border-radius:4px;font-size:12px;max-height:300px;overflow:auto;white-space:pre-wrap;color:#d03050">{{ formatJson(diffData.diff_result) }}</pre>
              </n-card>
              <n-alert v-else type="success">无差异，响应一致</n-alert>
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
import { ref, onMounted, h } from 'vue'
import { NSpace, NGrid, NGridItem, NCard, NDataTable, NButton, NModal, NForm, NFormItem, NInput, NSelect, NText, NAlert, NPopconfirm, useMessage } from 'naive-ui'
import { compareApi } from '@/api/compare'
import { replayApi } from '@/api/replays'
import { useUserStore } from '@/store/user'

const message = useMessage()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const rules = ref<any[]>([])
const ruleLoading = ref(false)
const showModal = ref(false)
const resultId = ref('')
const diffData = ref<any>(null)
const ruleForm = ref({ name: '', scope: 'global', rule_type: 'ignore', config: '{}', is_active: true })

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

async function loadRules() {
  ruleLoading.value = true
  try {
    const res = await compareApi.list()
    rules.value = res.data
  } catch {
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
  } catch (error: any) {
    diffData.value = null
    message.error(error.response?.data?.detail || '查询失败')
  }
}

onMounted(loadRules)
</script>
