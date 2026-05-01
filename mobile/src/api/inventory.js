import request from '@/utils/request'

// ==================== 仓库 ====================
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
export function getWarehouseDetail(id) {
  return request({ url: `/inventory/warehouses/${id}/`, method: 'get' })
}
export function getWarehouseOptions() {
  return request({ url: '/inventory/warehouses/options/', method: 'get' })
}

// ==================== 库位 ====================
export function getLocationList(params) {
  return request({ url: '/inventory/locations/', method: 'get', params })
}
export function createLocation(data) {
  return request({ url: '/inventory/locations/', method: 'post', data })
}
export function updateLocation(id, data) {
  return request({ url: `/inventory/locations/${id}/`, method: 'put', data })
}
export function deleteLocation(id) {
  return request({ url: `/inventory/locations/${id}/`, method: 'delete' })
}

// ==================== 物料档案 ====================
export function getMaterialList(params) {
  return request({ url: '/inventory/materials/', method: 'get', params })
}
export function createMaterial(data) {
  return request({ url: '/inventory/materials/', method: 'post', data })
}
export function updateMaterial(id, data) {
  return request({ url: `/inventory/materials/${id}/`, method: 'put', data })
}
export function deleteMaterial(id) {
  return request({ url: `/inventory/materials/${id}/`, method: 'delete' })
}
export function patchMaterial(id, data) {
  return request({ url: `/inventory/materials/${id}/`, method: 'patch', data })
}
export function getMaterialOptions(params) {
  return request({ url: '/inventory/materials/options/', method: 'get', params })
}

// ==================== 库存查询 ====================
export function getStockList(params) {
  return request({ url: '/inventory/stocks/', method: 'get', params })
}
export function getStockStats() {
  return request({ url: '/inventory/stocks/stats/', method: 'get' })
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

// ==================== 库存预警 ====================
export function getWarningList(params) {
  return request({ url: '/inventory/warnings/', method: 'get', params })
}
export function handleWarning(id) {
  return request({ url: `/inventory/warnings/${id}/handle/`, method: 'post', data: {} })
}
export function getWarningStats() {
  return request({ url: '/inventory/warnings/stats/', method: 'get' })
}

// ==================== 库位商品映射 ====================
export function getLocationProducts(params) {
  return request({ url: '/inventory/locations/products/', method: 'get', params })
}
export function getLocationOptions(params) {
  return request({ url: '/inventory/locations/options/', method: 'get', params })
}
