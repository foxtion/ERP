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
