import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useUserStore } from './store/user'
import { usePermissionStore } from './store/permission'
import { NavBar, Tabbar, TabbarItem, Toast, Dialog } from 'vant'
import './style.css'
import 'vant/lib/index.css'

const app = createApp(App)
app.use(createPinia())
app.use(NavBar)
app.use(Tabbar)
app.use(TabbarItem)
app.use(Toast)
app.use(Dialog)

// 恢复登录态
const userStore = useUserStore()
const permissionStore = usePermissionStore()
userStore.restoreSession()

async function initApp() {
  if (userStore.isLoggedIn) {
    try {
      // 刷新用户信息，确保 menus 是最新的
      await userStore.fetchUserInfo()
    } catch (e) {
      console.error('initApp error:', e)
      if (e?.response?.status === 401) {
        // token 过期，清理登录态
        userStore.logout()
        permissionStore.clearRoutes()
      }
    }
  }
  app.use(router)
  app.mount('#app')
}

initApp()
