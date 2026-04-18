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
export function toggleSupplierStatus(id) {
  return request({ url: `/purchase/suppliers/${id}/toggle_status/`, method: 'post' })
}
export function exportSuppliers(params) {
  return request({ url: '/purchase/suppliers/export/', method: 'get', params, responseType: 'blob' })
}
export function importSuppliers(data) {
  return request({ url: '/purchase/suppliers/import/', method: 'post', data })
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
export function confirmOrder(id) {
  return request({ url: `/purchase/orders/${id}/confirm/`, method: 'post' })
}
export function cancelOrder(id) {
  return request({ url: `/purchase/orders/${id}/cancel/`, method: 'post' })
}
export function completeOrder(id) {
  return request({ url: `/purchase/orders/${id}/complete/`, method: 'post' })
}
export function exportOrders(params) {
  return request({ url: '/purchase/orders/export/', method: 'get', params, responseType: 'blob' })
}
export function getOrderOptions() {
  return request({ url: '/purchase/orders/options/', method: 'get' })
}

// ==================== 采购申请转订单 ====================
export function convertRequestToOrder(id, data) {
  return request({ url: `/purchase/requests/${id}/convert_to_order/`, method: 'post', data })
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
