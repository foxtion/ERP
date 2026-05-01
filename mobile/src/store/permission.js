import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const modules = import.meta.glob('@/views/**/*.vue')

function loadComponent(path) {
  const keys = Object.keys(modules)
  for (const key of keys) {
    if (key.endsWith(path + '.vue')) return modules[key]
  }
  for (const key of keys) {
    if (key.includes(path)) return modules[key]
  }
  return null
}

export const usePermissionStore = defineStore('permission', () => {
  const dynamicRoutes = ref([])
  const sidebarMenus = ref([])
  const cachedViews = ref([])

  const tabbarMenus = computed(() => {
    // 底部 TabBar 只展示前 5 个一级菜单入口，避免过多导致重叠
    const list = sidebarMenus.value.filter(m => m.menu_type === 'MENU' && !m.is_hidden)
    return list.slice(0, 5)
  })

  const generateRoutes = (menus) => {
    const routes = []
    const sidebar = []
    const cached = []

    const visited = new Set()
    function traverse(list) {
      if (!Array.isArray(list)) return []
      for (const menu of list) {
        if (!menu || visited.has(menu.id)) continue
        visited.add(menu.id)
        if (menu.menu_type === 'BUTTON') continue

        const menuItem = {
          id: menu.id,
          name: menu.name,
          title: menu.title || menu.name,
          path: menu.path,
          icon: menu.icon,
          permission: menu.permission,
          menu_type: menu.menu_type,
          sort_order: menu.sort_order,
          is_hidden: menu.is_hidden,
          keep_alive: menu.keep_alive,
          children: [],
        }

        if (menu.children && menu.children.length > 0) {
          menuItem.children = traverse(menu.children)
        }

        sidebar.push(menuItem)

        if (menu.menu_type === 'MENU' && menu.component && !menu.is_hidden) {
          const comp = loadComponent(menu.component)
          if (comp) {
            const route = {
              path: menu.path,
              name: menu.name,
              component: comp,
              meta: {
                title: menu.title,
                icon: menu.icon,
                permission: menu.permission,
                keepAlive: menu.keep_alive,
              },
            }
            routes.push(route)
            if (menu.keep_alive) {
              cached.push(menu.name)
            }
          }
        }
      }
      return sidebar
    }

    traverse(menus)
    dynamicRoutes.value = routes
    sidebarMenus.value = sidebar
    cachedViews.value = cached
    return routes
  }

  const clearRoutes = () => {
    dynamicRoutes.value = []
    sidebarMenus.value = []
    cachedViews.value = []
  }

  return {
    dynamicRoutes,
    sidebarMenus,
    cachedViews,
    tabbarMenus,
    generateRoutes,
    clearRoutes,
  }
})
