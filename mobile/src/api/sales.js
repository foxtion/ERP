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
export function getCustomerOptions() {
  return request({ url: '/sales/customers/options/', method: 'get' })
}
export function getCustomerDetail(id) {
  return request({ url: `/sales/customers/${id}/`, method: 'get' })
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
export function getSalesOrderDetail(id) {
  return request({ url: `/sales/orders/${id}/`, method: 'get' })
}
export function exportSalesOrders(params) {
  return request({ url: '/sales/orders/export/', method: 'get', params, responseType: 'blob' })
}
export function confirmOrder(id) {
  return request({ url: `/sales/orders/${id}/confirm/`, method: 'post', data: {} })
}
export function cancelOrder(id) {
  return request({ url: `/sales/orders/${id}/cancel/`, method: 'post', data: {} })
}
export function completeOrder(id) {
  return request({ url: `/sales/orders/${id}/complete/`, method: 'post', data: {} })
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
export function getOutStockDetail(id) {
  return request({ url: `/sales/outstocks/${id}/`, method: 'get' })
}
export function getPendingOutStockOrders() {
  return request({ url: '/sales/orders/pending-outstock/', method: 'get' })
}
export function getOrderOutStockItems(id) {
  return request({ url: `/sales/orders/${id}/outstock-items/`, method: 'get' })
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

// ==================== 拣货单 ====================
export function getPickingList(params) {
  return request({ url: '/sales/pickings/', method: 'get', params })
}
export function getPickingDetail(id) {
  return request({ url: `/sales/pickings/${id}/`, method: 'get' })
}
export function createPicking(data) {
  return request({ url: '/sales/pickings/', method: 'post', data })
}
export function updatePicking(id, data) {
  return request({ url: `/sales/pickings/${id}/`, method: 'put', data })
}
export function deletePicking(id) {
  return request({ url: `/sales/pickings/${id}/`, method: 'delete' })
}
export function createPickingFromOrder(orderId) {
  return request({ url: `/sales/orders/${orderId}/create-picking/`, method: 'post', data: {} })
}
export function assignPicking(id, assigneeId) {
  return request({ url: `/sales/pickings/${id}/assign/`, method: 'post', data: { assignee_id: assigneeId } })
}
export function acceptPicking(id) {
  return request({ url: `/sales/pickings/${id}/accept/`, method: 'post', data: {} })
}
export function pickItem(id, itemId, pickedQty, shortageQty) {
  return request({ url: `/sales/pickings/${id}/pick-item/`, method: 'post', data: { item_id: itemId, picked_qty: pickedQty, shortage_qty: shortageQty } })
}
export function reportShortage(id, itemId, remark) {
  return request({ url: `/sales/pickings/${id}/report-shortage/`, method: 'post', data: { item_id: itemId, remark } })
}
export function submitPicking(id) {
  return request({ url: `/sales/pickings/${id}/submit/`, method: 'post', data: {} })
}
export function refundItem(id, itemId) {
  return request({ url: `/sales/pickings/${id}/refund-item/`, method: 'post', data: { item_id: itemId } })
}
