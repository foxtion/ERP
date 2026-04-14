import request from '@/utils/request'

// ==================== 仓库管理 ====================
export function getWarehouseList(params) {
  return request({ url: '/inventory/warehouses/', method: 'get', params })
}
export function createWarehouse(data) {
  return request({ url: '/inventory/warehouses/', method: 'post', data })
}
export function updateWarehouse(id, data) {
  return request({ url: `/inventory/warehouses/${id}/`, method: 'put', data })
}
export function deleteWarehouse(id) {
  return request({ url: `/inventory/warehouses/${id}/`, method: 'delete' })
}
export function getWarehouseOptions() {
  return request({ url: '/inventory/warehouses/options/', method: 'get' })
}

// ==================== 库存查询 ====================
export function getStockList(params) {
  return request({ url: '/inventory/stocks/', method: 'get', params })
}

// ==================== 库存调拨 ====================
export function getTransferList(params) {
  return request({ url: '/inventory/transfers/', method: 'get', params })
}
export function createTransfer(data) {
  return request({ url: '/inventory/transfers/', method: 'post', data })
}
export function updateTransfer(id, data) {
  return request({ url: `/inventory/transfers/${id}/`, method: 'put', data })
}
export function deleteTransfer(id) {
  return request({ url: `/inventory/transfers/${id}/`, method: 'delete' })
}

// ==================== 库存盘点 ====================
export function getCheckList(params) {
  return request({ url: '/inventory/checks/', method: 'get', params })
}
export function createCheck(data) {
  return request({ url: '/inventory/checks/', method: 'post', data })
}
export function updateCheck(id, data) {
  return request({ url: `/inventory/checks/${id}/`, method: 'put', data })
}
export function deleteCheck(id) {
  return request({ url: `/inventory/checks/${id}/`, method: 'delete' })
}
