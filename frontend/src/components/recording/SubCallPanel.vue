<template>
  <n-card title="子调用详情">
    <template #header-extra>
      <n-space :size="6" align="center">
        <n-tag type="info" size="small">{{ stats.total }} 条</n-tag>
        <n-tag type="default" size="small">{{ stats.expandedTotal }} 节点</n-tag>
        <n-tag
          v-for="(count, kind) in stats.kindCounts"
          :key="kind"
          size="small"
          :type="kindTagType(kind)"
        >
          {{ kind }} {{ count }}
        </n-tag>
        <n-tag
          v-for="(count, type) in stats.typeCounts"
          :key="type"
          size="small"
          :type="typeTagType(type)"
        >
          {{ type }} {{ count }}
        </n-tag>
      </n-space>
    </template>

    <n-empty v-if="subCalls.length === 0" description="当前录制未包含子调用信息" />

    <n-collapse v-else accordion display-directive="show">
      <n-collapse-item
        v-for="(item, index) in subCalls"
        :key="index"
        :name="index"
        :title="collapseTitle(item, index)"
      >
        <SubCallNode :item="item" :path="String(index + 1)" />
      </n-collapse-item>
    </n-collapse>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NCollapse, NCollapseItem, NEmpty, NSpace, NTag } from 'naive-ui'
import type { RecordingSubCall } from '@/utils/recording'
import {
  buildRecordingSubCallSummary,
  formatRecordingSubCallValue,
  getRecordingSubCallTypeLabel,
  getRecordingSubCallKind,
  getRecordingSubCallKindLabel,
  parseRecordingSubCalls,
  summarizeRecordingSubCalls,
} from '@/utils/recording'
import SubCallNode from '@/components/recording/SubCallNode.vue'

const props = defineProps<{
  subCalls?: RecordingSubCall[] | string | null
}>()

const subCalls = computed(() => parseRecordingSubCalls(props.subCalls))
const stats = computed(() => summarizeRecordingSubCalls(subCalls.value))
const summary = computed(() => buildRecordingSubCallSummary(subCalls.value))

function collapseTitle(item: RecordingSubCall, index: number) {
  const label = item.operation
    ? item.operation
    : formatRecordingSubCallValue(item.request).replace(/\s+/g, ' ').trim()
  const shortLabel = label.length > 80 ? `${label.slice(0, 80)}...` : label
  return `#${index + 1} ${getRecordingSubCallKindLabel(getRecordingSubCallKind(item))} · ${getRecordingSubCallTypeLabel(item.type)}${shortLabel ? ` · ${shortLabel}` : ''}`
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

defineExpose({
  summary,
})
</script>
