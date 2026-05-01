<template>
  <div class="page">
    <van-nav-bar title="菜单管理" fixed placeholder left-arrow @click-left="router.back()" />
    <ListPage
      ref="listRef"
      :fetch-api="fetchApi"
      :show-search="false"
      show-add
      :has-add-permission="userStore.hasPermission('system:menu:add')"
      @add="onAdd"
    >
      <template #list="{ list }">
        <van-collapse v-if="treeData.length > 0" v-model="activeNames">
          <MenuTreeItem
            v-for="item in treeData"
            :key="item.id"
            :item="item"
            :active-names="activeNames"
            @edit="onEdit"
            @delete="onDelete"
          />
        </van-collapse>
      </template>
    </ListPage>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/store/user'
import ListPage from '@/components/ListPage.vue'
import { getMenuTree, deleteMenu } from '@/api/system'
import MenuTreeItem from './MenuTreeItem.vue'

const router = useRouter()
const userStore = useUserStore()
const listRef = ref(null)
const flatList = ref([])
const activeNames = ref([])

const fetchApi = async () => {
  const res = await getMenuTree()
  const data = res.data || []
  flatList.value = flattenTree(data)
  return {
    data: {
      list: flatList.value,
      pagination: { total: flatList.value.length },
    },
  }
}

const treeData = computed(() => {
  return buildTree(flatList.value)
})

function flattenTree(tree, result = []) {
  for (const node of tree) {
    result.push(node)
    if (node.children && node.children.length > 0) {
      flattenTree(node.children, result)
    }
  }
  return result
}

function buildTree(flat, parentId = null) {
  return flat
    .filter((item) => item.parent_id === parentId || (parentId === null && !item.parent_id))
    .map((item) => ({
      ...item,
      children: buildTree(flat, item.id),
    }))
}

const onAdd = () => {
  router.push('/system/menu/form')
}

const onEdit = (item) => {
  router.push(`/system/menu/form?id=${item.id}`)
}

const onDelete = async (item) => {
  await showConfirmDialog({
    title: '确认删除',
    message: `确定删除菜单「${item.name || item.title}」吗？`,
  })
  await deleteMenu(item.id)
  showToast('删除成功')
  listRef.value?.onRefresh()
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
