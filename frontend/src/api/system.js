import request from '@/utils/request'

// ==================== 用户管理 ====================
export function getUserList(params) {
  return request({ url: '/system/users/', method: 'get', params })
}

export function getUserDetail(id) {
  return request({ url: `/system/users/${id}/`, method: 'get' })
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

export function getRoleDetail(id) {
  return request({ url: `/system/roles/${id}/`, method: 'get' })
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

export function getRoleMenus(roleId) {
  return request({ url: `/system/roles/${roleId}/menus/`, method: 'get' })
}

export function updateRoleMenus(roleId, data) {
  return request({ url: `/system/roles/${roleId}/menus/`, method: 'put', data })
}

// ==================== 菜单管理 ====================
export function getMenuList() {
  return request({ url: '/system/menus/', method: 'get' })
}

export function getMenuTree() {
  return request({ url: '/system/menus/tree/', method: 'get' })
}

export function getMenuFlat() {
  return request({ url: '/system/menus/flat/', method: 'get' })
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

// ==================== 部门管理 ====================
export function getDeptList() {
  return request({ url: '/system/departments/', method: 'get' })
}

export function getDeptTree() {
  return request({ url: '/system/departments/tree/', method: 'get' })
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
