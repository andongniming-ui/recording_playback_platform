export type TableSortOrder = 'ascend' | 'descend' | false

export type TableSortState = {
  columnKey: string
  order: TableSortOrder
}

export function defaultSortState(columnKey: string, order: Exclude<TableSortOrder, false> = 'descend'): TableSortState {
  return { columnKey, order }
}

export function resolveSortOrder(state: TableSortState, columnKey: string): TableSortOrder {
  return state.columnKey === columnKey ? state.order : false
}

export function updateSortState(
  sorter: { columnKey?: string; order?: TableSortOrder } | null | undefined,
  fallbackColumnKey: string,
  fallbackOrder: Exclude<TableSortOrder, false> = 'descend',
): TableSortState {
  if (!sorter?.columnKey || !sorter.order) {
    return defaultSortState(fallbackColumnKey, fallbackOrder)
  }
  return {
    columnKey: String(sorter.columnKey),
    order: sorter.order,
  }
}

export function toApiSortOrder(order: TableSortOrder): 'asc' | 'desc' {
  return order === 'ascend' ? 'asc' : 'desc'
}
