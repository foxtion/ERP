<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getLocationList"
    search-placeholder="搜索库位名称/编码"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('inventory:location:add')"
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
          <div><span class="label">所属仓库：</span>{{ item.warehouse_name || '-' }}</div>
          <div><span class="label">容量：</span>{{ item.capacity || '-' }}</div>
          <div><span class="label">备注：</span>{{ item.remark || '-' }}</div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('inventory:location:edit')"
            size="small"
            type="primary"
            plain
            @click="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('inventory:location:delete')"
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
import { getLocationList, deleteLocation } from '@/api/inventory'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref()

const onAdd = () => {
  router.push('/inventory/location/add')
}

const onEdit = (item) => {
  router.push(`/inventory/location/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showDialog({
      title: '确认删除',
      message: `确定删除库位「${item.name}」吗？`,
    })
    showLoadingToast({ message: '删除中...', forbidClick: true })
    await deleteLocation(item.id)
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
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}
</style>
