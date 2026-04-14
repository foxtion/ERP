<template>
  <!-- 有子菜单：渲染 el-sub-menu -->
  <el-sub-menu v-if="hasChildren" :index="menu.path">
    <template #title>
      <el-icon v-if="menu.icon"><IconRender :icon="menu.icon" /></el-icon>
      <span>{{ menu.title }}</span>
    </template>
    <SidebarMenuItem
      v-for="child in menu.children"
      :key="child.id"
      :menu="child"
    />
  </el-sub-menu>

  <!-- 无子菜单：渲染 el-menu-item -->
  <el-menu-item v-else :index="menu.path">
    <el-icon v-if="menu.icon"><IconRender :icon="menu.icon" /></el-icon>
    <template #title>
      <span>{{ menu.title }}</span>
    </template>
  </el-menu-item>
</template>

<script setup>
import { computed } from 'vue'
import IconRender from '@/components/IconRender.vue'

const props = defineProps({
  menu: {
    type: Object,
    required: true,
  },
})

const hasChildren = computed(() => {
  return props.menu.children && props.menu.children.length > 0
})
</script>
