<template>
  <div class="dashboard-page">
    <!-- 用户信息卡片 -->
    <div class="user-card">
      <div class="user-info">
        <van-image round width="50" height="50" :src="userAvatar" />
        <div class="user-meta">
          <div class="username">{{ userStore.userInfo?.username || '未登录' }}</div>
          <div class="dept">{{ userStore.userInfo?.dept_name || '' }}</div>
        </div>
      </div>
      <van-button size="small" type="danger" plain @click="handleLogout">退出</van-button>
    </div>

    <!-- 功能菜单网格 -->
    <div class="menu-grid">
      <div class="grid-wrap">
        <div
          v-for="menu in menuList"
          :key="menu.id"
          class="grid-cell"
          @click="navigateTo(menu.path)"
        >
          <van-icon :name="mapIcon(menu.icon, menu.path)" class="grid-icon" />
          <span class="grid-text">{{ menu.title }}</span>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <div class="section-title">快捷操作</div>
      <van-cell-group inset>
        <van-cell title="修改密码" is-link @click="showChangePassword = true" />
        <van-cell title="关于系统" is-link @click="showAbout" />
      </van-cell-group>
    </div>

    <!-- 修改密码弹窗 -->
    <van-dialog
      v-model:show="showChangePassword"
      title="修改密码"
      show-cancel-button
      @confirm="onChangePassword"
    >
      <van-form>
        <van-field
          v-model="pwdForm.old_password"
          type="password"
          label="旧密码"
          placeholder="请输入旧密码"
        />
        <van-field
          v-model="pwdForm.new_password"
          type="password"
          label="新密码"
          placeholder="请输入新密码"
        />
        <van-field
          v-model="pwdForm.confirm_password"
          type="password"
          label="确认密码"
          placeholder="请再次输入新密码"
        />
      </van-form>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog, showFailToast } from 'vant'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'
import { changePassword } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

const userAvatar = computed(() => {
  return userStore.userInfo?.avatar || 'https://img.yzcdn.cn/vant/cat.jpeg'
})

// 从侧边栏菜单过滤出可点击的菜单项
const menuList = computed(() => {
  const result = []
  const visited = new Set()
  function traverse(list) {
    if (!Array.isArray(list)) return
    for (const item of list) {
      if (!item || visited.has(item.id)) continue
      visited.add(item.id)
      if (item.menu_type === 'MENU' && !item.is_hidden) {
        result.push(item)
      }
      if (item.children && item.children.length > 0) {
        traverse(item.children)
      }
    }
  }
  traverse(permissionStore.sidebarMenus)
  return result
})

const navigateTo = (path) => {
  router.push(path)
}

