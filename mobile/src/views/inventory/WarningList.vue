<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="getWarningList"
    search-placeholder="搜索物料名称/编码"
    :show-add="false"
  >
    <template #list="{ list }">
      <div v-for="item in list" :key="item.id" class="card-item">
        <div class="card-header">
          <span class="title">{{ item.material_name }}</span>
          <StatusTag
            :status="item.warning_type"
            :options="warningOptions"
            :type-map="warningTypeMap"
          />
        </div>
        <div class="card-body">
          <div><span class="label">物料编码：</span>{{ item.material_code || '-' }}</div>
          <div><span class="label">规格：</span>{{ item.specification || '-' }}</div>
          <div><span class="label">当前数量：</span><span class="current">{{ item.current_quantity || 0 }}</span></div>
          <div><span class="label">安全库存：</span>{{ item.safety_stock || 0 }}</div>
          <div><span class="label">上限阈值：</span>{{ item.max_stock || '-' }}</div>
          <div><span class="label">仓库：</span>{{ item.warehouse_name || '-' }}</div>
          <div><span class="label">预警时间：</span>{{ item.warning_time || '-' }}</div>
        </div>
        <div class="card-actions">
          <van-button
            v-if="userStore.hasPermission('inventory:warning:handle') && item.status !== 'handled'"
            size="small"
            type="primary"
            @click="onHandle(item)"
          >
            处理
          </van-button>
          <van-tag v-else-if="item.status === 'handled'" type="success">已处理</van-tag>
        </div>
      </div>
    </template>
  </ListPage>
</template>

<script setup>
import { ref } from 'vue'
import { showDialog, showToast, showLoadingToast, closeToast } from 'vant'
import ListPage from '@/components/ListPage.vue'
import StatusTag from '@/components/StatusTag.vue'
import { useUserStore } from '@/store/user'
import { getWarningList, handleWarning } from '@/api/inventory'

const userStore = useUserStore()
const listPageRef = ref()

const warningOptions = {
  low_stock: '库存不足',
  over_stock: '库存积压',
  expiry: '即将过期',
}

const warningTypeMap = {
  low_stock: 'danger',
  over_stock: 'warning',
  expiry: 'primary',
}

const onHandle = async (item) => {
  try {
    await showDialog({
      title: '确认处理',
      message: `确定处理物料「${item.material_name}」的库存预警吗？`,
    })
    showLoadingToast({ message: '处理中...', forbidClick: true })
    await handleWarning(item.id)
    closeToast()
    showToast('处理成功')
    listPageRef.value?.onRefresh()
  } catch (error) {
    closeToast()
    if (error !== 'cancel') {
      showToast(error.message || '处理失败')
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
.current {
  color: #ee0a24;
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
