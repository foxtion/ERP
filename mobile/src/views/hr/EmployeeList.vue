<template>
  <div class="page">
    <van-nav-bar title="员工档案" fixed placeholder left-arrow @click-left="router.back()" />
    <ListPage
      ref="listRef"
      :fetch-api="getEmployeeList"
      search-placeholder="搜索姓名/工号"
      show-add
      :has-add-permission="userStore.hasPermission('hr:employee:add')"
      @add="onAdd"
    >
      <template #list="{ list }">
        <van-swipe-cell v-for="item in list" :key="item.id">
          <van-cell class="card-cell">
            <div class="card">
              <div class="card-header">
                <span class="name">{{ item.name }}</span>
                <van-tag :type="statusType(item.status)">{{ statusText(item.status) }}</van-tag>
              </div>
              <div class="card-body">
                <div class="info-row">
                  <span class="label">工号</span>
                  <span class="value">{{ item.employee_no }}</span>
                </div>
                <div class="info-row">
                  <span class="label">部门</span>
                  <span class="value">{{ item.department_name || item.department || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">职位</span>
                  <span class="value">{{ item.position_name || item.position || '-' }}</span>
                </div>
              </div>
            </div>
          </van-cell>
          <template #right>
            <van-button
              v-if="userStore.hasPermission('hr:employee:edit')"
              square
              type="primary"
              text="编辑"
              class="swipe-btn"
              @click="onEdit(item)"
            />
            <van-button
              v-if="userStore.hasPermission('hr:employee:delete')"
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
import { getEmployeeList, deleteEmployee } from '@/api/hr'

const router = useRouter()
const userStore = useUserStore()
const listRef = ref(null)

const statusMap = {
  active: { text: '在职', type: 'success' },
  inactive: { text: '离职', type: 'default' },
  probation: { text: '试用', type: 'warning' },
}

const statusType = (status) => statusMap[status]?.type || 'default'
const statusText = (status) => statusMap[status]?.text || status

const onAdd = () => {
  router.push('/hr/employee/form')
}

const onEdit = (item) => {
  router.push(`/hr/employee/form?id=${item.id}`)
}

const onDelete = async (item) => {
  await showConfirmDialog({
    title: '确认删除',
    message: `确定删除员工「${item.name}」吗？`,
  })
  await deleteEmployee(item.id)
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
