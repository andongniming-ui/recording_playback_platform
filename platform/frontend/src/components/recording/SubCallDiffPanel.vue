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

        <div v-if="pair.side === 'both' && pair.response_matched === false" class="diff-summary">
          <div class="field-label">差异字段</div>
          <n-space :size="6" wrap>
            <n-tag
              v-for="path in diffPaths(pair)"
              :key="path"
              type="error"
              size="small"
              style="font-family: monospace"
            >
              {{ path }}
            </n-tag>
          </n-space>
        </div>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <div class="col-title">录制侧</div>
            <template v-if="pair.recorded">
              <div v-if="pair.recorded.operation" class="field-label">操作</div>
              <pre v-if="pair.recorded.operation" class="code-block compact">{{ pair.recorded.operation }}</pre>
              <div class="field-label">响应</div>
              <pre class="code-block" :class="{ diff: pair.side === 'both' && pair.response_matched === false }">{{ formatValue(pair.recorded.response) }}</pre>
            </template>
            <div v-else class="empty-side">— 仅回放侧有此调用 —</div>
          </n-grid-item>
          <n-grid-item>
            <div class="col-title">回放侧</div>
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

function parseStructuredValue(value: unknown): unknown {
  if (typeof value !== 'string') return value
  const text = value.trim()
  if (!text) return value
  if (!((text.startsWith('{') && text.endsWith('}')) || (text.startsWith('[') && text.endsWith(']')))) {
    return value
  }
  try {
    return JSON.parse(text)
  } catch {
    return value
  }
}

function toComparableNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value !== 'string') return null
  const text = value.trim()
  if (!/^[+-]?\d+(\.\d+)?$/.test(text)) return null
  const parsed = Number(text)
  return Number.isFinite(parsed) ? parsed : null
}

function valuesEqual(left: unknown, right: unknown): boolean {
  const normalizedLeft = parseStructuredValue(left)
  const normalizedRight = parseStructuredValue(right)

  if (Array.isArray(normalizedLeft) && Array.isArray(normalizedRight)) {
    return normalizedLeft.length === normalizedRight.length
      && normalizedLeft.every((item, index) => valuesEqual(item, normalizedRight[index]))
  }

  if (
    normalizedLeft !== null
    && normalizedRight !== null
    && typeof normalizedLeft === 'object'
    && typeof normalizedRight === 'object'
    && !Array.isArray(normalizedLeft)
    && !Array.isArray(normalizedRight)
  ) {
    const leftKeys = Object.keys(normalizedLeft as Record<string, unknown>).sort()
    const rightKeys = Object.keys(normalizedRight as Record<string, unknown>).sort()
    if (leftKeys.length !== rightKeys.length) return false
    if (leftKeys.some((key, index) => key !== rightKeys[index])) return false
    return leftKeys.every((key) =>
      valuesEqual(
        (normalizedLeft as Record<string, unknown>)[key],
        (normalizedRight as Record<string, unknown>)[key],
      ),
    )
  }

  const leftNumber = toComparableNumber(normalizedLeft)
  const rightNumber = toComparableNumber(normalizedRight)
  if (leftNumber !== null && rightNumber !== null) return leftNumber === rightNumber

  return normalizedLeft === normalizedRight
}

function collectDiffPaths(left: unknown, right: unknown, basePath = 'response'): string[] {
  const normalizedLeft = parseStructuredValue(left)
  const normalizedRight = parseStructuredValue(right)

  if (valuesEqual(normalizedLeft, normalizedRight)) return []

  if (Array.isArray(normalizedLeft) && Array.isArray(normalizedRight)) {
    const maxLength = Math.max(normalizedLeft.length, normalizedRight.length)
    const paths: string[] = []
    for (let index = 0; index < maxLength; index += 1) {
      const nextPath = `${basePath}[${index}]`
      if (index >= normalizedLeft.length || index >= normalizedRight.length) {
        paths.push(nextPath)
        continue
      }
      paths.push(...collectDiffPaths(normalizedLeft[index], normalizedRight[index], nextPath))
    }
    return paths
  }

  if (
    normalizedLeft !== null
    && normalizedRight !== null
    && typeof normalizedLeft === 'object'
    && typeof normalizedRight === 'object'
    && !Array.isArray(normalizedLeft)
    && !Array.isArray(normalizedRight)
  ) {
    const keys = Array.from(new Set([
      ...Object.keys(normalizedLeft as Record<string, unknown>),
      ...Object.keys(normalizedRight as Record<string, unknown>),
    ])).sort()
    const paths: string[] = []
    for (const key of keys) {
      const nextPath = `${basePath}.${key}`
      const hasLeft = Object.prototype.hasOwnProperty.call(normalizedLeft, key)
      const hasRight = Object.prototype.hasOwnProperty.call(normalizedRight, key)
      if (!hasLeft || !hasRight) {
        paths.push(nextPath)
        continue
      }
      paths.push(...collectDiffPaths(
        (normalizedLeft as Record<string, unknown>)[key],
        (normalizedRight as Record<string, unknown>)[key],
        nextPath,
      ))
    }
    return paths
  }

  return [basePath]
}

function diffPaths(pair: SubCallDiffPair): string[] {
  if (!pair.recorded || !pair.replayed) return []
  const paths = collectDiffPaths(pair.recorded.response, pair.replayed.response)
  return paths.length ? paths : ['response']
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
.diff-summary {
  margin-bottom: 10px;
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
