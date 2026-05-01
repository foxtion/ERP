import request from '@/utils/request'

// ==================== 员工档案 ====================
export function getEmployeeList(params) {
  return request({ url: '/hr/employees/', method: 'get', params })
}
export function createEmployee(data) {
  return request({ url: '/hr/employees/', method: 'post', data })
}
export function updateEmployee(id, data) {
  return request({ url: `/hr/employees/${id}/`, method: 'put', data })
}
export function deleteEmployee(id) {
  return request({ url: `/hr/employees/${id}/`, method: 'delete' })
}
export function getEmployeeOptions() {
  return request({ url: '/hr/employees/options/', method: 'get' })
}
export function getEmployeeDetail(id) {
  return request({ url: `/hr/employees/${id}/`, method: 'get' })
}
export function generateEmployeeNo() {
  return request({ url: '/hr/employees/generate-no/', method: 'get' })
}
export function confirmEmployee(id) {
  return request({ url: `/hr/employees/${id}/confirm/`, method: 'post', data: {} })
}
export function resignEmployee(id) {
  return request({ url: `/hr/employees/${id}/resign/`, method: 'post', data: {} })
}
export function getEmployeeStats(id) {
  return request({ url: `/hr/employees/${id}/stats/`, method: 'get' })
}

// ==================== 职位管理 ====================
export function getPositionList(params) {
  return request({ url: '/hr/positions/', method: 'get', params })
}
export function createPosition(data) {
  return request({ url: '/hr/positions/', method: 'post', data })
}
export function updatePosition(id, data) {
  return request({ url: `/hr/positions/${id}/`, method: 'put', data })
}
export function deletePosition(id) {
  return request({ url: `/hr/positions/${id}/`, method: 'delete' })
}
export function getPositionsByDepartment(deptId) {
  return request({ url: '/hr/positions/by-department/', method: 'get', params: { dept_id: deptId } })
}

// ==================== 考勤记录 ====================
export function getAttendanceList(params) {
  return request({ url: '/hr/attendances/', method: 'get', params })
}
export function createAttendance(data) {
  return request({ url: '/hr/attendances/', method: 'post', data })
}
export function updateAttendance(id, data) {
  return request({ url: `/hr/attendances/${id}/`, method: 'put', data })
}
export function deleteAttendance(id) {
  return request({ url: `/hr/attendances/${id}/`, method: 'delete' })
}
export function getAttendanceStats(params) {
  return request({ url: '/hr/attendances/stats/', method: 'get', params })
}
export function getAttendanceDetail(id) {
  return request({ url: `/hr/attendances/${id}/`, method: 'get' })
}
export function bulkCreateAttendance(data) {
  return request({ url: '/hr/attendances/bulk/', method: 'post', data })
}

// ==================== 钉钉集成 ====================
export function getDingTalkConfig() {
  return request({ url: '/hr/dingtalk/config/', method: 'get' })
}
export function saveDingTalkConfig(data) {
  return request({ url: '/hr/dingtalk/config/', method: 'post', data })
}
export function testDingTalkConnection() {
  return request({ url: '/hr/dingtalk/test/', method: 'get' })
}
export function syncDingTalkAttendance() {
  return request({ url: '/hr/dingtalk/sync/', method: 'post', data: {} })
}

// ==================== 薪资管理 ====================
export function getSalaryList(params) {
  return request({ url: '/hr/salaries/', method: 'get', params })
}
export function createSalary(data) {
  return request({ url: '/hr/salaries/', method: 'post', data })
}
export function updateSalary(id, data) {
  return request({ url: `/hr/salaries/${id}/`, method: 'put', data })
}
export function deleteSalary(id) {
  return request({ url: `/hr/salaries/${id}/`, method: 'delete' })
}

// ==================== 招聘管理 ====================
export function getRecruitmentList(params) {
  return request({ url: '/hr/recruitments/', method: 'get', params })
}
export function createRecruitment(data) {
  return request({ url: '/hr/recruitments/', method: 'post', data })
}
export function updateRecruitment(id, data) {
  return request({ url: `/hr/recruitments/${id}/`, method: 'put', data })
}
export function deleteRecruitment(id) {
  return request({ url: `/hr/recruitments/${id}/`, method: 'delete' })
}
