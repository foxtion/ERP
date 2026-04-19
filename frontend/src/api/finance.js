import request from '@/utils/request'

// ==================== 会计科目 ====================
export function getSubjectList() {
  return request({ url: '/finance/subjects/', method: 'get' })
}
export function getSubjectFlat() {
  return request({ url: '/finance/subjects/flat/', method: 'get' })
}
export function createSubject(data) {
  return request({ url: '/finance/subjects/', method: 'post', data })
}
export function updateSubject(id, data) {
  return request({ url: `/finance/subjects/${id}/`, method: 'put', data })
}
export function deleteSubject(id) {
  return request({ url: `/finance/subjects/${id}/`, method: 'delete' })
}

// ==================== 记账凭证 ====================
export function getVoucherList(params) {
  return request({ url: '/finance/vouchers/', method: 'get', params })
}
export function createVoucher(data) {
  return request({ url: '/finance/vouchers/', method: 'post', data })
}
export function updateVoucher(id, data) {
  return request({ url: `/finance/vouchers/${id}/`, method: 'put', data })
}
export function deleteVoucher(id) {
  return request({ url: `/finance/vouchers/${id}/`, method: 'delete' })
}
export function auditVoucher(id) {
  return request({ url: `/finance/vouchers/${id}/audit/`, method: 'post' })
}
export function cancelAuditVoucher(id) {
  return request({ url: `/finance/vouchers/${id}/cancel_audit/`, method: 'post' })
}
export function generateVoucherNo() {
  return request({ url: '/finance/vouchers/generate_no/', method: 'get' })
}

// ==================== 应收应付 ====================
export function getReceivableList(params) {
  return request({ url: '/finance/receivables/', method: 'get', params })
}
export function createReceivable(data) {
  return request({ url: '/finance/receivables/', method: 'post', data })
}
export function updateReceivable(id, data) {
  return request({ url: `/finance/receivables/${id}/`, method: 'put', data })
}
export function deleteReceivable(id) {
  return request({ url: `/finance/receivables/${id}/`, method: 'delete' })
}
export function getOverdueReceivables(params) {
  return request({ url: '/finance/receivables/overdue/', method: 'get', params })
}

// ==================== 收款付款 ====================
export function getPaymentList(params) {
  return request({ url: '/finance/payments/', method: 'get', params })
}
export function createPayment(data) {
  return request({ url: '/finance/payments/', method: 'post', data })
}
export function updatePayment(id, data) {
  return request({ url: `/finance/payments/${id}/`, method: 'put', data })
}
export function deletePayment(id) {
  return request({ url: `/finance/payments/${id}/`, method: 'delete' })
}

// ==================== 核销明细 ====================
export function getSettlementList(params) {
  return request({ url: '/finance/settlements/', method: 'get', params })
}
export function createSettlement(data) {
  return request({ url: '/finance/settlements/', method: 'post', data })
}
export function deleteSettlement(id) {
  return request({ url: `/finance/settlements/${id}/`, method: 'delete' })
}
export function settlePayment(id, data) {
  return request({ url: `/finance/payments/${id}/settle/`, method: 'post', data })
}
export function cancelSettlement(id) {
  return request({ url: `/finance/settlements/${id}/cancel/`, method: 'post' })
}

// ==================== 对账单 ====================
export function getStatement(params) {
  return request({ url: '/finance/statement/', method: 'get', params })
}

// ==================== 财务汇总 ====================
export function getFinanceSummary() {
  return request({ url: '/finance/summary/', method: 'get' })
}
