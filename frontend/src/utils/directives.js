import { useUserStore } from '@/store/user'

/**
 * 检查并处理权限
 * @param {HTMLElement} el
 * @param {string} requiredPermission
 */
function checkPermission(el, requiredPermission) {
  const userStore = useUserStore()
  if (!userStore.hasPermission(requiredPermission)) {
    if (el.parentNode) {
      el.parentNode.removeChild(el)
    }
  }
}

/**
 * 自定义权限指令 v-permission
 * 用法：v-permission="'system:user:add'"
 * 当用户没有该权限时，会自动移除该 DOM 元素
 */
export const permissionDirective = {
  mounted(el, binding) {
    checkPermission(el, binding.value)
  },
  updated(el, binding) {
    checkPermission(el, binding.value)
  },
}
