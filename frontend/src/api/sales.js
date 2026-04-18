import request from '@/utils/request'

// ==================== 客户管理 ====================
export function getCustomerList(params) {
  return request({ url: '/sales/customers/', method: 'get', params })
}
export function createCustomer(data) {
  return request({ url: '/sales/customers/', method: 'post', data })
}
export function updateCustomer(id, data) {
  return request({ url: `/sales/customers/${id}/`, method: 'put', data })
}
export function deleteCustomer(id) {
  return request({ url: `/sales/customers/${id}/`, method: 'delete' })
}
export function getCustomerStats(id) {
  return request({ url: `/sales/customers/${id}/stats/`, method: 'get' })
}
export function getCustomerDetailStats(id) {
  return request({ url: `/sales/customers/${id}/detail-stats/`, method: 'get' })
}
export function exportCustomers(params) {
  return request({ url: '/sales/customers/export/', method: 'get', params, responseType: 'blob' })
}

// ==================== 销售订单 ====================
export function getSalesOrderList(params) {
  return request({ url: '/sales/orders/', method: 'get', params })
}
export function createSalesOrder(data) {
  return request({ url: '/sales/orders/', method: 'post', data })
}
export function updateSalesOrder(id, data) {
  return request({ url: `/sales/orders/${id}/`, method: 'put', data })
}
export function deleteSalesOrder(id) {
  return request({ url: `/sales/orders/${id}/`, method: 'delete' })
}
export function getSalesOrderOptions() {
  return request({ url: '/sales/orders/options/', method: 'get' })
}

// ==================== 销售出库 ====================
export function getOutStockList(params) {
  return request({ url: '/sales/outstocks/', method: 'get', params })
}
export function createOutStock(data) {
  return request({ url: '/sales/outstocks/', method: 'post', data })
}
export function updateOutStock(id, data) {
  return request({ url: `/sales/outstocks/${id}/`, method: 'put', data })
}
export function deleteOutStock(id) {
  return request({ url: `/sales/outstocks/${id}/`, method: 'delete' })
}

// ==================== 销售退货 ====================
export function getReturnList(params) {
  return request({ url: '/sales/returns/', method: 'get', params })
}
export function createReturn(data) {
  return request({ url: '/sales/returns/', method: 'post', data })
}
export function updateReturn(id, data) {
  return request({ url: `/sales/returns/${id}/`, method: 'put', data })
}
export function deleteReturn(id) {
  return request({ url: `/sales/returns/${id}/`, method: 'delete' })
}
