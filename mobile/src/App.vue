<template>
  <router-view v-slot="{ Component }">
    <keep-alive :include="cachedViews">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>

<script setup>
import { computed } from 'vue'
import { usePermissionStore } from '@/store/permission'

const permissionStore = usePermissionStore()
const cachedViews = computed(() => permissionStore.cachedViews)
</script>
