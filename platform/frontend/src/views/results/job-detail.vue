<template>
  <n-space vertical :size="16">
    <n-space justify="space-between" align="center">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/replay/history')">回放历史</n-breadcrumb-item>
        <n-breadcrumb-item>任务 #{{ jobId }}</n-breadcrumb-item>
      </n-breadcrumb>
      <n-space>
        <n-button @click="loadPage">刷新</n-button>
        <n-button @click="router.push('/replay/history')">返回历史</n-button>
        <n-button type="info" @click="openReport">导出 HTML 报告</n-button>
      </n-space>
    </n-space>

    <!-- 任务基本信息 -->
    <n-card v-if="job" :title="job.name || `回放任务 #${jobId}`">
      <template #header-extra>
        <n-tag :type="jobStatusTypeMap[job.status] || 'default'">
          {{ jobStatusLabelMap[job.status] || job.status }}
        </n-tag>
      </template>
      <n-descriptions bordered :column="3" size="small">
        <n-descriptions-item label="回放应用">{{ appName }}</n-descriptions-item>
        <n-descriptions-item label="开始时间">{{ formatDateTime(job.started_at) }}</n-descriptions-item>
        <n-descriptions-item label="完成时间">{{ formatDateTime(job.finished_at) }}</n-descriptions-item>
        <n-descriptions-item label="并发数">{{ job.concurrency }}</n-descriptions-item>
        <n-descriptions-item label="超时">{{ job.timeout_ms }}ms</n-descriptions-item>
        <n-descriptions-item label="智能降噪">{{ job.smart_noise_reduction ? '开启' : '关闭' }}</n-descriptions-item>
      </n-descriptions>
      <n-space v-if="job.ignore_fields?.length" style="margin-top:12px">
        <span style="color:#666;font-size:13px">忽略字段：</span>
        <n-tag v-for="f in job.ignore_fields" :key="f" size="small" type="default">{{ f }}</n-tag>
      </n-space>
    </n-card>

    <!-- 统计卡片 -->
    <n-grid cols="1 s:2 l:4" responsive="screen" :x-gap="16">
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="总计" :value="job?.total || 0" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="通过">
            <template #default><span style="color:#18a058;font-size:28px;font-weight:bold">{{ job?.passed || 0 }}</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="失败">
            <template #default><span style="color:#d03050;font-size:28px;font-weight:bold">{{ job?.failed || 0 }}</span></template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card style="text-align:center">
          <n-statistic label="通过率">
            <template #default>
              <span :style="{ color: passRate >= 90 ? '#18a058' : passRate >= 60 ? '#f0a020' : '#d03050', fontSize: '28px', fontWeight: 'bold' }">
                {{ passRate.toFixed(1) }}%
              </span>
            </template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 失败原因分析 -->
    <n-card v-if="job && (job.failed > 0 || job.errored > 0)" title="失败原因分析">
      <n-spin :show="analysisLoading">
        <n-grid cols="1 s:2 l:5" responsive="screen" :x-gap="12">
          <n-grid-item v-for="cat in analysisCategories" :key="cat.key">
            <div class="analysis-card">
              <div class="analysis-icon">{{ cat.icon }}</div>
              <div class="analysis-label">{{ cat.label }}</div>
              <div class="analysis-count" :style="{ color: cat.color }">{{ cat.count }}</div>
              <n-progress
                type="line"
                :percentage="cat.percentage"
                :color="cat.color"
                :rail-color="'#f0f0f0'"
                :indicator-placement="'inside'"
                style="margin-top:6px"
              />
              <div class="analysis-pct">{{ cat.percentage.toFixed(0) }}%</div>
            </div>
          </n-grid-item>
        </n-grid>
      </n-spin>
    </n-card>

    <!-- 逐条结果 -->
    <n-card title="逐条结果">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="resultFilter"
            :options="resultFilterOptions"
            clearable
            placeholder="按状态筛选"
            style="width:160px"
            @update:value="reloadResultsFromFirstPage"
          />
        </n-space>
      </template>
      <n-data-table
        :columns="resultColumns"
        :data="results"
        :loading="resultsLoading"
        :pagination="resultPagination"
        remote
        size="small"
      />
    </n-card>

    <n-card title="回放审计日志">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="auditEventType"
            clearable
            :options="auditEventOptions"
            placeholder="事件类型"
            style="width: 180px"
            @update:value="reloadAuditLogsFromFirstPage"
          />
          <n-button @click="loadAuditLogs">刷新日志</n-button>
        </n-space>
      </template>
      <n-data-table
        :columns="auditColumns"
        :data="auditLogs"
        :loading="auditLoading"
        :pagination="auditPagination"
        remote
        size="small"
      />
    </n-card>
  </n-space>

  <n-modal v-model:show="showAuditDetail" preset="card" style="width: 760px" title="回放审计详情">
    <n-space vertical :size="12">
      <n-descriptions bordered :column="2" size="small">
        <n-descriptions-item label="事件">{{ selectedAuditLog?.event_type || '-' }}</n-descriptions-item>
        <n-descriptions-item label="时间">{{ formatDateTime(selectedAuditLog?.created_at) }}</n-descriptions-item>
        <n-descriptions-item label="目标">{{ selectedAuditLog?.target_url || '-' }}</n-descriptions-item>
        <n-descriptions-item label="交易码">{{ selectedAuditLog?.transaction_code || '-' }}</n-descriptions-item>
        <n-descriptions-item label="状态码">{{ selectedAuditLog?.actual_status_code ?? '-' }}</n-descriptions-item>
        <n-descriptions-item label="耗时">{{ selectedAuditLog?.latency_ms != null ? `${selectedAuditLog.latency_ms}ms` : '-' }}</n-descriptions-item>
        <n-descriptions-item label="消息" :span="2">{{ selectedAuditLog?.message || '-' }}</n-descriptions-item>
      </n-descriptions>
      <n-card size="small" title="Detail JSON">
        <pre class="code-block compact">{{ prettyText(selectedAuditLog?.detail) }}</pre>
      </n-card>
    </n-space>
  </n-modal>

  <!-- 对比详情弹窗 -->
  <n-modal v-model:show="showDiff" preset="card" style="width:1000px" title="结果对比详情">
    <n-space vertical :size="12">
      <n-descriptions bordered :column="3" size="small">
        <n-descriptions-item label="接口">
          <b>{{ selectedResult?.request_method }}</b> {{ selectedResult?.request_uri }}
        </n-descriptions-item>
        <n-descriptions-item label="状态码">{{ selectedResult?.actual_status_code || '-' }}</n-descriptions-item>
        <n-descriptions-item label="Diff Score">
          <span :style="{ color: diffScoreColor(selectedResult?.diff_score) }">
            {{ selectedResult?.diff_score != null ? selectedResult.diff_score.toFixed(3) : '-' }}
          </span>
        </n-descriptions-item>
        <n-descriptions-item label="来源录制">
          <n-space align="center" :size="8">
            <n-tag :type="selectedResult?.use_sub_invocation_mocks ? 'success' : 'default'" size="small">
              {{ selectedResult?.use_sub_invocation_mocks ? 'Mock 开启' : 'Mock 关闭' }}
            </n-tag>
            <span>{{ selectedResult?.source_recording_id ? `#${selectedResult.source_recording_id}` : '-' }}</span>
          </n-space>
        </n-descriptions-item>
        <n-descriptions-item label="子调用数">{{ selectedResult?.source_recording_sub_call_count ?? '-' }}</n-descriptions-item>
        <n-descriptions-item label="失败分类" :span="2">
          {{ failureCategoryLabelMap[selectedResult?.failure_category || ''] || selectedResult?.failure_category || '-' }}
        </n-descriptions-item>
        <n-descriptions-item label="耗时">{{ selectedResult?.latency_ms != null ? `${selectedResult.latency_ms}ms` : '-' }}</n-descriptions-item>
      </n-descriptions>

      <n-grid cols="1 l:2" responsive="screen" :x-gap="16">
        <n-grid-item>
          <n-card title="期望响应（SIT 录制）" size="small">
            <pre class="code-block">{{ rawText(selectedResult?.expected_response) }}</pre>
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card title="实际响应（UAT 回放）" size="small">
            <pre class="code-block">{{ rawText(selectedResult?.actual_response) }}</pre>
          </n-card>
        </n-grid-item>
      </n-grid>

      <n-card v-if="sourceRecording" title="来源录制链路" size="small">
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
        <div style="margin-top: 12px">
          <SubCallPanel :sub-calls="sourceRecording.sub_calls" />
        </div>
      </n-card>

      <n-tabs type="line" animated>
        <n-tab-pane name="diff" tab="差异详情">
          <n-card size="small" :bordered="false">
            <n-space vertical>
              <div>
                <div class="section-title">Diff 结果</div>
                <pre class="code-block compact">{{ prettyText(selectedResult?.diff_result) }}</pre>
              </div>
              <n-card v-if="ruleSuggestions.length > 0" size="small" title="规则修复建议">
                <n-space vertical :size="8">
                  <div v-for="item in ruleSuggestions" :key="item.key" class="rule-suggestion-row">
                    <n-space align="center" justify="space-between" style="width: 100%">
                      <n-space align="center" :size="8">
                        <n-tag type="warning" size="small">{{ item.field }}</n-tag>
                        <span class="suggestion-path">{{ item.path }}</span>
                        <span class="suggestion-change">{{ item.change_types.join(', ') }}</span>
                      </n-space>
                      <n-space v-if="canEdit" :size="6">
                        <n-button
                          size="tiny"
                          :loading="applyingSuggestionKey === `${item.key}:job_ignore_fields`"
                          @click="applyRuleSuggestion(item.key, 'job_ignore_fields')"
                        >
                          加入本任务
                        </n-button>
                        <n-button
                          size="tiny"
                          type="primary"
                          ghost
                          :loading="applyingSuggestionKey === `${item.key}:application_default_ignore_fields`"
                          @click="applyRuleSuggestion(item.key, 'application_default_ignore_fields')"
                        >
                          加入应用默认
                        </n-button>
                      </n-space>
                    </n-space>
                  </div>
                </n-space>
              </n-card>
              <div v-if="parsedAssertionResults.length > 0">
                <div class="section-title">断言结果</div>
                <n-space vertical :size="6">
                  <div v-for="(item, i) in parsedAssertionResults" :key="i">
                    <n-tag :type="item.passed ? 'success' : 'error'" size="small">{{ item.passed ? '通过' : '失败' }}</n-tag>
                    <span style="margin-left:8px;font-size:12px">{{ item.message }}</span>
                  </div>
                </n-space>
              </div>
              <div v-if="selectedResult?.failure_reason">
                <div class="section-title">失败原因</div>
                <template v-if="failureReasonFields(selectedResult.failure_reason)">
                  <div style="font-size:13px;color:#555;margin-bottom:8px">
                    {{ failureReasonPrefix(selectedResult.failure_reason) }}
                  </div>
                  <n-space vertical :size="4">
                    <div
                      v-for="field in failureReasonFields(selectedResult.failure_reason)"
                      :key="field"
                      style="display:flex;align-items:center;gap:8px"
                    >
                      <n-tag type="error" size="small" style="font-family:monospace">{{ field }}</n-tag>
                    </div>
                  </n-space>
                </template>
                <pre v-else class="code-block compact">{{ selectedResult.failure_reason }}</pre>
              </div>
            </n-space>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="subcall" tab="子调用对比">
          <n-spin :show="subCallDiffLoading">
            <SubCallDiffPanel
              :pairs="subCallDiff?.pairs ?? []"
              :replayed="subCallDiff?.replayed ?? []"
            />
          </n-spin>
        </n-tab-pane>
      </n-tabs>
    </n-space>
  </n-modal>
