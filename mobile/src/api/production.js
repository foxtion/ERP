import request from '@/utils/request'

// ==================== BOM ====================
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
export function getBomDetail(id) {
  return request({ url: `/production/boms/${id}/`, method: 'get' })
}
export function copyBom(id) {
  return request({ url: `/production/boms/${id}/copy/`, method: 'post', data: {} })
}
export function getBomOptions() {
  return request({ url: '/production/boms/options/', method: 'get' })
}

// ==================== 生产计划 ====================
export function getPlanList(params) {
  return request({ url: '/production/plans/', method: 'get', params })
}
export function getPlanDetail(id) {
  return request({ url: `/production/plans/${id}/`, method: 'get' })
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
export function confirmPlan(id) {
  return request({ url: `/production/plans/${id}/confirm/`, method: 'post', data: {} })
}
export function completePlan(id) {
  return request({ url: `/production/plans/${id}/complete/`, method: 'post', data: {} })
}
export function cancelPlan(id) {
  return request({ url: `/production/plans/${id}/cancel/`, method: 'post', data: {} })
}
export function createOrderFromPlan(id) {
  return request({ url: `/production/plans/${id}/order/`, method: 'post', data: {} })
}
export function getPlanOptions() {
  return request({ url: '/production/plans/options/', method: 'get' })
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
export function releaseWorkOrder(id) {
  return request({ url: `/production/orders/${id}/release/`, method: 'post', data: {} })
}
export function startWorkOrder(id) {
  return request({ url: `/production/orders/${id}/start/`, method: 'post', data: {} })
}
export function completeWorkOrder(id) {
  return request({ url: `/production/orders/${id}/complete/`, method: 'post', data: {} })
}
export function cancelWorkOrder(id) {
  return request({ url: `/production/orders/${id}/cancel/`, method: 'post', data: {} })
}
export function createRequisitionFromOrder(id) {
  return request({ url: `/production/orders/${id}/requisition/`, method: 'post', data: {} })
}
export function createInStockFromOrder(id) {
  return request({ url: `/production/orders/${id}/instock/`, method: 'post', data: {} })
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
export function submitRequisition(id) {
  return request({ url: `/production/requisitions/${id}/submit/`, method: 'post', data: {} })
}
export function approveRequisition(id) {
  return request({ url: `/production/requisitions/${id}/approve/`, method: 'post', data: {} })
}
export function issueRequisition(id) {
  return request({ url: `/production/requisitions/${id}/issue/`, method: 'post', data: {} })
}
export function cancelRequisition(id) {
  return request({ url: `/production/requisitions/${id}/cancel/`, method: 'post', data: {} })
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
export function submitProductionInStock(id) {
  return request({ url: `/production/instocks/${id}/submit/`, method: 'post', data: {} })
}
export function approveProductionInStock(id) {
  return request({ url: `/production/instocks/${id}/approve/`, method: 'post', data: {} })
}
export function confirmProductionInStock(id) {
  return request({ url: `/production/instocks/${id}/confirm/`, method: 'post', data: {} })
}
export function cancelProductionInStock(id) {
  return request({ url: `/production/instocks/${id}/cancel/`, method: 'post', data: {} })
}
