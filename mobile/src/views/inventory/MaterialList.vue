<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getMaterialList"
    search-placeholder="搜索物料编码/名称/规格"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('inventory:material:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.name }}</span>
          <van-tag :type="item.status === 'active' ? 'success' : 'danger'">
            {{ item.status === 'active' ? '启用' : '禁用' }}
          </van-tag>
        </div>
        <div class="card-body">
          <div><span class="label">编码：</span>{{ item.code || '-' }}</div>
          <div><span class="label">规格：</span>{{ item.specification || '-' }}</div>
          <div><span class="label">单位：</span>{{ item.unit || '-' }}</div>
          <div><span class="label">库存数量：</span><span class="stock">{{ item.stock_quantity || 0 }}</span></div>
          <div><span class="label">安全库存：</span>{{ item.safety_stock || 0 }}</div>
          <div><span class="label">分类：</span>{{ item.category_name || '-' }}</div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('inventory:material:edit')"
            size="small"
            type="primary"
            plain
            @click="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('inventory:material:delete')"
            size="small"
            type="danger"
            plain
            @click="onDelete(item)"
          >
            删除
          </van-button>
        </div>
      </div>
    </template>
  </ListPage>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog, showToast, showLoadingToast, closeToast } from 'vant'
import ListPage from '@/components/ListPage.vue'
import { useUserStore } from '@/store/user'
import { getMaterialList, deleteMaterial } from '@/api/inventory'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref()

const onAdd = () => {
  router.push('/inventory/material/add')
}

const onEdit = (item) => {
  router.push(`/inventory/material/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showDialog({
      title: '确认删除',
      message: `确定删除物料「${item.name}」吗？`,
    })
    showLoadingToast({ message: '删除中...', forbidClick: true })
    await deleteMaterial(item.id)
    closeToast()
    showToast('删除成功')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.card-item {
  margin: 10px 12px;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.card-body {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}
.label {
  color: #999;
}
.stock {
  color: #1989fa;
  font-weight: 600;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}
</style>
