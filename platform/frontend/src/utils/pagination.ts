export type PagedResponse<T> = {
  items: T[]
  total: number
  skip: number
  limit: number
}

export function unpackPagedResponse<T>(payload: T[] | PagedResponse<T>) {
  if (Array.isArray(payload)) {
    return { items: payload, total: payload.length }
  }
  return {
    items: payload.items || [],
    total: Number(payload.total || 0),
  }
}

export function pageOffset(page: number, pageSize: number) {
  return (Math.max(page, 1) - 1) * pageSize
}

export function lastValidPage(total: number, pageSize: number) {
  return Math.max(1, Math.ceil(total / pageSize))
}

type ApiListResponse<T> = {
  data: T[] | PagedResponse<T>
}

export async function loadPagedData<T>(
  loader: (params?: any) => Promise<ApiListResponse<T>>,
  params: Record<string, unknown>,
  page: number,
  pageSize: number,
  fallbackLimit: number,
) {
  const requestParams = {
    ...params,
    skip: pageOffset(page, pageSize),
    limit: pageSize,
    include_total: true,
  }
  const res = await loader(requestParams)
  if (!Array.isArray(res.data)) {
    return unpackPagedResponse<T>(res.data)
  }

  // Compatibility for a running backend that has not picked up include_total yet.
  // In that case the first response is only the current slice, so fetch a legal
  // wider window and slice locally to keep pagination usable.
  const fallbackRes = await loader({
    ...params,
    skip: 0,
    limit: fallbackLimit,
  })
  const allItems = Array.isArray(fallbackRes.data) ? fallbackRes.data : fallbackRes.data.items
  const start = pageOffset(page, pageSize)
  return {
    items: allItems.slice(start, start + pageSize),
    total: allItems.length,
  }
}
