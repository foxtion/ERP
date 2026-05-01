<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    show-search
    search-placeholder="搜索客户名称/编码"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('sales:customer:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
        @click="showDetail(item)"
      >
        <div class="card-header">
          <span class="title">{{ item.name }}</span>
          <StatusTag
            :status="item.status"
            :options="{ active: '启用', inactive: '禁用' }"
            :type-map="{ active: 'success', inactive: 'danger' }"
          />
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">编码：</span>
            <span class="value">{{ item.code }}</span>
          </div>
          <div class="info-row">
            <span class="label">等级：</span>
            <span class="value">{{ item.level || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">信用额度：</span>
            <span class="value">{{ item.credit_limit != null ? `¥${item.credit_limit}` : '-' }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('sales:customer:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('sales:customer:delete')"
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

  <!-- 客户详情 -->
  <van-action-sheet
    v-model:show="detailVisible"
    title="客户详情"
    :closeable="true"
  >
    <div class="detail-sheet" v-if="currentItem">
      <van-cell-group>
        <van-cell title="客户名称" :value="currentItem.name" />
        <van-cell title="客户编码" :value="currentItem.code" />
        <van-cell title="客户等级" :value="currentItem.level || '-'" />
        <van-cell title="信用额度" :value="currentItem.credit_limit != null ? `¥${currentItem.credit_limit}` : '-'" />
        <van-cell title="联系人" :value="currentItem.contact_name || '-'" />
        <van-cell title="联系电话" :value="currentItem.contact_phone || '-'" />
        <van-cell title="地址" :value="currentItem.address || '-'" />
        <van-cell title="状态">
          <template #value>
            <StatusTag
              :status="currentItem.status"
              :options="{ active: '启用', inactive: '禁用' }"
              :type-map="{ active: 'success', inactive: 'danger' }"
            />
          </template>
        </van-cell>
        <van-cell title="备注" :value="currentItem.remark || '-'" />
      </van-cell-group>
    </div>
  </van-action-sheet>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/store/user'
import { getCustomerList, deleteCustomer } from '@/api/sales'
import ListPage from '@/components/ListPage.vue'
import StatusTag from '@/components/StatusTag.vue'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })
const fetchApi = getCustomerList

const detailVisible = ref(false)
const currentItem = ref(null)

const showDetail = (item) => {
  currentItem.value = item
  detailVisible.value = true
}

const onAdd = () => {
  router.push('/sales/customer-form')
}

const onEdit = (item) => {
  router.push(`/sales/customer-form?id=${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除客户「${item.name}」吗？`,
    })
    await deleteCustomer(item.id)
    showToast('删除成功')
    listPageRef.value?.onRefresh()
  } catch (e) {
    // 取消或删除失败
  }
}
</script>

<style scoped>
.card {
  margin: 10px 12px;
  padding: 12px;
  background-color: #fff;
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
  margin-bottom: 4px;
  font-size: 13px;
  color: #666;
}
.label {
  color: #969799;
  min-width: 70px;
}
.value {
  color: #323233;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.detail-sheet {
  padding-bottom: 16px;
  max-height: 60vh;
  overflow-y: auto;
}
</style>