// 把菜单路径或 Element Plus 图标名映射到 Vant 图标名
const mapIcon = (icon, path) => {
  // 标准化路径：统一加上 / 前缀，去除尾部斜杠
  const normalized = (p) => {
    if (!p) return ''
    let s = p.trim()
    if (!s.startsWith('/')) s = '/' + s
    if (s.endsWith('/')) s = s.slice(0, -1)
    return s
  }

  // 优先按路径精确映射，确保每个菜单都有独特图标
  const pathMap = {
    '/system/user': 'manager-o',
    '/system/role': 'friends-o',
    '/system/menu': 'apps-o',
    '/system/dept': 'cluster-o',
    '/purchase/supplier': 'shop-o',
    '/purchase/order': 'cart-o',
    '/sales/customer': 'contact-o',
    '/sales/order': 'orders-o',
    '/inventory/warehouse': 'home-o',
    '/inventory/stock': 'search',
    '/inventory/stocks': 'search',
    '/sales/picking-list': 'todo-list-o',
    '/sales/picking_list': 'todo-list-o',
    '/inventory/material': 'label-o',
    '/inventory/location': 'location-o',
    '/inventory/warning': 'warning-o',
    '/production/bom': 'records-o',
    '/production/workorder': 'description-o',
    '/production/plan': 'calendar-o',
    '/production/requisition': 'medal-o',
    '/production/instock': 'arrow-down',
    '/production/instocks': 'arrow-down',
    '/finance/receivable': 'balance-o',
    '/finance/voucher': 'edit',
    '/finance/vouchers': 'edit',
    '/finance/payment': 'balance-o',
    '/finance/payments': 'balance-o',
    '/finance/statement': 'chart-trending-o',
    '/hr/employee': 'idcard',
    '/hr/employees': 'idcard',
    '/hr/attendance': 'clock-o',
    '/sales/outstock': 'logistics',
    '/sales/outstocks': 'logistics',
    '/inventory/outstock': 'logistics',
    '/inventory/outstocks': 'logistics',
    '/sales/return': 'refund-o',
    '/inventory/transfer': 'logistics',
    '/inventory/transfers': 'logistics',
    '/inventory/check': 'search-o',
    '/purchase/request': 'records-o',
    '/purchase/instock': 'down-o',
    '/production/order': 'description-o',
  }
  const np = normalized(path)
  if (np && pathMap[np]) return pathMap[np]

  // 按路径最后一段模糊匹配
  const lastSegment = np.split('/').pop()
  const segmentMap = {
    'user': 'manager-o',
    'role': 'friends-o',
    'menu': 'apps-o',
    'dept': 'cluster-o',
    'supplier': 'shop-o',
    'order': 'orders-o',
    'customer': 'contact-o',
    'warehouse': 'home-o',
    'stock': 'search',
    'stocks': 'search',
    'picking-list': 'todo-list-o',
    'picking_list': 'todo-list-o',
    'material': 'label-o',
    'location': 'location-o',
    'warning': 'warning-o',
    'bom': 'records-o',
    'workorder': 'description-o',
    'plan': 'calendar-o',
    'requisition': 'medal-o',
    'instock': 'arrow-down',
    'instocks': 'arrow-down',
    'receivable': 'balance-o',
    'voucher': 'edit',
    'vouchers': 'edit',
    'payment': 'balance-o',
    'payments': 'balance-o',
    'statement': 'chart-trending-o',
    'employee': 'idcard',
    'employees': 'idcard',
    'attendance': 'clock-o',
    'outstock': 'logistics',
    'outstocks': 'logistics',
    'outstock-job': 'logistics',
    'return': 'refund-o',
    'transfer': 'logistics',
    'transfers': 'logistics',
    'check': 'search-o',
    'request': 'records-o',
  }
  if (lastSegment && segmentMap[lastSegment]) return segmentMap[lastSegment]

  if (lastSegment && !segmentMap[lastSegment]) {
    console.log('[Dashboard] unknown path segment:', lastSegment, 'full path:', path, 'icon:', icon)
  }

  // 兜底：按 Element Plus 图标名映射
  const map = {
    'HomeFilled': 'home-o',
    'UserFilled': 'manager-o',
    'User': 'manager-o',
    'OfficeBuilding': 'cluster-o',
    'List': 'apps-o',
    'Menu': 'apps-o',
    'Grid': 'apps-o',
    'Setting': 'setting-o',
    'Tools': 'setting-o',
    'ShoppingCart': 'cart-o',
    'ShoppingBag': 'bag-o',
    'Goods': 'goods-collect-o',
    'Box': 'logistics-o',
    'Warehouse': 'home-o',
    'Money': 'balance-o',
    'Coin': 'balance-o',
    'Document': 'description-o',
    'DocumentChecked': 'records-o',
    'DocumentCopy': 'orders-o',
    'Tickets': 'coupon-o',
    'Calendar': 'calendar-o',
    'Clock': 'clock-o',
    'TrendCharts': 'chart-trending-o',
    'Histogram': 'bar-chart-o',
    'PieChart': 'chart-trending-o',
    'CircleCheck': 'checked-o',
    'CircleClose': 'close-o',
    'Warning': 'warning-o',
    'InfoFilled': 'info-o',
    'QuestionFilled': 'question-o',
    'Avatar': 'user-circle-o',
    'Stamp': 'passed-o',
    'Sell': 'cart-o',
    'Shop': 'shop-o',
    'Truck': 'logistics-o',
    'FirstAidKit': 'medal-o',
    'Suitcase': 'friends-o',
    'Discount': 'discount-o',
    'PriceTag': 'label-o',
    'Message': 'comment-o',
    'Bell': 'bell-o',
    'Phone': 'phone-o',
    'Location': 'location-o',
    'MapLocation': 'location-o',
    'Van': 'logistics-o',
    'Notebook': 'notes-o',
    'DataAnalysis': 'chart-trending-o',
    'Management': 'manager-o',
    'Promotion': 'point-gift-o',
    'Present': 'gift-o',
    'GobletFull': 'gem-o',
    'Goblet': 'gem-o',
    'Food': 'smile-o',
    'Dish': 'smile-o',
    'DishDot': 'smile-o',
    'Chicken': 'smile-o',
    'ForkSpoon': 'smile-o',
    'KnifeFork': 'smile-o',
    'Burger': 'smile-o',
    'IceCream': 'smile-o',
    'IceDrink': 'smile-o',
    'Coffee': 'smile-o',
    'Mug': 'smile-o',
    'ColdDrink': 'smile-o',
    'Grape': 'smile-o',
    'Watermelon': 'smile-o',
    'Cherry': 'smile-o',
    'Apple': 'smile-o',
    'Pear': 'smile-o',
    'Orange': 'smile-o',
    'IceTea': 'smile-o',
    'MilkTea': 'smile-o',
    'Lemon': 'smile-o',
    'Sugar': 'smile-o',
    'Bowl': 'smile-o',
    'IceCreamRound': 'smile-o',
    'IceCreamSquare': 'smile-o',
  }
  return map[icon] || 'apps-o'
}

const handleLogout = () => {
  showConfirmDialog({
    title: '确认退出',
    message: '确定要退出登录吗？',
  }).then(async () => {
    await userStore.logout()
    permissionStore.clearRoutes()
    router.push('/login')
    showToast('已退出登录')
  }).catch(() => {})
}

const showChangePassword = ref(false)
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })

const showAbout = () => {
  showToast('ERP Mobile v1.0')
}

const onChangePassword = async () => {
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    showFailToast('请填写完整密码信息')
    return
  }
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
    showFailToast('两次输入的新密码不一致')
    return
  }
  try {
    await changePassword(pwdForm.value)
    showToast('密码修改成功，请重新登录')
    await userStore.logout()
    router.push('/login')
  } catch (e) {
    showFailToast(e?.response?.data?.message || '修改失败')
  }
}
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 20px;
}
.user-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  font-size: 16px;
  font-weight: bold;
}
.dept {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 4px;
}
.menu-grid {
  margin: 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.grid-wrap {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.grid-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 4px;
  background-color: #fff;
  border-radius: 6px;
}
.quick-actions {
  margin-top: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #969799;
  padding: 0 16px 8px;
}
.grid-item-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.grid-icon {
  font-size: 24px;
  color: #1989fa;
}
.grid-text {
  font-size: 12px;
  color: #323233;
}
</style>
