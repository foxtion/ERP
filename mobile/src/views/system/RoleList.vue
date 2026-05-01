<template>
  <div class="page">
    <van-nav-bar title="角色管理" fixed placeholder left-arrow @click-left="router.back()" />
    <ListPage
      ref="listRef"
      :fetch-api="getRoleList"
      search-placeholder="搜索角色名/编码"
      show-add
      :has-add-permission="userStore.hasPermission('system:role:add')"
      @add="onAdd"
    >
      <template #list="{ list }">
        <van-swipe-cell v-for="item in list" :key="item.id">
          <van-cell class="card-cell">
            <div class="card">
              <div class="card-header">
                <span class="name">{{ item.name }}</span>
              </div>
              <div class="card-body">
                <div class="info-row">
                  <span class="label">编码</span>
                  <span class="value">{{ item.code || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">描述</span>
                  <span class="value">{{ item.description || '-' }}</span>
                </div>
              </div>
            </div>
          </van-cell>
          <template #right>
            <van-button
              v-if="userStore.hasPermission('system:role:edit')"
              square
              type="primary"
              text="编辑"
              class="swipe-btn"
              @click="onEdit(item)"
            />
            <van-button
              v-if="userStore.hasPermission('system:role:delete')"
              square
              type="danger"
              text="删除"
              class="swipe-btn"
              @click="onDelete(item)"
            />
          </template>
        </van-swipe-cell>
      </template>
    </ListPage>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/store/user'
import ListPage from '@/components/ListPage.vue'
import { getRoleList, deleteRole } from '@/api/system'

const router = useRouter()
const userStore = useUserStore()
const listRef = ref(null)

const onAdd = () => {
  router.push('/system/role/form')
}

const onEdit = (item) => {
  router.push(`/system/role/form?id=${item.id}`)
}

const onDelete = async (item) => {
  await showConfirmDialog({
    title: '确认删除',
    message: `确定删除角色「${item.name}」吗？`,
  })
  await deleteRole(item.id)
  showToast('删除成功')
  listRef.value?.onRefresh()
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.card-cell {
  padding: 8px 12px;
  background: transparent;
}
.card-cell :deep(.van-cell__value) {
  text-align: left;
}
.card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.name {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}
.card-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.label {
  color: #969799;
}
.value {
  color: #323233;
}
.swipe-btn {
  height: 100%;
}
</style>
