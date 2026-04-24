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
      {
        path: '/sales/customer-detail/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/sales/CustomerDetail.vue'),
        meta: { title: '客户详情', hidden: true },
      },
      {
        path: '/sales/picking-job/:id?',
        name: 'PickingJob',
        component: () => import('@/views/sales/PickingJob.vue'),
        meta: { title: '拣货作业', hidden: true },
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
        next({ path: to.path, query: to.query, hash: to.hash, replace: true })
      } else {
        next()
      }
    }
  } else {
    if (to.path === '/login') {
      next()
    } else {
      next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
    }
  }
})

export default router
