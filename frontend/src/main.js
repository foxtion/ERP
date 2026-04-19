import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'

import App from './App.vue'
import router from './router'
import { permissionDirective } from './utils/directives'
import { useUserStore } from './store/user'
import { usePermissionStore } from './store/permission'

const app = createApp(App)

// 注册全局权限指令
app.directive('permission', permissionDirective)

app.use(createPinia())

// 应用启动时恢复用户登录状态（从 localStorage 读取 Token）
const userStore = useUserStore()
const permissionStore = usePermissionStore()
userStore.restoreSession()

// 如果已登录，自动刷新用户信息和菜单权限（解决新增菜单后刷新页面404的问题）
async function initApp() {
  if (userStore.isLoggedIn) {
    try {
      await userStore.fetchUserInfo()
      // fetchUserInfo 完成后，用最新菜单重新生成路由和侧边栏
      if (userStore.menus.length > 0) {
        const accessRoutes = permissionStore.generateRoutes(userStore.menus)
        accessRoutes.forEach((route) => {
          if (!router.hasRoute(route.name)) {
            router.addRoute(route)
          }
        })
      }
    } catch (e) {
      console.error('fetchUserInfo failed:', e)
      // 401 时响应拦截器已清理状态并准备跳转登录页，这里不再继续挂载主应用
      // 避免页面闪烁或已登出状态仍显示登录后的布局
      if (e.response?.status === 401) {
        app.use(router)
        app.use(ElementPlus)
        app.mount('#app')
        return
      }
    }
  }
  app.use(router)
  app.use(ElementPlus)
  app.mount('#app')
}

initApp()
