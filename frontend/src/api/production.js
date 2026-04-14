import request from '@/utils/request'

// ==================== BOM管理 ====================
export function getBomList(params) {
  return request({ url: '/production/boms/', method: 'get', params })
}
export function createBom(data) {
  return request({ url: '/production/boms/', method: 'post', data })
}
export function updateBom(id, data) {
  return request({ url: `/production/boms/${id}/`, method: 'put', data })
}
export function deleteBom(id) {
  return request({ url: `/production/boms/${id}/`, method: 'delete' })
}
export function getBomOptions() {
  return request({ url: '/production/boms/options/', method: 'get' })
}

// ==================== 生产计划 ====================
export function getPlanList(params) {
  return request({ url: '/production/plans/', method: 'get', params })
}
export function createPlan(data) {
  return request({ url: '/production/plans/', method: 'post', data })
}
export function updatePlan(id, data) {
  return request({ url: `/production/plans/${id}/`, method: 'put', data })
}
export function deletePlan(id) {
  return request({ url: `/production/plans/${id}/`, method: 'delete' })
}

// ==================== 生产工单 ====================
export function getWorkOrderList(params) {
  return request({ url: '/production/orders/', method: 'get', params })
}
export function createWorkOrder(data) {
  return request({ url: '/production/orders/', method: 'post', data })
}
export function updateWorkOrder(id, data) {
  return request({ url: `/production/orders/${id}/`, method: 'put', data })
}
export function deleteWorkOrder(id) {
  return request({ url: `/production/orders/${id}/`, method: 'delete' })
}
export function getWorkOrderOptions() {
  return request({ url: '/production/orders/options/', method: 'get' })
}

// ==================== 领料单 ====================
export function getRequisitionList(params) {
  return request({ url: '/production/requisitions/', method: 'get', params })
}
export function createRequisition(data) {
  return request({ url: '/production/requisitions/', method: 'post', data })
}
export function updateRequisition(id, data) {
  return request({ url: `/production/requisitions/${id}/`, method: 'put', data })
}
export function deleteRequisition(id) {
  return request({ url: `/production/requisitions/${id}/`, method: 'delete' })
}

// ==================== 生产入库 ====================
export function getProductionInStockList(params) {
  return request({ url: '/production/instocks/', method: 'get', params })
}
export function createProductionInStock(data) {
  return request({ url: '/production/instocks/', method: 'post', data })
}
export function updateProductionInStock(id, data) {
  return request({ url: `/production/instocks/${id}/`, method: 'put', data })
}
export function deleteProductionInStock(id) {
  return request({ url: `/production/instocks/${id}/`, method: 'delete' })
}
