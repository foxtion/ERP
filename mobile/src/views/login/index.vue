<template>
  <div class="login-page">
    <div class="login-header">
      <h1 class="title">ERP 移动版</h1>
      <p class="subtitle">企业资源计划管理系统</p>
    </div>

    <van-form @submit="onSubmit" class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          name="username"
          label="账号"
          placeholder="请输入账号"
          :rules="[{ required: true, message: '请输入账号' }]"
          left-icon="user-o"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
          left-icon="lock"
        />
      </van-cell-group>

      <div class="remember-row">
        <van-checkbox v-model="rememberMe" shape="square">记住我</van-checkbox>
      </div>

      <div class="submit-btn">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
      </div>
    </van-form>


  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const rememberMe = ref(false)

onMounted(() => {
  // 清理可能残留的 Vant 函数式弹窗节点（teleport 到 body 上，页面切换时可能未销毁）
  const vantClasses = ['.van-dialog', '.van-toast', '.van-overlay', '.van-popup']
  vantClasses.forEach((cls) => {
    document.querySelectorAll(cls).forEach((el) => el.remove())
  })
  // 同时清理函数式调用留下的空容器 div
  document.body.querySelectorAll(':scope > div').forEach((el) => {
    if (el.childElementCount === 0 && !el.id) {
      el.remove()
    }
  })

  const saved = localStorage.getItem('erp_remember_username')
  if (saved) {
    form.value.username = saved
    rememberMe.value = true
  }
})

const onSubmit = async () => {
  loading.value = true
  try {
    const res = await userStore.login(form.value)
    if (rememberMe.value) {
      localStorage.setItem('erp_remember_username', form.value.username)
    } else {
      localStorage.removeItem('erp_remember_username')
    }

    // 生成动态路由并注册到 router
    if (userStore.menus.length > 0) {
      const routes = permissionStore.generateRoutes(userStore.menus)
      routes.forEach((route) => {
        if (!router.hasRoute(route.name)) {
          router.addRoute('Layout', route)
        }
      })
    }

    showToast({ message: '登录成功', className: 'van-toast--white' })
    setTimeout(() => {
      const redirect = route.query.redirect || '/dashboard'
      router.replace(redirect)
    }, 1500)
  } catch (e) {
    showFailToast(e?.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}


</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 80px;
}
.login-header {
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}
.title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}
.subtitle {
  font-size: 14px;
  opacity: 0.9;
}
.login-form {
  width: 100%;
}
.remember-row {
  padding: 12px 32px;
  display: flex;
  align-items: center;
}
.submit-btn {
  padding: 20px 32px;
}
</style>
