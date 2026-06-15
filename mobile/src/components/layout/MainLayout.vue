<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      :title="pageTitle"
      :left-arrow="showBack"
      @click-left="onClickLeft"
      fixed
      placeholder
    />

    <!-- 主内容区 -->
    <div class="main-content">
      <router-view v-slot="{ Component }">
        <keep-alive :include="cachedViews">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>

    <!-- 底部 TabBar -->
    <van-tabbar v-model="activeTab" route placeholder>
      <van-tabbar-item
        v-for="menu in tabbarMenus"
        :key="menu.path"
        :to="menu.path"
        :icon="mapIcon(menu.icon, menu.path)"
      >
        {{ menu.title }}
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePermissionStore } from '@/store/permission'
import { mapIcon } from '@/utils/icon-map'

const route = useRoute()
const router = useRouter()
const permissionStore = usePermissionStore()

const activeTab = ref(0)
const cachedViews = computed(() => permissionStore.cachedViews)

const tabbarMenus = computed(() => {
  const menus = permissionStore.tabbarMenus
  // 如果没有动态菜单，返回默认首页
  if (!menus || menus.length === 0) {
    return [{ path: '/dashboard', title: '首页', icon: 'home-o' }]
  }
  return menus
})

const pageTitle = computed(() => {
  return route.meta?.title || 'ERP移动版'
})

const showBack = computed(() => {
  // 首页和Tab页面不显示返回箭头
  const noBackPaths = ['/dashboard', '/login']
  const tabPaths = tabbarMenus.value.map(m => m.path)
  return !noBackPaths.includes(route.path) && !tabPaths.includes(route.path)
})

const onClickLeft = () => {
  router.back()
}

// 同步当前激活的tab
watch(
  () => route.path,
  (path) => {
    const idx = tabbarMenus.value.findIndex(m => m.path === path)
    if (idx !== -1) {
      activeTab.value = idx
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.main-content {
  padding-bottom: 50px;
}
</style>
