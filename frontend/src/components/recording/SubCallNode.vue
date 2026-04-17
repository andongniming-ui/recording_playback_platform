<template>
  <n-card size="small" embedded :style="{ marginLeft: depth > 0 ? '12px' : '0' }">
    <template #header>
      <span>{{ title }}</span>
    </template>
    <template #header-extra>
      <n-space align="center" :size="8">
        <n-tag size="small" :type="kindTagType(getRecordingSubCallKind(item))">
          {{ getRecordingSubCallKindLabel(getRecordingSubCallKind(item)) }}
        </n-tag>
        <n-tag size="small" :type="typeTagType(item.type)">
          {{ getRecordingSubCallTypeLabel(item.type) }}
        </n-tag>
      </n-space>
    </template>

    <n-descriptions bordered :column="2" size="small">
      <n-descriptions-item label="类型">{{ getRecordingSubCallTypeLabel(item.type) }}</n-descriptions-item>
      <n-descriptions-item label="分类">{{ getRecordingSubCallKindLabel(getRecordingSubCallKind(item)) }}</n-descriptions-item>
      <n-descriptions-item label="耗时">{{ item.elapsed_ms != null ? `${item.elapsed_ms}ms` : '-' }}</n-descriptions-item>
      <n-descriptions-item label="目标" :span="2">{{ item.target || '-' }}</n-descriptions-item>
      <n-descriptions-item label="数据库">{{ item.database || '-' }}</n-descriptions-item>
      <n-descriptions-item label="操作">{{ item.operation || '-' }}</n-descriptions-item>
      <n-descriptions-item label="表名">{{ item.table || '-' }}</n-descriptions-item>
      <n-descriptions-item label="方法">{{ item.method || '-' }}</n-descriptions-item>
      <n-descriptions-item label="端点">{{ item.endpoint || '-' }}</n-descriptions-item>
      <n-descriptions-item label="Trace ID">{{ item.trace_id || '-' }}</n-descriptions-item>
      <n-descriptions-item label="Parent ID">{{ item.parent_id || '-' }}</n-descriptions-item>
      <n-descriptions-item label="Span ID">{{ item.span_id || '-' }}</n-descriptions-item>
      <n-descriptions-item label="线程">{{ item.thread_name || '-' }}</n-descriptions-item>
      <n-descriptions-item label="状态" :span="2">{{ item.status || '-' }}</n-descriptions-item>
      <n-descriptions-item label="错误" :span="2">{{ item.error || '-' }}</n-descriptions-item>
    </n-descriptions>

    <n-card v-if="sqlText(item) || item.params != null" size="small" title="SQL / 参数" style="margin-top: 12px">
      <n-space vertical :size="10">
        <div v-if="sqlText(item)">
          <div class="section-title">SQL</div>
          <pre class="code-block compact">{{ sqlText(item) }}</pre>
        </div>
        <div v-if="item.params != null">
          <div class="section-title">参数</div>
          <pre class="code-block compact">{{ formatRecordingSubCallValue(item.params) }}</pre>
        </div>
      </n-space>
    </n-card>

    <n-grid :cols="2" :x-gap="12" :y-gap="12" style="margin-top: 12px">
      <n-grid-item>
        <div class="section-title">请求</div>
        <pre class="code-block">{{ formatRecordingSubCallValue(item.request) }}</pre>
      </n-grid-item>
      <n-grid-item>
        <div class="section-title">响应</div>
        <pre class="code-block">{{ formatRecordingSubCallValue(item.response) }}</pre>
      </n-grid-item>
    </n-grid>

    <n-card v-if="item.children?.length" size="small" title="子调用链" style="margin-top: 12px">
      <n-space vertical :size="10">
        <SubCallNode
          v-for="(child, childIndex) in item.children"
          :key="`${path}.${childIndex + 1}`"
          :item="child"
          :path="`${path}.${childIndex + 1}`"
          :depth="depth + 1"
        />
      </n-space>
    </n-card>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NDescriptions, NDescriptionsItem, NGrid, NGridItem, NSpace, NTag } from 'naive-ui'
import type { RecordingSubCall } from '@/utils/recording'
import {
  formatRecordingSubCallValue,
  getRecordingSubCallTypeLabel,
  getRecordingSubCallKind,
  getRecordingSubCallKindLabel,
} from '@/utils/recording'

defineOptions({ name: 'SubCallNode' })

const props = withDefaults(defineProps<{
  item: RecordingSubCall
  path?: string
  depth?: number
}>(), {
  path: '1',
  depth: 0,
})

const title = computed(() => {
  const label = props.item.operation
    ? props.item.table
      ? `${props.item.operation} → ${props.item.table}`
      : props.item.operation
    : formatRecordingSubCallValue(props.item.request).replace(/\s+/g, ' ').trim()
  const shortLabel = label.length > 80 ? `${label.slice(0, 80)}...` : label
  return `#${props.path} ${getRecordingSubCallKindLabel(getRecordingSubCallKind(props.item))} · ${getRecordingSubCallTypeLabel(props.item.type)}${shortLabel ? ` · ${shortLabel}` : ''}`
})

function sqlText(item: RecordingSubCall) {
  if (item.sql) {
    return item.sql
  }
  if (typeof item.request === 'object' && item.request) {
    const request = item.request as Record<string, unknown>
    const sql = request.sql ?? request.statement ?? request.query
    return typeof sql === 'string' ? sql : null
  }
  return null
}

function typeTagType(type?: string | null) {
  const normalized = (type || '').toLowerCase()
  if (normalized.includes('mysql') || normalized.includes('jdbc')) return 'warning'
  if (normalized.includes('redis')) return 'info'
  if (normalized.includes('rpc')) return 'success'
  if (normalized.includes('http')) return 'default'
  return 'default'
}

function kindTagType(kind?: string | null) {
  if (kind === '数据库') return 'warning'
  if (kind === '缓存') return 'info'
  if (kind === 'RPC') return 'success'
  if (kind === 'HTTP') return 'default'
  if (kind === '消息') return 'primary'
  return 'default'
}
</script>

<style scoped>
.section-title {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #444;
}

.code-block {
  margin: 0;
  padding: 12px;
  min-height: 120px;
  max-height: 320px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  background: #fafafa;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}
.code-block.compact {
  min-height: 72px;
  max-height: 180px;
}
</style>
