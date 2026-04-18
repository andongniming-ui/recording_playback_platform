<template>
  <div>
    <n-alert v-if="!pairs.length" type="default" :show-icon="false" style="color:#999">
      {{ replayed.length === 0
          ? 'Agent 未上报子调用（回放时 AREX Agent 可能未启动或未配置录制模式）'
          : '暂无子调用数据' }}
    </n-alert>

    <n-space v-else vertical :size="12">
      <n-card
        v-for="pair in pairs"
        :key="pair.index"
        size="small"
        :style="{ borderLeft: `3px solid ${pairColor(pair)}` }"
      >
        <template #header>
          <n-space align="center" :size="8">
            <span style="font-weight:600">#{{ pair.index }}</span>
            <n-tag size="small" :type="typeTagType(pair.type)">{{ pair.type || '未知' }}</n-tag>
            <span style="color:#666;font-size:13px">{{ pairOperation(pair) }}</span>
          </n-space>
        </template>
        <template #header-extra>
          <n-tag :type="pairTagType(pair)" size="small">{{ pairLabel(pair) }}</n-tag>
        </template>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <div class="col-title">录制（System A）</div>
            <template v-if="pair.recorded">
              <div v-if="pair.recorded.operation" class="field-label">操作</div>
              <pre v-if="pair.recorded.operation" class="code-block compact">{{ pair.recorded.operation }}</pre>
              <div class="field-label">响应</div>
              <pre class="code-block" :class="{ diff: pair.side === 'both' && pair.response_matched === false }">{{ formatValue(pair.recorded.response) }}</pre>
            </template>
            <div v-else class="empty-side">— 仅回放侧有此调用 —</div>
          </n-grid-item>
          <n-grid-item>
            <div class="col-title">回放（System B）</div>
            <template v-if="pair.replayed">
              <div v-if="pair.replayed.operation" class="field-label">操作</div>
              <pre v-if="pair.replayed.operation" class="code-block compact">{{ pair.replayed.operation }}</pre>
              <div class="field-label">响应</div>
              <pre class="code-block" :class="{ diff: pair.side === 'both' && pair.response_matched === false }">{{ formatValue(pair.replayed.response) }}</pre>
            </template>
            <div v-else class="empty-side">— 仅录制侧有此调用 —</div>
          </n-grid-item>
        </n-grid>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { NAlert, NCard, NGrid, NGridItem, NSpace, NTag } from 'naive-ui'
import type { SubCallDiffPair, SubCallDiffItem } from '@/api/replays'

defineProps<{
  pairs: SubCallDiffPair[]
  replayed: SubCallDiffItem[]
}>()

function formatValue(value: unknown): string {
  if (value == null) return '-'
  if (typeof value === 'string') {
    try { return JSON.stringify(JSON.parse(value), null, 2) } catch { return value }
  }
  return JSON.stringify(value, null, 2)
}

function pairOperation(pair: SubCallDiffPair): string {
  const op = pair.recorded?.operation || pair.replayed?.operation || ''
  return op.length > 60 ? op.slice(0, 60) + '…' : op
}

function pairColor(pair: SubCallDiffPair): string {
  if (pair.side === 'recorded_only' || pair.side === 'replayed_only') return '#f0a020'
  if (pair.response_matched === false) return '#d03050'
  return '#18a058'
}

function pairTagType(pair: SubCallDiffPair): 'success' | 'error' | 'warning' | 'default' {
  if (pair.side === 'recorded_only' || pair.side === 'replayed_only') return 'warning'
  if (pair.response_matched === false) return 'error'
  return 'success'
}

function pairLabel(pair: SubCallDiffPair): string {
  if (pair.side === 'recorded_only') return '仅录制侧'
  if (pair.side === 'replayed_only') return '仅回放侧'
  if (pair.response_matched === false) return '响应差异'
  return '一致'
}

function typeTagType(type: string): 'warning' | 'info' | 'default' {
  const t = (type || '').toLowerCase()
  if (t.includes('mysql') || t.includes('jdbc')) return 'warning'
  if (t.includes('redis')) return 'info'
  return 'default'
}
</script>

<style scoped>
.col-title {
  font-size: 12px;
  font-weight: 600;
  color: #888;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.field-label {
  font-size: 12px;
  color: #aaa;
  margin: 6px 0 3px;
}
.code-block {
  margin: 0;
  padding: 8px 10px;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  border-radius: 4px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
  font-family: monospace;
  font-size: 12px;
}
.code-block.compact {
  max-height: 60px;
}
.code-block.diff {
  border-color: #ffb3b3;
  background: #fff5f5;
}
.empty-side {
  color: #ccc;
  font-size: 13px;
  padding: 20px 0;
  text-align: center;
}
</style>
