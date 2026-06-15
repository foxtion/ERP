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

    <!-- 退出确认弹窗 -->
    <van-dialog
      v-model:show="showLogoutDialog"
      title="确认退出"
      show-cancel-button
      @confirm="onConfirmLogout"
    >
      <div style="padding: 20px 24px; text-align: center; color: #323233;">
        确定要退出登录吗？
      </div>
    </van-dialog>



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
import { showDialog, showToast } from 'vant'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'
import { changePassword } from '@/api/auth'
import { mapIcon } from '@/utils/icon-map'

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

const showLogoutDialog = ref(false)

const handleLogout = () => {
  showLogoutDialog.value = true
}

const onConfirmLogout = async () => {
  showLogoutDialog.value = false
  await userStore.logout()
  permissionStore.clearRoutes()
  showToast({ message: '已退出登录', className: 'van-toast--white' })
  setTimeout(() => {
    router.push('/login')
  }, 1500)
}

const showChangePassword = ref(false)
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })

const showAbout = () => {
  showToast('ERP Mobile v1.0')
}

const onChangePassword = async () => {
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    showDialog({ title: '提示', message: '请填写完整密码信息' })
    return
  }
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
    showDialog({ title: '提示', message: '两次输入的新密码不一致' })
    return
  }
  try {
    await changePassword(pwdForm.value)
    showDialog({ title: '成功', message: '密码修改成功，请重新登录' }).then(async () => {
      await userStore.logout()
      router.push('/login')
    })
  } catch (e) {
    showDialog({ title: '提示', message: e?.response?.data?.message || '修改失败' })
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
