<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索科目编码/名称"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('finance:subject:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
        @click="onDetail(item)"
      >
        <div class="card-header">
          <span class="title">{{ item.code }}</span>
          <van-tag :type="categoryTypeMap[item.category] || 'default'">
            {{ categoryMap[item.category] || item.category }}
          </van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">科目名称</span>
            <span class="value">{{ item.name }}</span>
          </div>
          <div class="info-row">
            <span class="label">余额方向</span>
            <span class="value">{{ item.balance_direction === 'debit' ? '借方' : '贷方' }}</span>
          </div>
          <div class="info-row">
            <span class="label">上级科目</span>
            <span class="value">{{ item.parent_name || '-' }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('finance:subject:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('finance:subject:delete')"
            size="small"
            type="danger"
            plain
            @click.stop="onDelete(item)"
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
import { showConfirmDialog, showToast } from 'vant'
import ListPage from '@/components/ListPage.vue'
import { getSubjectList, deleteSubject } from '@/api/finance'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })

const categoryMap = {
  asset: '资产',
  liability: '负债',
  equity: '所有者权益',
  cost: '成本',
  income: '损益',
}

const categoryTypeMap = {
  asset: 'primary',
  liability: 'warning',
  equity: 'success',
  cost: 'danger',
  income: 'default',
}

const fetchApi = (params) => getSubjectList(params)

const onAdd = () => {
  router.push('/finance/subject/add')
}

const onDetail = (item) => {
  router.push(`/finance/subject/detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/finance/subject/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除科目 "${item.name}" 吗？`,
    })
    await deleteSubject(item.id)
    showToast({ type: 'success', message: '删除成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      showToast({ type: 'fail', message: '删除失败' })
    }
  }
}
</script>

<style scoped>
.card {
  margin: 10px 12px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
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
  color: #323233;
}
.card-body {
  margin-bottom: 10px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}
.label {
  color: #969799;
}
.value {
  color: #323233;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f5f5f5;
}
</style>
