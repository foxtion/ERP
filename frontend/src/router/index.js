import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'

/**
 * 静态路由：不需要权限即可访问的页面
 */
export const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    hidden: true,
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    hidden: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes,
  scrollBehavior() {
    return { top: 0 }
  },
})

/**
 * 路由守卫：处理动态路由加载和登录校验
 */
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  const hasToken = userStore.isLoggedIn

  if (hasToken) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      // 如果已经登录且动态路由未生成，根据缓存的菜单生成路由
      if (permissionStore.dynamicRoutes.length === 0 && userStore.menus.length > 0) {
        const accessRoutes = permissionStore.generateRoutes(userStore.menus)
        accessRoutes.forEach((route) => {
          if (!router.hasRoute(route.name)) {
            router.addRoute(route)
          }
        })
        // 重新导航，确保新路由生效（使用 path 避免 name 被解析为 NotFound）
        next({ path: to.path, query: to.query, hash: to.hash, replace: true })
      } else if (permissionStore.dynamicRoutes.length === 0 && userStore.menus.length === 0) {
        // 有 Token 但没有菜单缓存，说明登录态异常，重定向到登录页
        next({ path: '/login', query: { redirect: to.fullPath } })
      } else {
        next()
      }
    }
  } else {
    if (to.path === '/login') {
      next()
    } else {
      next(`/login?redirect=${encodeURIComponent(to.path)}`)
    }
  }
})

export default router
