import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo, logout as logoutApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('erp_token') || '')
  const userInfo = ref(null)
  const menus = ref([])
  const permissions = ref([])

  const isLoggedIn = computed(() => !!token.value)

  const login = async (credentials) => {
    const res = await loginApi(credentials)
    token.value = res.data.access
    localStorage.setItem('erp_token', res.data.access)
    localStorage.setItem('erp_refresh_token', res.data.refresh)
    menus.value = res.data.menus || []
    permissions.value = res.data.permissions || []
    userInfo.value = res.data.user
    localStorage.setItem('erp_menus', JSON.stringify(menus.value))
    localStorage.setItem('erp_permissions', JSON.stringify(permissions.value))
    localStorage.setItem('erp_user_info', JSON.stringify(res.data.user))
    return res
  }

  const fetchUserInfo = async () => {
    const res = await getUserInfo()
    userInfo.value = res.data
    if (res.data.menus) {
      menus.value = res.data.menus
      localStorage.setItem('erp_menus', JSON.stringify(res.data.menus))
    }
    if (res.data.permissions) {
      permissions.value = res.data.permissions
      localStorage.setItem('erp_permissions', JSON.stringify(res.data.permissions))
    }
    return res
  }

  const restoreSession = () => {
    const storedToken = localStorage.getItem('erp_token')
    const storedMenus = localStorage.getItem('erp_menus')
    const storedPerms = localStorage.getItem('erp_permissions')
    const storedUserInfo = localStorage.getItem('erp_user_info')
    if (storedToken) {
      token.value = storedToken
      menus.value = storedMenus ? JSON.parse(storedMenus) : []
      permissions.value = storedPerms ? JSON.parse(storedPerms) : []
      userInfo.value = storedUserInfo ? JSON.parse(storedUserInfo) : null
    }
  }

  const logout = async () => {
    try {
      await logoutApi()
    } catch (e) {
      // 忽略后端登出错误
    }
    token.value = ''
    userInfo.value = null
    menus.value = []
    permissions.value = []
    localStorage.removeItem('erp_token')
    localStorage.removeItem('erp_refresh_token')
    localStorage.removeItem('erp_menus')
    localStorage.removeItem('erp_permissions')
    localStorage.removeItem('erp_user_info')
  }

  const hasPermission = (perm) => {
    if (!perm) return true
    if (userInfo.value?.is_superuser) return true
    if (permissions.value.includes(perm)) return true
    // 部门兜底权限：仅对特定的作业/执行类权限生效，且用户必须有部门
    // TODO: 如需严格按部门隔离，应校验用户部门与资源所属部门是否匹配
    const dept = userInfo.value?.dept_name || userInfo.value?.department
    if (dept && perm && (perm.endsWith(':job') || perm.endsWith(':operate') || perm.endsWith(':execute'))) {
      return true
    }
    return false
  }

  return {
    token,
    userInfo,
    menus,
    permissions,
    isLoggedIn,
    login,
    fetchUserInfo,
    restoreSession,
    logout,
    hasPermission,
  }
})
