<template>
  <n-space vertical :size="16" class="applications-page">
    <n-space justify="space-between" align="center">
      <div>
        <n-h2 style="margin: 0">应用管理</n-h2>
        <n-text depth="3">统一管理被测应用、接入配置和 Agent 状态。</n-text>
      </div>
      <n-button v-if="canEdit" type="primary" @click="openCreate">+ 新增应用</n-button>
    </n-space>

    <n-grid :cols="4" :x-gap="12" :y-gap="12">
      <n-grid-item>
        <n-card>
          <n-statistic label="应用总数" :value="apps.length" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="已挂载">
            <template #default>
              <span style="color:#18a058">{{ onlineCount }}</span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="未挂载">
            <template #default>
              <span style="color:#d03050">{{ offlineCount }}</span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="挂载中">
            <template #default>
              <span style="color:#f0a020">{{ mountingCount }}</span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="应用列表">
      <template #header-extra>
        <n-tag type="info" size="small">共 {{ apps.length }} 个应用</n-tag>
      </template>
      <n-data-table
        class="applications-table"
        :columns="columns"
        :data="apps"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
      />
    </n-card>

    <n-card title="页面说明">
      <n-space vertical :size="8">
        <n-alert type="info" :show-icon="false">
          页面采用上下结构展示，表格列间距和左右留白已拉宽，便于大屏阅读。
        </n-alert>
        <n-alert type="warning" :show-icon="false">
          新增 / 编辑时只需要补充宿主机、端口、服务进程和 AREX 配置即可。
        </n-alert>
      </n-space>
    </n-card>
  </n-space>

  <n-modal
    v-model:show="showModal"
    :title="editingId ? '编辑应用' : '新增应用'"
    preset="card"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="form" label-placement="left" label-width="120px">
      <!-- 隐藏诱饵输入框，防止浏览器自动填充连接字段 -->
      <input type="text" style="display:none" autocomplete="username" tabindex="-1" aria-hidden="true" />
      <input type="password" style="display:none" autocomplete="current-password" tabindex="-1" aria-hidden="true" />
      <n-form-item label="应用名称" path="name" :rule="{ required: true, message: '请输入应用名称' }">
        <n-input v-model:value="form.name" placeholder="例如：demo-service" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="form.description" placeholder="可选" />
      </n-form-item>
      <n-form-item label="宿主机地址" path="ssh_host" :rule="{ required: true, message: '请输入宿主机地址' }">
        <n-input v-model:value="form.ssh_host" placeholder="IP 或域名" />
      </n-form-item>
      <n-form-item label="宿主机用户" path="ssh_user" :rule="{ required: true, message: '请输入宿主机用户' }">
        <n-input v-model:value="form.ssh_user" placeholder="例如：ubuntu" />
      </n-form-item>
      <n-form-item label="宿主机端口">
        <n-input-number v-model:value="form.ssh_port" />
      </n-form-item>
      <n-form-item label="启动模式">
        <n-select v-model:value="form.launch_mode" :options="launchModeOptions" />
      </n-form-item>
      <n-alert type="info" :show-icon="false">
        Docker 模式由平台生成启动模板并通过 docker compose 控制容器重建，不再修改 start.sh。
      </n-alert>
      <template v-if="form.launch_mode === 'docker_compose'">
        <n-form-item label="Docker 工作目录" path="docker_workdir" :rule="{ required: true, message: '请输入 Docker 工作目录' }">
          <n-input v-model:value="form.docker_workdir" placeholder="/home/test/N-LS" />
        </n-form-item>
        <n-form-item label="Docker Compose 文件">
          <n-input v-model:value="form.docker_compose_file" placeholder="docker-compose.yml" />
        </n-form-item>
        <n-form-item label="Compose 服务名" path="docker_service_name" :rule="{ required: true, message: '请输入 Compose 服务名' }">
          <n-input v-model:value="form.docker_service_name" placeholder="sat / uat / app-service" />
        </n-form-item>
        <n-form-item label="Docker Agent Storage">
          <n-input v-model:value="form.docker_storage_url" placeholder="留空则使用平台默认 Docker storage URL" />
        </n-form-item>
        <n-form-item label="Agent 挂载路径">
          <n-input v-model:value="form.docker_agent_path" placeholder="/opt/arex/arex-agent.jar" />
        </n-form-item>
      </template>
      <n-form-item label="密钥路径">
        <n-input
          v-model:value="form.ssh_key_path"
          placeholder="/path/to/key"
          :input-props="{ autocomplete: 'new-password' }"
        />
      </n-form-item>
      <n-form-item label="连接密码">
        <n-input
          v-model:value="form.ssh_password"
          type="password"
          :input-props="{ autocomplete: 'new-password' }"
          :placeholder="editingHasPassword ? '已设置密码（留空不修改）' : '可选'"
        />
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
      <n-form-item label="AREX Storage 地址">
        <n-input v-model:value="form.arex_storage_url" placeholder="留空则使用全局配置" />
      </n-form-item>
      <n-form-item label="采样率">
        <n-slider v-model:value="form.sample_rate" :min="0" :max="1" :step="0.1" style="width: 200px" />
        <n-text style="margin-left: 12px">{{ form.sample_rate }}</n-text>
      </n-form-item>
      <n-form-item label="交易码映射">
        <n-space vertical style="width: 100%">
          <n-alert type="info" :show-icon="false">
            以 JSON 数组配置，每个交易码一组规则。平台会在回放前自动按交易码加载对应映射。
            推荐按 <code>transaction_code</code> 一条一组填写。字段路径使用点号，例如 <code>name</code>、<code>customer.name</code>、<code>items.0.name</code>、<code>*.name</code>。
          </n-alert>
          <n-alert type="warning" :show-icon="false">
            规则类型目前支持 <code>rename</code>（改名）、<code>delete</code>（删除）、<code>default</code>（补默认值）、<code>set</code>（强制赋值）、<code>copy</code>（复制到新字段）。
            推荐先参考 <code>docs/交易码映射模板.md</code> 再填写。
          </n-alert>
          <n-input
            v-model:value="form.transaction_mappings"
            type="textarea"
            :autosize="{ minRows: 6, maxRows: 14 }"
            placeholder='[
  {
    "transaction_code": "A0201M14I",
    "enabled": true,
    "description": "开户字段映射",
    "request_rules": [
      { "type": "rename", "source": "name", "target": "cst_name" },
      { "type": "rename", "source": "idNo", "target": "cert_no" },
      { "type": "default", "source": "branch_code", "value": "0101" },
      { "type": "delete", "source": "debug_flag" }
    ],
    "response_rules": [
      { "type": "rename", "source": "cst_name", "target": "name" },
      { "type": "delete", "source": "debug_flag" }
    ]
  },
  {
    "transaction_code": "A0201D008",
    "enabled": true,
    "description": "支用字段映射",
    "request_rules": [
      { "type": "rename", "source": "amount", "target": "loan_amount" }
    ],
    "response_rules": []
  }
]'
          />
        </n-space>
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
import { computed, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NAlert,
  NButton,
  NDataTable,
  NCard,
  NGrid,
  NGridItem,
  NForm,
  NFormItem,
  NH2,
  NInput,
  NInputNumber,
  NModal,
  NPopconfirm,
  NSelect,
  NSlider,
  NSpace,
  NStatistic,
  NTag,
  NText,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, TagProps } from 'naive-ui'
