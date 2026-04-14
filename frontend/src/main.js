import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'

import App from './App.vue'
import router from './router'
import { permissionDirective } from './utils/directives'
import { useUserStore } from './store/user'

const app = createApp(App)

// 注册全局权限指令
app.directive('permission', permissionDirective)

app.use(createPinia())

// 应用启动时恢复用户登录状态（从 localStorage 读取 Token）
const userStore = useUserStore()
userStore.restoreSession()

app.use(router)
app.use(ElementPlus)

app.mount('#app')
