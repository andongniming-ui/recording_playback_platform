<template>
  <n-space vertical :size="16" class="recording-page">
    <n-space justify="space-between" align="center">
      <div>
        <n-h2 style="margin: 0">录制中心</n-h2>
        <n-text depth="3">按会话查看录制结果，按样本治理视图做批量处理。</n-text>
      </div>
      <n-button v-if="canEdit" type="primary" @click="openCreateSession">+ 新建会话</n-button>
    </n-space>

    <n-grid cols="1 s:2 l:4" responsive="screen" :x-gap="12" :y-gap="12" class="recording-summary">
      <n-grid-item>
        <n-card>
          <n-statistic label="会话总数" :value="sessionPagination.itemCount" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="已完成会话" :value="sessions.filter(item => item.status === 'done').length" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="治理分组" :value="groupPagination.itemCount" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="已选分组" :value="selectedGroupRecordingIds.length" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-card title="查询条件">
      <div class="recording-filter-grid">
        <n-select
          v-model:value="filterApplicationId"
          :options="appOptions"
          clearable
          placeholder="请选择应用"
          @update:value="handleApplicationFilterChange"
        />
        <n-select
          v-model:value="filterStatus"
          :options="statusOptions"
          clearable
          placeholder="会话状态"
          @update:value="reloadSessionsFromFirstPage"
        />
        <n-date-picker
          v-model:value="filterDateRange"
          type="daterange"
          clearable
          @update:value="reloadSessionsFromFirstPage"
        />
        <n-input
          v-model:value="sessionSearch"
          clearable
          placeholder="搜索会话名称或应用"
          @keyup.enter="reloadSessionsFromFirstPage"
        />
        <div class="recording-filter-actions">
          <n-button type="primary" @click="reloadSessionsFromFirstPage">查询</n-button>
          <n-button quaternary @click="resetFilters">重置</n-button>
        </div>
      </div>
    </n-card>

    <n-card title="录制会话">
      <template #header-extra>
        <n-space>
          <n-tag type="info" size="small">共 {{ sessionPagination.itemCount }} 条</n-tag>
          <n-button
            v-if="canEdit"
            size="small"
            type="error"
            :disabled="selectedSessionIds.length === 0"
            @click="deleteSelectedSessions"
          >
            批量删除{{ selectedSessionIds.length > 0 ? ` (${selectedSessionIds.length})` : '' }}
          </n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="sessionColumns"
        :data="filteredSessions"
        :loading="sessionsLoading"
        :row-key="(row: SessionRow) => row.id"
        :pagination="sessionPagination"
        remote
        v-model:checked-row-keys="selectedSessionIds"
        @update:sorter="handleSessionSorterChange"
      />
    </n-card>

    <n-card title="样本治理视图">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="groupGovernanceStatus"
            clearable
            :options="governanceOptions"
            placeholder="治理状态"
            style="width: 150px"
            @update:value="reloadRecordingGroupsFromFirstPage"
          />
          <n-input
            v-model:value="groupSearch"
            clearable
            placeholder="交易码 / 场景键 / URI"
            style="width: 240px"
            @keyup.enter="reloadRecordingGroupsFromFirstPage"
          />
          <n-button @click="reloadRecordingGroupsFromFirstPage">查询</n-button>
          <n-button
            v-if="canEdit"
            type="error"
            :disabled="selectedGroupRecordingIds.length === 0"
            @click="deleteSelectedGroupRecordings"
          >
            批量删除代表样本{{ selectedGroupRecordingIds.length > 0 ? ` (${selectedGroupRecordingIds.length})` : '' }}
          </n-button>
          <n-button
            v-if="canEdit"
            type="primary"
            :disabled="selectedGroupRecordingIds.length === 0"
            @click="openBatchModal('groups')"
          >
            批量生成用例{{ selectedGroupRecordingIds.length > 0 ? ` (${selectedGroupRecordingIds.length})` : '' }}
          </n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="groupColumns"
        :data="recordingGroups"
        :loading="groupsLoading"
        :pagination="groupPagination"
        :row-key="(row: RecordingGroupRow) => row.representative_recording_id"
        remote
        v-model:checked-row-keys="selectedGroupRecordingIds"
        @update:sorter="handleGroupSorterChange"
      />
    </n-card>
  </n-space>

  <n-modal v-model:show="showSessionModal" title="新建录制会话" preset="card" style="width: 480px">
    <n-form :model="sessionForm" label-placement="left" label-width="120px">
      <n-form-item label="会话名称">
        <n-input v-model:value="sessionForm.name" placeholder="可选，便于识别" />
      </n-form-item>
      <n-form-item label="所属应用">
        <n-select
          v-model:value="sessionForm.application_id"
          :options="appOptions"
          placeholder="请选择应用"
        />
      </n-form-item>
      <n-form-item label="交易码过滤">
        <n-input
          v-model:value="sessionForm.recording_filter_prefixes_text"
          type="textarea"
          :autosize="{ minRows: 3, maxRows: 6 }"
          placeholder="例如：car001\n=car001_open\nre:^car001.*$"
        />
      </n-form-item>
      <n-form-item label="说明">
        <n-text depth="3">推荐一行一条规则，支持前缀、精确和正则；空白表示不过滤。</n-text>
      </n-form-item>
    </n-form>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showSessionModal = false">取消</n-button>
        <n-button type="primary" :loading="creatingSession" @click="createSession">创建</n-button>
      </n-space>
    </template>
  </n-modal>

  <n-drawer v-model:show="showRecordingDrawer" :width="760" placement="right">
    <n-drawer-content :title="`会话 #${selectedSession?.id} 的录制数据`" closable>
      <n-space vertical :size="8">
        <n-space justify="space-between">
          <n-input
            v-model:value="recordingSearch"
            clearable
            placeholder="按请求路径或交易码搜索"
            style="width: 100%"
            @keyup.enter="reloadCurrentRecordingsFromFirstPage"
          />
          <n-space v-if="canEdit">
            <n-button
              size="small"
              type="error"
              :disabled="selectedSessionRecordingIds.length === 0"
              @click="deleteSelectedSessionRecordings"
            >
              批量删除{{ selectedSessionRecordingIds.length > 0 ? ` (${selectedSessionRecordingIds.length})` : '' }}
            </n-button>
            <n-button
              size="small"
              type="primary"
              :disabled="selectedSessionRecordingIds.length === 0"
              @click="openBatchModal('recordings')"
            >
              批量生成用例{{ selectedSessionRecordingIds.length > 0 ? ` (${selectedSessionRecordingIds.length})` : '' }}
            </n-button>
          </n-space>
        </n-space>
        <n-data-table
          :columns="recordingColumns"
          :data="filteredRecordings"
          :loading="recordingsLoading"
          :pagination="recordingPagination"
          size="small"
          :row-key="(row: RecordingRow) => row.id"
          remote
          v-model:checked-row-keys="selectedSessionRecordingIds"
          @update:sorter="handleRecordingSorterChange"
        />
      </n-space>
    </n-drawer-content>
  </n-drawer>

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

  <!-- 批量生成用例 Modal（两步：前缀输入 → 冲突检测结果） -->
  <n-modal
    v-model:show="showBatchModal"
    :title="batchStep === 'prefix' ? '批量生成测试用例' : '冲突检测结果'"
    preset="card"
    style="width: 480px"
    :closable="!batchGenerating"
    :mask-closable="!batchGenerating"
  >
    <template v-if="batchStep === 'prefix'">
      <n-space vertical>
        <span>{{ batchSource === 'groups' ? `已选 ${selectedGroupRecordingIds.length} 个分组` : `已选 ${selectedSessionRecordingIds.length} 条录制` }}</span>
        <n-form label-placement="left" label-width="100px">
          <n-form-item label="用例名称前缀">
            <n-input
              v-model:value="batchPrefix"
              placeholder="如：银行服务"
              @keyup.enter="doBatchCheck"
            />
          </n-form-item>
        </n-form>
      </n-space>
    </template>
    <template v-else>
      <n-space vertical>
        <n-alert
          v-if="batchCheckItems.filter(i => !i.has_existing).length > 0"
          type="success"
          :show-icon="true"
        >
          {{ batchCheckItems.filter(i => !i.has_existing).length }} 条可生成
        </n-alert>
        <n-alert
          v-if="batchCheckItems.filter(i => i.has_existing).length > 0"
          type="warning"
          :show-icon="true"
        >
          {{ batchCheckItems.filter(i => i.has_existing).length }} 条已有用例（{{
            batchCheckItems.filter(i => i.has_existing).map(i => i.transaction_code || `#${i.recording_id}`).join('、')
          }}），将自动跳过
        </n-alert>
        <n-alert
          v-if="batchCheckItems.filter(i => !i.has_existing).length === 0"
          type="info"
        >
          所有选中分组均已有对应用例，无需重复生成
        </n-alert>
      </n-space>
    </template>
    <template #footer>
      <n-space justify="end">
        <template v-if="batchStep === 'prefix'">
          <n-button @click="showBatchModal = false">取消</n-button>
          <n-button type="primary" :loading="batchChecking" @click="doBatchCheck">
            检测冲突 →
          </n-button>
        </template>
        <template v-else>
          <n-button @click="batchStep = 'prefix'">返回</n-button>
          <n-button
            v-if="batchCheckItems.filter(i => !i.has_existing).length > 0"
            type="primary"
            :loading="batchGenerating"
            @click="doBatchGenerate"
          >
            确认生成 →
          </n-button>
        </template>
      </n-space>
    </template>
  </n-modal>

  <!-- 批量生成结果 Modal -->
  <n-modal
    v-model:show="showBatchResultModal"
    title="生成完成"
    preset="card"
    style="width: 420px"
  >
    <n-space vertical v-if="batchResult">
      <n-alert v-if="batchResult.created > 0" type="success" :show-icon="true">成功 {{ batchResult.created }} 条</n-alert>
      <n-alert v-if="batchResult.skipped > 0" type="warning" :show-icon="true">
        跳过 {{ batchResult.skipped }} 条（已有用例）
      </n-alert>
      <n-alert v-if="batchResult.failed > 0" type="error" :show-icon="true">
        失败 {{ batchResult.failed }} 条
        <ul style="margin: 4px 0 0; padding-left: 16px; font-size: 12px">
          <li v-for="r in batchResult.results.filter(x => x.status === 'failed')" :key="r.recording_id">
            录制 #{{ r.recording_id }}：{{ r.error }}
          </li>
        </ul>
      </n-alert>
      <n-alert v-if="batchResult.created === 0 && batchResult.skipped === 0 && batchResult.failed === 0" type="info" :show-icon="true">
        未生成任何用例
      </n-alert>
    </n-space>
    <template #footer>
      <n-space justify="end">
        <n-button @click="showBatchResultModal = false">关闭</n-button>
        <n-button type="primary" @click="() => { showBatchResultModal = false; router.push('/testcases') }">
          前往测试用例库 →
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { NAlert, NButton, NCard, NDataTable, NDatePicker, NDrawer, NDrawerContent, NGrid, NGridItem, NH2, NForm, NFormItem, NInput, NModal, NSpace, NSelect, NStatistic, NTag, NText } from 'naive-ui'
import type { RecordingGroupRow, RecordingRow, SessionRow } from './types'
import { useRecordingPage } from './useRecordingPage'

