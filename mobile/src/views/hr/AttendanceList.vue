<template>
  <div class="page">
    <ListPage
      ref="listRef"
      :fetch-api="getAttendanceList"
      search-placeholder="搜索员工姓名"
      show-add
      :has-add-permission="userStore.hasPermission('hr:attendance:add')"
      @add="onAdd"
    >
      <template #list="{ list }">
        <van-swipe-cell v-for="item in list" :key="item.id">
          <van-cell class="card-cell">
            <div class="card">
              <div class="card-header">
                <span class="date">{{ item.date }}</span>
                <van-tag :type="statusType(item.status)">{{ statusText(item.status) }}</van-tag>
              </div>
              <div class="card-body">
                <div class="info-row">
                  <span class="label">员工</span>
                  <span class="value">{{ item.employee_name || item.employee || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">签到</span>
                  <span class="value">{{ item.check_in || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">签退</span>
                  <span class="value">{{ item.check_out || '-' }}</span>
                </div>
              </div>
            </div>
          </van-cell>
          <template #right>
            <van-button
              v-if="userStore.hasPermission('hr:attendance:edit')"
              square
              type="primary"
              text="编辑"
              class="swipe-btn"
              @click="onEdit(item)"
            />
            <van-button
              v-if="userStore.hasPermission('hr:attendance:delete')"
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
import { getAttendanceList, deleteAttendance } from '@/api/hr'

const router = useRouter()
const userStore = useUserStore()
const listRef = ref(null)

const statusMap = {
  normal: { text: '正常', type: 'success' },
  late: { text: '迟到', type: 'warning' },
  early: { text: '早退', type: 'warning' },
  absent: { text: '缺勤', type: 'danger' },
  leave: { text: '请假', type: 'primary' },
}

const statusType = (status) => statusMap[status]?.type || 'default'
const statusText = (status) => statusMap[status]?.text || status

const onAdd = () => {
  router.push('/hr/attendance/form')
}

const onEdit = (item) => {
  router.push(`/hr/attendance/form?id=${item.id}`)
}

const onDelete = async (item) => {
  await showConfirmDialog({
    title: '确认删除',
    message: `确定删除该考勤记录吗？`,
  })
  await deleteAttendance(item.id)
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
.date {
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
