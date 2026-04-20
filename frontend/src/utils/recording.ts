export type RecordingSubCall = {
  type?: string | null
  source?: string | null
  target?: string | null
  database?: string | null
  operation?: string | null
  table?: string | null
  method?: string | null
  endpoint?: string | null
  sql?: string | null
  params?: unknown
  request?: unknown
  response?: unknown
  elapsed_ms?: number | null
  status?: string | null
  trace_id?: string | null
  parent_id?: string | null
  span_id?: string | null
  thread_name?: string | null
  error?: string | null
  children?: RecordingSubCall[] | null
}

export type RecordingSubCallStats = {
  total: number
  expandedTotal: number
  typeCounts: Record<string, number>
  kindCounts: Record<string, number>
}

const TYPE_LABELS: Record<string, string> = {
  mysql: 'MySQL',
  jdbc: 'JDBC',
  redis: 'Redis',
  rpc: 'RPC',
  http: 'HTTP',
  mq: 'MQ',
  kafka: 'Kafka',
  risk: '风控',
  business: '业务',
}

const KIND_LABELS: Record<string, string> = {
  database: '数据库',
  cache: '缓存',
  rpc: 'RPC',
  http: 'HTTP',
  messaging: '消息',
  other: '其他',
}

const SOURCE_LABELS: Record<string, string> = {
  agent: '原始录制',
  reconstructed: '增强补建',
}

function parseJsonLike(value: string) {
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

function normalizePrimitive(value: unknown): unknown {
  if (value === null || value === undefined) {
    return null
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) {
      return null
    }
    const parsed = parseJsonLike(trimmed)
    return parsed ?? trimmed
  }
  return value
}

function extractScalar(raw: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = raw[key]
    if (value !== null && value !== undefined && value !== '') {
      return value
    }
  }
  return null
}

function normalizeSubCall(item: unknown): RecordingSubCall {
  if (!item || typeof item !== 'object' || Array.isArray(item)) {
    return {
      type: 'UNKNOWN',
      request: normalizePrimitive(item),
      response: null,
    }
  }

  const raw = item as Record<string, unknown>
  const type =
    (raw.type as string | undefined)
    || (raw.callType as string | undefined)
    || (raw.category as string | undefined)
    || (raw.subCallType as string | undefined)
    || (raw.invocationType as string | undefined)
    || (raw.name as string | undefined)
    || 'UNKNOWN'

  const request =
    extractScalar(raw, ['request', 'sql', 'statement', 'command', 'query', 'body', 'detail', 'params', 'arguments'])
    ?? null

  const response =
    extractScalar(raw, ['response', 'result', 'returnValue', 'output', 'responseBody', 'value', 'rows'])
    ?? null

  const target = extractScalar(raw, ['target', 'db', 'service', 'host', 'endpoint', 'datasource'])
  const database = extractScalar(raw, ['database', 'dbName', 'schema', 'catalog', 'datasource'])
  const operation = extractScalar(raw, ['operation', 'operationName', 'methodName', 'action', 'command'])
  const table = extractScalar(raw, ['table', 'tableName', 'collection'])
  const method = extractScalar(raw, ['method', 'httpMethod', 'rpcMethod', 'verb'])
  const endpoint = extractScalar(raw, ['endpoint', 'path', 'uri', 'url'])
  const sql = extractScalar(raw, ['sql', 'statement', 'query'])
  const params = extractScalar(raw, ['params', 'parameters', 'args', 'arguments'])
  const elapsedRaw = raw.elapsed_ms ?? raw.elapsedMs ?? raw.duration ?? raw.cost ?? raw.latencyMs ?? raw.elapsed
  const childrenRaw = raw.children ?? raw.subCalls ?? raw.subInvocations ?? raw.sub_invocations ?? raw.items

  const elapsed_ms = typeof elapsedRaw === 'number'
    ? elapsedRaw
    : typeof elapsedRaw === 'string' && elapsedRaw.trim()
      ? Number(elapsedRaw)
      : null

  return {
    type: String(type).trim() || 'UNKNOWN',
    source: typeof raw.source === 'string' ? raw.source : raw.source != null ? String(raw.source) : null,
    target: typeof target === 'string' ? target : target != null ? String(target) : null,
    database: typeof database === 'string' ? database : database != null ? String(database) : null,
    operation: typeof operation === 'string' ? operation : operation != null ? String(operation) : null,
    table: typeof table === 'string' ? table : table != null ? String(table) : null,
    method: typeof method === 'string' ? method : method != null ? String(method) : null,
    endpoint: typeof endpoint === 'string' ? endpoint : endpoint != null ? String(endpoint) : null,
    sql: typeof sql === 'string' ? sql : sql != null ? String(sql) : null,
    params: normalizePrimitive(params),
    request: normalizePrimitive(request),
    response: normalizePrimitive(response),
    elapsed_ms: Number.isFinite(elapsed_ms ?? NaN) ? elapsed_ms : null,
    status: typeof raw.status === 'string' ? raw.status : raw.status != null ? String(raw.status) : null,
    trace_id: typeof raw.trace_id === 'string' ? raw.trace_id : typeof raw.traceId === 'string' ? raw.traceId : null,
    parent_id: typeof raw.parent_id === 'string' ? raw.parent_id : typeof raw.parentId === 'string' ? raw.parentId : null,
    span_id: typeof raw.span_id === 'string' ? raw.span_id : typeof raw.spanId === 'string' ? raw.spanId : null,
    thread_name: typeof raw.thread_name === 'string' ? raw.thread_name : typeof raw.threadName === 'string' ? raw.threadName : null,
    error: typeof raw.error === 'string' ? raw.error : typeof raw.error_message === 'string' ? raw.error_message : typeof raw.message === 'string' ? raw.message : null,
    children: Array.isArray(childrenRaw) ? childrenRaw.map((child) => normalizeSubCall(child)) : null,
  }
}

