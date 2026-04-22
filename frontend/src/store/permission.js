import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 使用 Vite 的 import.meta.glob 自动收集所有视图组件
 * 这样可以实现真正的按需加载（代码分割），避免所有组件被打包到一个超大 chunk 中
 */
const viewModules = import.meta.glob('@/views/**/*.vue')

// 显式导入：解决 Vite import.meta.glob 偶尔不识别新文件的问题
const explicitModules = {
  'sales/OutStockJob': () => import('@/views/sales/OutStockJob.vue'),
  'sales/OutStockList': () => import('@/views/sales/OutStockList.vue'),
}

// 启动时打印 glob 扫描结果，方便调试
const allKeys = Object.keys(viewModules)
console.log('[permission.js] import.meta.glob keys count:', allKeys.length)
const hasOutStockJob = allKeys.some(k => k.includes('OutStockJob'))
console.log('[permission.js] OutStockJob in glob?', hasOutStockJob)

/**
 * 权限路由状态管理：负责将后端返回的菜单树转换为前端动态路由
 */
export const usePermissionStore = defineStore('permission', () => {
  // ==================== State ====================
  const dynamicRoutes = ref([])
  const sidebarMenus = ref([])

  // ==================== Actions ====================
  /**
   * 根据后端菜单树生成侧边栏菜单和动态路由
   * @param {Array} menus 后端返回的菜单树
   */
  const generateRoutes = (menus) => {
    sidebarMenus.value = buildMenuTree(menus)
    dynamicRoutes.value = buildDynamicRoutes(menus)
    return dynamicRoutes.value
  }

  /**
   * 清空权限路由（登出时调用）
   */
  const clearRoutes = () => {
    dynamicRoutes.value = []
    sidebarMenus.value = []
  }

  return {
    dynamicRoutes,
    sidebarMenus,
    generateRoutes,
    clearRoutes,
  }
})

/**
 * 构建菜单树：过滤掉隐藏节点，保留用于侧边栏展示的数据
 */
function buildMenuTree(menus) {
  if (!menus || !menus.length) return []
  return menus
    .filter((menu) => !menu.is_hidden && menu.menu_type !== 'BUTTON')
    .map((menu) => {
      const item = {
        id: menu.id,
        name: menu.name,
        path: menu.path || '',
        title: menu.title,
        icon: menu.icon,
        component: menu.component,
        menu_type: menu.menu_type,
        keep_alive: menu.keep_alive,
        children: menu.children && menu.children.length ? buildMenuTree(menu.children) : undefined,
      }
      return item
    })
}

/**
 * 构建动态路由：将菜单树转换为 vue-router 路由对象数组
 */
function buildDynamicRoutes(menus) {
  const routes = []
  menus.forEach((menu) => {
    // 过滤按钮类型，防止生成无效路由
    if (menu.menu_type === 'BUTTON') return
    if (menu.menu_type === 'DIR') {
      // 目录节点：创建父路由
      const route = {
        path: menu.path || `/${menu.name}`,
        name: menu.name,
        component: () => import('@/components/layout/MainLayout.vue'),
        meta: {
          title: menu.title,
          icon: menu.icon,
          keepAlive: menu.keep_alive,
        },
        children: menu.children ? buildDynamicRoutes(menu.children) : [],
      }
      // 如果目录下有第一个子菜单，设置重定向
      if (route.children && route.children.length > 0) {
        route.redirect = route.children[0].path
      }
      routes.push(route)
    } else if (menu.menu_type === 'MENU') {
      // 菜单节点：映射到具体的页面组件
      const route = {
        path: menu.path || `/${menu.name}`,
        name: menu.name,
        component: loadComponent(menu.component),
        meta: {
          title: menu.title,
          icon: menu.icon,
          keepAlive: menu.keep_alive,
          permission: menu.permission,
        },
        children: menu.children ? buildDynamicRoutes(menu.children) : [],
      }
      routes.push(route)
    }
  })
  return routes
}

/**
 * 根据组件路径动态加载页面组件
 * 约定：component 字段格式如 "views/system/UserList.vue"
 * 使用 import.meta.glob 收集的模块表进行按需加载，实现代码分割
 */
function loadComponent(componentPath) {
  if (!componentPath) {
    return viewModules['/src/views/dashboard/index.vue']
  }
  // 统一处理路径前缀，并移除 .vue 后缀
  let path = componentPath.startsWith('views/')
    ? componentPath.replace('views/', '')
    : componentPath
  if (path.endsWith('.vue')) {
    path = path.slice(0, -4)
  }

  // 尝试多种路径格式（兼容不同系统和 Vite 版本）
  const candidateKeys = [
    `/src/views/${path}.vue`,
    `src/views/${path}.vue`,
    `./src/views/${path}.vue`,
    `../src/views/${path}.vue`,
    `../../src/views/${path}.vue`,
    `/views/${path}.vue`,
  ]

  for (const key of candidateKeys) {
    if (viewModules[key]) {
      return viewModules[key]
    }
  }

  // 模糊匹配：遍历所有 key，找包含目标路径的
  for (const [key, value] of Object.entries(viewModules)) {
    const normalizedKey = key.replace(/\\/g, '/')
    if (normalizedKey.includes(`${path}.vue`)) {
      return value
    }
  }

  // 尝试显式导入 fallback
  if (explicitModules[path]) {
    console.log(`[loadComponent] 使用显式导入: ${path}`)
    return explicitModules[path]
  }

  console.warn(`[loadComponent] 未找到组件: ${componentPath}，已回退到 dashboard`)
  console.warn('[loadComponent] 可用 keys:', Object.keys(viewModules).slice(0, 20))
  return viewModules['/src/views/dashboard/index.vue']
}
