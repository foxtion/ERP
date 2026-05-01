<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索凭证号"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('finance:voucher:add')"
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
          <span class="title">{{ item.voucher_no }}</span>
          <van-tag :type="statusTypeMap[item.status] || 'default'">
            {{ statusMap[item.status] || item.status }}
          </van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">凭证日期</span>
            <span class="value">{{ item.voucher_date }}</span>
          </div>
          <div class="info-row">
            <span class="label">摘要</span>
            <span class="value">{{ item.summary || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">金额</span>
            <span class="value amount">¥ {{ Number(item.total_amount || 0).toFixed(2) }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('finance:voucher:audit')"
            size="small"
            type="primary"
            plain
            @click.stop="onAudit(item)"
          >
            审核
          </van-button>
          <van-button
            v-if="item.status === 'audited' && userStore.hasPermission('finance:voucher:cancel_audit')"
            size="small"
            type="warning"
            plain
            @click.stop="onCancelAudit(item)"
          >
            反审核
          </van-button>
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('finance:voucher:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="item.status === 'draft' && userStore.hasPermission('finance:voucher:delete')"
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
import { getVoucherList, auditVoucher, cancelAuditVoucher, deleteVoucher } from '@/api/finance'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })

const statusMap = {
  draft: '草稿',
  audited: '已审核',
}

const statusTypeMap = {
  draft: 'default',
  audited: 'success',
}

const fetchApi = (params) => getVoucherList(params)

const onAdd = () => {
  router.push('/finance/voucher/add')
}

const onDetail = (item) => {
  router.push(`/finance/voucher/detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/finance/voucher/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除凭证 "${item.voucher_no}" 吗？`,
    })
    await deleteVoucher(item.id)
    showToast({ type: 'success', message: '删除成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      showToast({ type: 'fail', message: '删除失败' })
    }
  }
}

const onAudit = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定审核该凭证吗？' })
    await auditVoucher(item.id)
    showToast({ type: 'success', message: '审核成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
  }
}

const onCancelAudit = async (item) => {
  try {
    await showConfirmDialog({ title: '确认', message: '确定反审核该凭证吗？' })
    await cancelAuditVoucher(item.id)
    showToast({ type: 'success', message: '反审核成功' })
    listPageRef.value?.onRefresh()
  } catch (e) {
    if (e !== 'cancel') showToast({ type: 'fail', message: '操作失败' })
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
.amount {
  color: #ee0a24;
  font-weight: 600;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f5f5f5;
  flex-wrap: wrap;
}
</style>