import { applicationApi } from '@/api/applications'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/store/user'

type AppRow = {
  id: number
  name: string
  ssh_host: string
  ssh_key_path?: string | null
  has_password?: boolean
  service_port: number
  agent_status?: string | null
  created_at?: string
}

type AppForm = {
  name: string
  description: string
  ssh_host: string
  ssh_user: string
  ssh_port: number
  launch_mode: 'ssh_script' | 'docker_compose'
  ssh_key_path: string
  ssh_password: string
  docker_workdir: string
  docker_compose_file: string
  docker_service_name: string
  docker_storage_url: string
  docker_agent_path: string
  service_port: number
  jvm_process_name: string
  arex_app_id: string
  arex_storage_url: string
  sample_rate: number
  transaction_mappings: string
}

const message = useMessage()
const router = useRouter()
const userStore = useUserStore()
const canEdit = userStore.role === 'admin' || userStore.role === 'editor'
const apps = ref<AppRow[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const editingHasPassword = ref(false)
const formRef = ref()
const form = ref<AppForm>(createEmptyForm())
const onlineCount = computed(() => apps.value.filter((item) => normalizeAgentStatus(item.agent_status) === 'online').length)
const offlineCount = computed(() => apps.value.filter((item) => normalizeAgentStatus(item.agent_status) === 'offline').length)
const mountingCount = computed(() => apps.value.filter((item) => normalizeAgentStatus(item.agent_status) === 'mounting').length)

function normalizeAgentStatus(status?: string | null) {
  const value = (status || 'unknown').toLowerCase()
  if (value === 'attached' || value === 'online' || value === 'already_injected') {
    return 'online'
  }
  if (value === 'detached' || value === 'offline') {
    return 'offline'
  }
  if (value === 'mounting') {
    return 'mounting'
  }
  if (value === 'error') {
    return 'error'
  }
  return 'unknown'
}

const statusTypeMap: Record<string, NonNullable<TagProps['type']>> = {
  online: 'success',
  offline: 'error',
  mounting: 'warning',
  error: 'error',
  unknown: 'default',
}

const statusLabelMap: Record<string, string> = {
  online: '已挂载',
  offline: '未挂载',
  mounting: '挂载中',
  error: '挂载失败',
  unknown: '未知',
}

const launchModeOptions = [
  { label: '宿主机脚本', value: 'ssh_script' },
  { label: 'Docker Compose', value: 'docker_compose' },
]

const columns: DataTableColumns<AppRow> = [
  {
    title: '名称',
    key: 'name',
    width: 220,
    render: (row) =>
      h(
        NButton,
        { text: true, type: 'primary', onClick: () => router.push(`/applications/${row.id}`) },
        () => row.name,
      ),
  },
  { title: '宿主机', key: 'ssh_host', width: 220 },
  { title: '服务端口', key: 'service_port', width: 110 },
  {
    title: 'Agent 状态',
    key: 'agent_status',
    width: 130,
    render: (row) => {
      const normalizedStatus = normalizeAgentStatus(row.agent_status)
      return h(
        NTag,
        {
          type: statusTypeMap[normalizedStatus] || 'default',
          size: 'small',
        },
        () => statusLabelMap[normalizedStatus] || '未知',
      )
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render: (row) => formatDateTime(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 320,
    render: (row) => {
      const normalizedStatus = normalizeAgentStatus(row.agent_status)
      return h(NSpace, { size: 8, wrap: true }, () => [
        h(NButton, { size: 'tiny', onClick: () => router.push(`/applications/${row.id}`) }, () => '查看详情'),
        ...(canEdit ? [
          h(NButton, { size: 'tiny', onClick: () => testConn(row.id) }, () => '连接测试'),
          normalizedStatus === 'online'
            ? h(NButton, { size: 'tiny', type: 'warning', onClick: () => unmount(row.id) }, () => '卸载 Agent')
            : h(NButton, { size: 'tiny', type: 'info', onClick: () => mount(row.id) }, () => '挂载 Agent'),
          h(NButton, { size: 'tiny', onClick: () => openEdit(row) }, () => '编辑'),
        ] : []),
        ...(userStore.role === 'admin'
          ? [h(
              NPopconfirm,
              { onPositiveClick: () => deleteApp(row.id) },
              {
                default: () => '确认删除？',
                trigger: () => h(NButton, { size: 'tiny', type: 'error' }, () => '删除'),
              },
            )]
          : []),
      ])
    },
  },
]

function createEmptyForm(): AppForm {
  return {
    name: '',
    description: '',
    ssh_host: '',
    ssh_user: '',
    ssh_port: 22,
    launch_mode: 'ssh_script',
    ssh_key_path: '',
    ssh_password: '',
    docker_workdir: '',
    docker_compose_file: 'docker-compose.yml',
    docker_service_name: '',
    docker_storage_url: '',
    docker_agent_path: '/opt/arex/arex-agent.jar',
    service_port: 8080,
    jvm_process_name: '',
    arex_app_id: '',
    arex_storage_url: '',
    sample_rate: 1.0,
    transaction_mappings: '',
  }
}


async function loadApps() {
  loading.value = true
  try {
    const res = await applicationApi.list()
    apps.value = res.data
  } catch (error: any) {
    apps.value = []
    message.error(error.response?.data?.detail || '加载应用列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = createEmptyForm()
}

function openCreate() {
  editingId.value = null
  editingHasPassword.value = false
  resetForm()
  showModal.value = true
}

function openEdit(app: Record<string, any>) {
  editingId.value = app.id
  editingHasPassword.value = Boolean(app.has_password)
  form.value = {
    ...createEmptyForm(),
    ...app,
    ssh_password: '',  // 不回填密码，留空表示不修改
    transaction_mappings: Array.isArray(app.transaction_mappings)
      ? JSON.stringify(app.transaction_mappings, null, 2)
      : '',
  }
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
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function testConn(id: number) {
  try {
    const res = await applicationApi.testConnection(id)
    if (res.data.success) {
      message.success('连接成功')
    } else {
      message.error(`连接失败：${res.data.message}`)
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '连接测试失败')
  }
}

async function mount(id: number) {
  try {
    await applicationApi.mountAgent(id)
    message.info('Agent 挂载已启动，请稍候...')
    setTimeout(() => { void loadApps() }, 3000)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '挂载失败')
  }
}

async function unmount(id: number) {
  try {
    await applicationApi.unmountAgent(id)
    message.success('Agent 已卸载')
    await loadApps()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '卸载失败')
  }
}

async function deleteApp(id: number) {
  try {
    await applicationApi.delete(id)
    message.success('删除成功')
    await loadApps()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(loadApps)
</script>

<style scoped>
.applications-page {
  width: 100%;
}

.applications-page :deep(.n-card) {
  border-radius: 16px;
}

.applications-page :deep(.n-card-header) {
  align-items: center;
}

.applications-table :deep(.n-data-table-th),
.applications-table :deep(.n-data-table-td) {
  padding-left: 18px;
  padding-right: 18px;
}
</style>
