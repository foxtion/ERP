import request from '@/utils/request'

// ==================== 供应商 ====================
export function getSupplierList(params) {
  return request({ url: '/purchase/suppliers/', method: 'get', params })
}
export function getSupplierOptions() {
  return request({ url: '/purchase/suppliers/', method: 'get', params: { page: 1, size: 500 } })
}
export function createSupplier(data) {
  return request({ url: '/purchase/suppliers/', method: 'post', data })
}
export function updateSupplier(id, data) {
  return request({ url: `/purchase/suppliers/${id}/`, method: 'put', data })
}
export function deleteSupplier(id) {
  return request({ url: `/purchase/suppliers/${id}/`, method: 'delete' })
}
export function toggleSupplierStatus(id) {
  return request({ url: `/purchase/suppliers/${id}/toggle_status/`, method: 'post', data: {} })
}
export function exportSuppliers(params) {
  return request({ url: '/purchase/suppliers/export/', method: 'get', params, responseType: 'blob' })
}
export function importSuppliers(data) {
  return request({ url: '/purchase/suppliers/import/', method: 'post', data })
}
export function getSupplierDetail(id) {
  return request({ url: `/purchase/suppliers/${id}/`, method: 'get' })
}

// ==================== 采购申请 ====================
export function getRequestList(params) {
  return request({ url: '/purchase/requests/', method: 'get', params })
}
export function createRequest(data) {
  return request({ url: '/purchase/requests/', method: 'post', data })
}
export function updateRequest(id, data) {
  return request({ url: `/purchase/requests/${id}/`, method: 'put', data })
}
export function deleteRequest(id) {
  return request({ url: `/purchase/requests/${id}/`, method: 'delete' })
}
export function convertRequestToOrder(id) {
  return request({ url: `/purchase/requests/${id}/convert_to_order/`, method: 'post', data: {} })
}

// ==================== 采购订单 ====================
export function getPurchaseOrderList(params) {
  return request({ url: '/purchase/orders/', method: 'get', params })
}
export function createPurchaseOrder(data) {
  return request({ url: '/purchase/orders/', method: 'post', data })
}
export function updatePurchaseOrder(id, data) {
  return request({ url: `/purchase/orders/${id}/`, method: 'put', data })
}
export function deletePurchaseOrder(id) {
  return request({ url: `/purchase/orders/${id}/`, method: 'delete' })
}
export function confirmPurchaseOrder(id) {
  return request({ url: `/purchase/orders/${id}/confirm/`, method: 'post', data: {} })
}
export function cancelPurchaseOrder(id) {
  return request({ url: `/purchase/orders/${id}/cancel/`, method: 'post', data: {} })
}
export function completePurchaseOrder(id) {
  return request({ url: `/purchase/orders/${id}/complete/`, method: 'post', data: {} })
}
export function exportPurchaseOrders(params) {
  return request({ url: '/purchase/orders/export/', method: 'get', params, responseType: 'blob' })
}
export function getPurchaseOrderOptions() {
  return request({ url: '/purchase/orders/options/', method: 'get' })
}
export function submitRequest(id) {
  return request({ url: `/purchase/requests/${id}/submit/`, method: 'post', data: {} })
}
export function approveRequest(id) {
  return request({ url: `/purchase/requests/${id}/approve/`, method: 'post', data: {} })
}
export function rejectRequest(id) {
  return request({ url: `/purchase/requests/${id}/reject/`, method: 'post', data: {} })
}

export function getPurchaseOrderDetail(id) {
  return request({ url: `/purchase/orders/${id}/`, method: 'get' })
}

// ==================== 采购入库 ====================
export function getInStockList(params) {
  return request({ url: '/purchase/instocks/', method: 'get', params })
}
export function createInStock(data) {
  return request({ url: '/purchase/instocks/', method: 'post', data })
}
export function updateInStock(id, data) {
  return request({ url: `/purchase/instocks/${id}/`, method: 'put', data })
}
export function deleteInStock(id) {
  return request({ url: `/purchase/instocks/${id}/`, method: 'delete' })
}