const {
  router,
  canEdit,
  sessions,
  sessionsLoading,
  filterApplicationId,
  filterStatus,
  filterDateRange,
  sessionSearch,
  appOptions,
  showSessionModal,
  creatingSession,
  sessionForm,
  showRecordingDrawer,
  selectedSession,
  recordingsLoading,
  recordingSearch,
  selectedSessionRecordingIds,
  recordingGroups,
  groupsLoading,
  groupGovernanceStatus,
  groupSearch,
  selectedSessionIds,
  selectedGroupRecordingIds,
  sessionPagination,
  groupPagination,
  recordingPagination,
  showConvertModal,
  batchSource,
  showBatchModal,
  batchStep,
  batchPrefix,
  batchChecking,
  batchCheckItems,
  batchGenerating,
  showBatchResultModal,
  batchResult,
  converting,
  convertForm,
  statusOptions,
  governanceOptions,
  filteredSessions,
  filteredRecordings,
  sessionColumns,
  recordingColumns,
  groupColumns,
  reloadSessionsFromFirstPage,
  reloadRecordingGroupsFromFirstPage,
  handleApplicationFilterChange,
  resetFilters,
  openCreateSession,
  createSession,
  deleteSelectedSessions,
  reloadCurrentRecordingsFromFirstPage,
  doConvert,
  openBatchModal,
  doBatchCheck,
  doBatchGenerate,
  deleteSelectedSessionRecordings,
  deleteSelectedGroupRecordings,
  handleSessionSorterChange,
  handleRecordingSorterChange,
  handleGroupSorterChange
} = useRecordingPage()
</script>

<style scoped>
.recording-page {
  width: 100%;
}

.recording-filter-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.9fr) minmax(0, 1.2fr) minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.recording-filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
}

.recording-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.95fr);
  gap: 16px;
  align-items: start;
}

.recording-grid :deep(.n-card) {
  border-radius: 16px;
}

.recording-grid :deep(.n-card-header) {
  align-items: center;
}

.quality-hint {
  font-size: 12px;
  color: #888;
  line-height: 1.2;
}

@media (max-width: 1280px) {
  .recording-filter-grid,
  .recording-grid {
    grid-template-columns: 1fr;
  }
}
</style>
