<template>
  <div class="page">
    <van-nav-bar title="薪资管理" fixed placeholder left-arrow @click-left="router.back()" />
    <ListPage
      ref="listRef"
      :fetch-api="getSalaryList"
      search-placeholder="搜索员工姓名"
      show-add
      :has-add-permission="userStore.hasPermission('hr:salary:add')"
      @add="onAdd"
    >
      <template #list="{ list }">
        <van-swipe-cell v-for="item in list" :key="item.id">
          <van-cell class="card-cell">
            <div class="card">
              <div class="card-header">
                <span class="period">{{ item.year_month || item.month || '-' }}</span>
                <span class="amount">¥{{ item.net_salary || item.actual_salary || 0 }}</span>
              </div>
              <div class="card-body">
                <div class="info-row">
                  <span class="label">员工</span>
                  <span class="value">{{ item.employee_name || item.employee || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">基本工资</span>
                  <span class="value">¥{{ item.base_salary || item.basic_salary || 0 }}</span>
                </div>
                <div class="info-row">
                  <span class="label">实发工资</span>
                  <span class="value highlight">¥{{ item.net_salary || item.actual_salary || 0 }}</span>
                </div>
              </div>
            </div>
          </van-cell>
          <template #right>
            <van-button
              v-if="userStore.hasPermission('hr:salary:edit')"
              square
              type="primary"
              text="编辑"
              class="swipe-btn"
              @click="onEdit(item)"
            />
            <van-button
              v-if="userStore.hasPermission('hr:salary:delete')"
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
import { getSalaryList, deleteSalary } from '@/api/hr'

const router = useRouter()
const userStore = useUserStore()
const listRef = ref(null)

const onAdd = () => {
  router.push('/hr/salary/form')
}

const onEdit = (item) => {
  router.push(`/hr/salary/form?id=${item.id}`)
}

const onDelete = async (item) => {
  await showConfirmDialog({
    title: '确认删除',
    message: `确定删除该薪资记录吗？`,
  })
  await deleteSalary(item.id)
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
.period {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}
.amount {
  font-size: 16px;
  font-weight: 600;
  color: #ee0a24;
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
.highlight {
  color: #ee0a24;
  font-weight: 500;
}
.swipe-btn {
  height: 100%;
}
</style>
