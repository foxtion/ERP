import request from '@/utils/request'

// ==================== 会计科目 ====================
export function getSubjectList(params) {
  return request({ url: '/finance/subjects/', method: 'get', params })
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
export function getVoucherDetail(id) {
  return request({ url: `/finance/vouchers/${id}/`, method: 'get' })
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
  return request({ url: `/finance/vouchers/${id}/audit/`, method: 'post', data: {} })
}
export function cancelAuditVoucher(id) {
  return request({ url: `/finance/vouchers/${id}/cancel_audit/`, method: 'post', data: {} })
}
export function generateVoucherNo() {
  return request({ url: '/finance/vouchers/generate-no/', method: 'get' })
}

// ==================== 应收应付 ====================
export function getReceivableList(params) {
  return request({ url: '/finance/receivables/', method: 'get', params })
}
export function getReceivableDetail(id) {
  return request({ url: `/finance/receivables/${id}/`, method: 'get' })
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
export function getOverdueReceivables() {
  return request({ url: '/finance/receivables/overdue/', method: 'get' })
}

// ==================== 收付款 ====================
export function getPaymentList(params) {
  return request({ url: '/finance/payments/', method: 'get', params })
}
export function getPaymentDetail(id) {
  return request({ url: `/finance/payments/${id}/`, method: 'get' })
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
export function settlePayment(id) {
  return request({ url: `/finance/payments/${id}/settle/`, method: 'post', data: {} })
}
export function cancelSettlement(id) {
  return request({ url: `/finance/settlements/${id}/cancel/`, method: 'post', data: {} })
}

// ==================== 往来单位 ====================
export function getCounterpartyList(params) {
  return request({ url: '/finance/counterparties/', method: 'get', params })
}
export function createCounterparty(data) {
  return request({ url: '/finance/counterparties/', method: 'post', data })
}
export function updateCounterparty(id, data) {
  return request({ url: `/finance/counterparties/${id}/`, method: 'put', data })
}
export function deleteCounterparty(id) {
  return request({ url: `/finance/counterparties/${id}/`, method: 'delete' })
}
export function getCounterpartyOptions() {
  return request({ url: '/finance/counterparties/options/', method: 'get' })
}
export function getCounterpartyStats(id) {
  return request({ url: `/finance/counterparties/${id}/stats/`, method: 'get' })
}

// ==================== 对账单 ====================
export function getStatement(params) {
  return request({ url: '/finance/statement/', method: 'get', params })
}

// ==================== 往来余额 ====================
export function getBalanceSheet(params) {
  return request({ url: '/finance/balance/', method: 'get', params })
}

// ==================== 财务汇总 ====================
export function getFinanceSummary() {
  return request({ url: '/finance/summary/', method: 'get' })
}