export function parseRecordingSubCalls(value?: RecordingSubCall[] | string | null): RecordingSubCall[] {
  if (!value) {
    return []
  }
  if (Array.isArray(value)) {
    return value.map((item) => normalizeSubCall(item))
  }
  if (typeof value === 'string') {
    const parsed = parseJsonLike(value)
    if (Array.isArray(parsed)) {
      return parsed.map((item) => normalizeSubCall(item))
    }
    if (parsed && typeof parsed === 'object') {
      const candidate = parsed as Record<string, unknown>
      const nested = candidate.items || candidate.subCalls || candidate.subCallInfo || candidate.sub_invocations || candidate.subInvocations
      if (Array.isArray(nested)) {
        return nested.map((item) => normalizeSubCall(item))
      }
      return [normalizeSubCall(parsed)]
    }
  }
  return []
}

function flattenRecordingSubCalls(subCalls: RecordingSubCall[]): RecordingSubCall[] {
  const result: RecordingSubCall[] = []
  for (const item of subCalls) {
    result.push(item)
    if (item.children?.length) {
      result.push(...flattenRecordingSubCalls(item.children))
    }
  }
  return result
}

export function formatRecordingSubCallValue(value: unknown): string {
  const normalized = normalizePrimitive(value)
  if (normalized === null || normalized === undefined) {
    return '-'
  }
  if (typeof normalized === 'string') {
    return normalized
  }
  try {
    return JSON.stringify(normalized, null, 2)
  } catch {
    return String(normalized)
  }
}

export function getRecordingSubCallTypeLabel(value?: string | null): string {
  if (!value) {
    return 'UNKNOWN'
  }
  const normalized = value.trim()
  if (!normalized) {
    return 'UNKNOWN'
  }
  const lower = normalized.toLowerCase()
  return TYPE_LABELS[lower] || normalized
}

export function getRecordingSubCallKind(item: RecordingSubCall) {
  const type = (item.type || '').toLowerCase()
  const target = `${item.target || ''} ${item.database || ''} ${item.operation || ''} ${item.endpoint || ''}`.toLowerCase()
  const sqlText = `${item.sql || ''} ${typeof item.request === 'string' ? item.request : ''}`.toLowerCase()

  if (type.includes('mysql') || type.includes('jdbc') || sqlText.includes('select ') || sqlText.includes('insert ') || sqlText.includes('update ') || sqlText.includes('delete ') || target.includes('mysql') || target.includes('jdbc') || target.includes('database')) {
    return 'database'
  }
  if (type.includes('redis') || target.includes('redis') || target.includes('cache')) {
    return 'cache'
  }
  if (type.includes('rpc') || type.includes('dubbo') || type.includes('grpc') || target.includes('rpc') || target.includes('dubbo') || target.includes('grpc')) {
    return 'rpc'
  }
  if (type.includes('mq') || type.includes('kafka') || type.includes('rabbit') || target.includes('kafka') || target.includes('queue') || target.includes('mq')) {
    return 'messaging'
  }
  if (type.includes('http') || target.includes('http') || target.includes('url') || item.method || item.endpoint) {
    return 'http'
  }
  return 'other'
}

export function getRecordingSubCallKindLabel(kind?: string | null): string {
  if (!kind) return KIND_LABELS.other
  return KIND_LABELS[kind] || kind
}

export function getRecordingSubCallSourceLabel(source?: string | null): string {
  if (!source) {
    return '未标记'
  }
  const normalized = source.trim().toLowerCase()
  return SOURCE_LABELS[normalized] || source
}

export function summarizeRecordingSubCalls(subCalls: RecordingSubCall[]) {
  const typeCounts: Record<string, number> = {}
  const kindCounts: Record<string, number> = {}
  const allCalls = flattenRecordingSubCalls(subCalls)

  for (const item of allCalls) {
    const typeLabel = getRecordingSubCallTypeLabel(item.type)
    const kindLabel = getRecordingSubCallKindLabel(getRecordingSubCallKind(item))
    typeCounts[typeLabel] = (typeCounts[typeLabel] || 0) + 1
    kindCounts[kindLabel] = (kindCounts[kindLabel] || 0) + 1
  }

  return {
    total: subCalls.length,
    expandedTotal: allCalls.length,
    typeCounts,
    kindCounts,
  } satisfies RecordingSubCallStats
}

export function buildRecordingSubCallSummary(subCalls: RecordingSubCall[]) {
  const stats = summarizeRecordingSubCalls(subCalls)
  const kindSummary = Object.entries(stats.kindCounts)
    .map(([type, count]) => `${type} ${count}`)
    .join(' / ')
  return kindSummary || '无细分'
}
