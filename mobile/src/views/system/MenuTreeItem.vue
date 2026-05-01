<template>
  <van-collapse-item
    v-if="hasChildren"
    :name="String(item.id)"
    class="tree-item"
  >
    <template #title>
      <div class="node-title">
        <van-icon :name="item.icon || 'apps-o'" class="node-icon" />
        <span class="node-name">{{ item.title || item.name }}</span>
        <van-tag v-if="item.menu_type === 'BUTTON'" size="mini" type="primary">按钮</van-tag>
        <van-tag v-else-if="item.menu_type === 'MENU'" size="mini" type="success">菜单</van-tag>
        <van-tag v-else size="mini" type="default">目录</van-tag>
      </div>
    </template>
    <template #right-icon>
      <div class="node-actions" @click.stop>
        <van-icon
          v-if="userStore.hasPermission('system:menu:edit')"
          name="edit"
          class="action-icon"
          @click="emit('edit', item)"
        />
        <van-icon
          v-if="userStore.hasPermission('system:menu:delete')"
          name="delete-o"
          class="action-icon danger"
          @click="emit('delete', item)"
        />
      </div>
    </template>
    <div class="node-info">
      <div class="info-row">
        <span class="label">路径</span>
        <span class="value">{{ item.path || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">组件</span>
        <span class="value">{{ item.component || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">权限</span>
        <span class="value">{{ item.permission || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">排序</span>
        <span class="value">{{ item.sort_order || 0 }}</span>
      </div>
    </div>
    <MenuTreeItem
      v-for="child in item.children"
      :key="child.id"
      :item="child"
      :active-names="activeNames"
      :visited-ids="newVisitedIds"
      @edit="(v) => emit('edit', v)"
      @delete="(v) => emit('delete', v)"
    />
  </van-collapse-item>

  <div v-else class="leaf-node">
    <div class="node-header">
      <div class="node-title">
        <van-icon :name="item.icon || 'apps-o'" class="node-icon" />
        <span class="node-name">{{ item.title || item.name }}</span>
        <van-tag v-if="item.menu_type === 'BUTTON'" size="mini" type="primary">按钮</van-tag>
        <van-tag v-else-if="item.menu_type === 'MENU'" size="mini" type="success">菜单</van-tag>
        <van-tag v-else size="mini" type="default">目录</van-tag>
      </div>
      <div class="node-actions" @click.stop>
        <van-icon
          v-if="userStore.hasPermission('system:menu:edit')"
          name="edit"
          class="action-icon"
          @click="emit('edit', item)"
        />
        <van-icon
          v-if="userStore.hasPermission('system:menu:delete')"
          name="delete-o"
          class="action-icon danger"
          @click="emit('delete', item)"
        />
      </div>
    </div>
    <div class="node-info">
      <div class="info-row">
        <span class="label">路径</span>
        <span class="value">{{ item.path || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">组件</span>
        <span class="value">{{ item.component || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">权限</span>
        <span class="value">{{ item.permission || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">排序</span>
        <span class="value">{{ item.sort_order || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store/user'

const props = defineProps({
  item: { type: Object, required: true },
  activeNames: { type: Array, default: () => [] },
  visitedIds: { type: Set, default: () => new Set() },
})

const emit = defineEmits(['edit', 'delete'])
const userStore = useUserStore()

const newVisitedIds = computed(() => {
  const set = new Set(props.visitedIds)
  set.add(props.item.id)
  return set
})

const hasChildren = computed(() => {
  return props.item.children && props.item.children.length > 0 &&
    props.item.children.some(c => !props.visitedIds.has(c.id))
})
</script>

<style scoped>
.tree-item :deep(.van-collapse-item__title) {
  padding: 10px 12px;
}
.tree-item :deep(.van-collapse-item__content) {
  padding: 0 0 0 16px;
  background: transparent;
}
.leaf-node {
  padding: 10px 12px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
}
.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.node-title {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}
.node-icon {
  color: #1989fa;
  font-size: 16px;
}
.node-name {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}
.node-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-icon {
  font-size: 18px;
  color: #1989fa;
}
.action-icon.danger {
  color: #ee0a24;
}
.node-info {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.label {
  color: #969799;
}
.value {
  color: #323233;
}
</style>
