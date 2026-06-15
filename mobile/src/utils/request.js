import axios from 'axios'
import { showToast, showFailToast } from 'vant'
import { useUserStore } from '@/store/user'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ==================== Token 自动刷新机制 ====================
let isRefreshing = false
let refreshSubscribers = []
let isLoggingOut = false

function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken))
  refreshSubscribers = []
}

function handleLogout() {
  if (isLoggingOut) return
  isLoggingOut = true
  const userStore = useUserStore()
  userStore.token = ''
  userStore.userInfo = null
  userStore.menus = []
  userStore.permissions = []
  localStorage.removeItem('erp_token')
  localStorage.removeItem('erp_refresh_token')
  localStorage.removeItem('erp_menus')
  localStorage.removeItem('erp_permissions')
  localStorage.removeItem('erp_user_info')
  router.push('/login')
  setTimeout(() => { isLoggingOut = false }, 3000)
}

async function doRefreshToken(refresh) {
  const res = await axios.post('/api/system/auth/refresh/', { refresh })
  return res.data
}

// ==================== 请求拦截器 ====================
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ==================== 响应拦截器 ====================
request.interceptors.response.use(
  (response) => {
    if (response.config.responseType === 'blob' || response.config.responseType === 'arraybuffer') {
      return response
    }
    const res = response.data
    if (typeof res.code === 'number' && !(res.code >= 200 && res.code < 300)) {
      showFailToast(res.message || '请求失败')
      const err = new Error(res.message || '请求失败')
      err.response = response
      return Promise.reject(err)
    }
    return res
  },
  async (error) => {
    const { response, config: originalRequest } = error
    if (response) {
      const status = response.status
      let message = response.data?.message
      if (!message && typeof response.data === 'object' && response.data !== null) {
        // 优先提取 detail 字段（DRF 默认错误格式）
        if (response.data.detail) {
          message = typeof response.data.detail === 'string' ? response.data.detail : JSON.stringify(response.data.detail)
        } else {
          const fieldErrors = Object.entries(response.data)
            .filter(([key]) => !['code', 'data'].includes(key))
            .map(([, val]) => val)
          const firstError = fieldErrors.flat()[0]
          if (firstError) {
            message = typeof firstError === 'string' ? firstError : firstError.detail || JSON.stringify(firstError)
          }
        }
      }
      if (!message) message = '服务器异常'

      // 401 处理：尝试刷新 Token
      if (status === 401 && originalRequest && !originalRequest._retry) {
        const url = originalRequest.url || ''
        const fullUrl = (originalRequest.baseURL || '') + url
        if (url.includes('/auth/logout/') || url.includes('/auth/refresh/') ||
            fullUrl.includes('/auth/logout/') || fullUrl.includes('/auth/refresh/')) {
          return Promise.reject(error)
        }
        const refreshToken = localStorage.getItem('erp_refresh_token')
        if (!refreshToken) {
          showFailToast('登录已过期，请重新登录')
          handleLogout()
          return Promise.reject(error)
        }
        if (!isRefreshing) {
          isRefreshing = true
          originalRequest._retry = true
          try {
            const res = await doRefreshToken(refreshToken)
            const newAccessToken = res.data?.access || res.access
            localStorage.setItem('erp_token', newAccessToken)
            const userStore = useUserStore()
            userStore.token = newAccessToken
            isRefreshing = false
            onTokenRefreshed(newAccessToken)
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
            return request(originalRequest)
          } catch (refreshError) {
            isRefreshing = false
            refreshSubscribers = []
            showFailToast('登录已过期，请重新登录')
            handleLogout()
            return Promise.reject(refreshError)
          }
        } else {
          return new Promise((resolve) => {
            subscribeTokenRefresh((newToken) => {
              originalRequest._retry = true
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              resolve(request(originalRequest))
            })
          })
        }
      }

      if (status === 403) {
        showFailToast('权限不足，无法访问')
      } else if (status !== 401) {
        showFailToast(message || '操作失败')
      }
      // 控制台输出完整错误，方便调试
      console.error(`[Request Error ${status}]`, originalRequest?.url, response.data)
    } else {
      showFailToast('网络请求失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default request
