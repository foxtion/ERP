import request from '@/utils/request'

// ==================== 用户管理 ====================
export function getUserList(params) {
  return request({ url: '/system/users/', method: 'get', params })
}
export function createUser(data) {
  return request({ url: '/system/users/', method: 'post', data })
}
export function updateUser(id, data) {
  return request({ url: `/system/users/${id}/`, method: 'put', data })
}
export function deleteUser(id) {
  return request({ url: `/system/users/${id}/`, method: 'delete' })
}

// ==================== 角色管理 ====================
export function getRoleList(params) {
  return request({ url: '/system/roles/', method: 'get', params })
}
export function createRole(data) {
  return request({ url: '/system/roles/', method: 'post', data })
}
export function updateRole(id, data) {
  return request({ url: `/system/roles/${id}/`, method: 'put', data })
}
export function deleteRole(id) {
  return request({ url: `/system/roles/${id}/`, method: 'delete' })
}
export function getRoleMenus(id) {
  return request({ url: `/system/roles/${id}/menus/`, method: 'get' })
}
export function updateRoleMenus(id, data) {
  return request({ url: `/system/roles/${id}/menus/`, method: 'put', data })
}

// ==================== 菜单管理 ====================
export function getMenuList(params) {
  return request({ url: '/system/menus/', method: 'get', params })
}
export function createMenu(data) {
  return request({ url: '/system/menus/', method: 'post', data })
}
export function updateMenu(id, data) {
  return request({ url: `/system/menus/${id}/`, method: 'put', data })
}
export function deleteMenu(id) {
  return request({ url: `/system/menus/${id}/`, method: 'delete' })
}
export function getMenuTree() {
  return request({ url: '/system/menus/tree/', method: 'get' })
}
export function getMenuFlat() {
  return request({ url: '/system/menus/flat/', method: 'get' })
}

// ==================== 部门管理 ====================
export function getDeptList(params) {
  return request({ url: '/system/departments/', method: 'get', params })
}
export function createDept(data) {
  return request({ url: '/system/departments/', method: 'post', data })
}
export function updateDept(id, data) {
  return request({ url: `/system/departments/${id}/`, method: 'put', data })
}
export function deleteDept(id) {
  return request({ url: `/system/departments/${id}/`, method: 'delete' })
}
export function getDeptTree() {
  return request({ url: '/system/departments/tree/', method: 'get' })
}
