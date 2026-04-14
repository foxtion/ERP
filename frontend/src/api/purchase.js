import request from '@/utils/request'

// ==================== 供应商 ====================
export function getSupplierList(params) {
  return request({ url: '/purchase/suppliers/', method: 'get', params })
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

// ==================== 采购订单 ====================
export function getOrderList(params) {
  return request({ url: '/purchase/orders/', method: 'get', params })
}
export function createOrder(data) {
  return request({ url: '/purchase/orders/', method: 'post', data })
}
export function updateOrder(id, data) {
  return request({ url: `/purchase/orders/${id}/`, method: 'put', data })
}
export function deleteOrder(id) {
  return request({ url: `/purchase/orders/${id}/`, method: 'delete' })
}
export function getOrderOptions() {
  return request({ url: '/purchase/orders/options/', method: 'get' })
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
