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

/**
 * 请求拦截器：自动注入 JWT Access Token
 */
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

/**
 * 响应拦截器：统一错误处理、Token过期跳转登录
 */
request.interceptors.response.use(
  (response) => {
    // blob / arraybuffer 响应直接返回原始 response，不做 JSON 格式校验
    if (response.config.responseType === 'blob' || response.config.responseType === 'arraybuffer') {
      return response
    }
    const res = response.data
    // 后端统一格式：{ code, message, data }
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    const { response } = error
    if (response) {
      const status = response.status
      const message = response.data?.message || '服务器异常'

      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        const userStore = useUserStore()
        userStore.logout()
        router.push('/login')
      } else if (status === 403) {
        ElMessage.error('权限不足，无法访问')
      } else {
        ElMessage.error(message)
      }
    } else {
      ElMessage.error('网络请求失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default request