</template>

<script setup lang="ts">
import {
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NGrid,
  NGridItem,
  NModal,
  NProgress,
  NSpace,
  NSelect,
  NSpin,
  NStatistic,
  NTabPane,
  NTabs,
  NTag,
} from 'naive-ui'
import SubCallPanel from '@/components/recording/SubCallPanel.vue'
import SubCallDiffPanel from '@/components/recording/SubCallDiffPanel.vue'
import { useJobDetail } from './useJobDetail'

const {
  router,
  canEdit,
  jobId,
  job,
  appName,
  results,
  resultsLoading,
  auditLogs,
  auditLoading,
  auditEventType,
  selectedAuditLog,
  showAuditDetail,
  resultFilter,
  showDiff,
  selectedResult,
  analysisLoading,
  sourceTestCase,
  sourceRecording,
  sourceRecordingSubCallSummary,
  subCallDiff,
  subCallDiffLoading,
  ruleSuggestions,
  applyingSuggestionKey,
  resultPagination,
  auditPagination,
  passRate,
  parsedAssertionResults,
  analysisCategories,
  jobStatusTypeMap,
  jobStatusLabelMap,
  failureCategoryLabelMap,
  resultFilterOptions,
  auditEventOptions,
  diffScoreColor,
  resultColumns,
  auditColumns,
  prettyText,
  rawText,
  failureReasonFields,
  failureReasonPrefix,
  applyRuleSuggestion,
  openReport,
  loadAuditLogs,
  loadPage,
  reloadResultsFromFirstPage,
  reloadAuditLogsFromFirstPage,
  formatDateTime
} = useJobDetail()
</script>

<style scoped>
.code-block {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 320px;
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  background: #f8f8f8;
  font-family: monospace;
  font-size: 12px;
}
.code-block.compact {
  max-height: 160px;
}
.section-title {
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #555;
}
.analysis-card {
  text-align: center;
  padding: 12px 8px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
}
.analysis-icon {
  font-size: 22px;
  margin-bottom: 4px;
}
.analysis-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}
.analysis-count {
  font-size: 24px;
  font-weight: bold;
  line-height: 1.2;
}
.analysis-pct {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.rule-suggestion-row {
  padding: 8px 10px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background: #fafafa;
}
.suggestion-path {
  font-family: monospace;
  font-size: 12px;
  color: #333;
}
.suggestion-change {
  font-size: 12px;
  color: #888;
}
</style>
