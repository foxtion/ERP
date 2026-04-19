import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import router from '@/router'

/**
 * Axios 实例配置
 * baseURL 结合 vite.config.js 的 proxy 配置，开发时自动转发到后端
 */
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

function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach((callback) => callback(newToken))
  refreshSubscribers = []
}

function handleLogout() {
  const userStore = useUserStore()
  userStore.logout()
  router.push('/login')
}

/**
 * 使用原生 axios 发送刷新请求（避免走 request 拦截器造成死循环）
 */
async function doRefreshToken(refresh) {
  const res = await axios.post('/api/system/auth/refresh/', { refresh })
  return res.data
}

// ==================== 请求拦截器：自动注入 JWT Access Token ====================
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
  (error) => {
    return Promise.reject(error)
  }
)

// ==================== 响应拦截器：统一错误处理、Token 无感刷新 ====================
request.interceptors.response.use(
  (response) => {
    // blob / arraybuffer 响应直接返回原始 response，不做 JSON 格式校验
    if (response.config.responseType === 'blob' || response.config.responseType === 'arraybuffer') {
      return response
    }
    const res = response.data
    // 后端统一格式：{ code, message, data }
    // 兼容 DRF 默认格式（没有 code 字段时直接返回）
    if (res.code !== undefined && !(res.code >= 200 && res.code < 300)) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  async (error) => {
    const { response, config: originalRequest } = error

    if (response) {
      const status = response.status
      let message = response.data?.message

      // DRF 序列化器错误格式：{ field: [errors] }
      if (!message && typeof response.data === 'object') {
        const firstError = Object.values(response.data).flat()[0]
        if (firstError) {
          message = typeof firstError === 'string' ? firstError : firstError.detail || JSON.stringify(firstError)
        }
      }
      if (!message) message = '服务器异常'

      // 401 处理：尝试用 refresh_token 无感刷新，失败才跳转登录
      if (status === 401 && originalRequest && !originalRequest._retry) {
        const refreshToken = localStorage.getItem('erp_refresh_token')
        if (!refreshToken) {
          ElMessage.error('登录已过期，请重新登录')
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
            // 重试原请求
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
            return request(originalRequest)
          } catch (refreshError) {
            isRefreshing = false
            refreshSubscribers = []
            ElMessage.error('登录已过期，请重新登录')
            handleLogout()
            return Promise.reject(refreshError)
          }
        } else {
          // 正在刷新中，将请求加入队列等待新 token
          return new Promise((resolve) => {
            subscribeTokenRefresh((newToken) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              resolve(request(originalRequest))
            })
          })
        }
      }

      if (status === 403) {
        ElMessage.error('权限不足，无法访问')
      } else if (status !== 401) {
        ElMessage.error(message)
      }
    } else {
      ElMessage.error('网络请求失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default request
