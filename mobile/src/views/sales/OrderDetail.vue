<template>
  <div class="page">
    <van-nav-bar title="销售订单详情" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div v-if="order" class="detail-content">
      <van-cell-group inset>
        <van-cell title="订单编号" :value="order.order_no" />
        <van-cell title="客户" :value="order.customer_name" />
        <van-cell title="订单日期" :value="order.order_date" />
        <van-cell title="交货日期" :value="order.delivery_date || '-'" />
        <van-cell title="状态">
          <template #value>
            <StatusTag :status="order.status" :options="statusTextMap" :type-map="statusTypeMap" />
          </template>
        </van-cell>
        <van-cell title="总金额" :value="`¥${order.total_amount || 0}`" />
        <van-cell title="备注" :value="order.remark || '-'" />
      </van-cell-group>

      <div class="section-title">订单明细</div>
      <van-cell-group inset>
        <van-cell v-for="item in order.items" :key="item.id">
          <template #title>
            <div class="item-title">{{ item.material_name }}</div>
            <div class="item-sub">规格: {{ item.spec || '-' }} | 单位: {{ item.unit || '件' }}</div>
          </template>
          <template #value>
            <div class="item-value">
              <div>数量: {{ item.quantity }}</div>
              <div>单价: ¥{{ item.price }}</div>
              <div>金额: ¥{{ item.amount }}</div>
            </div>
          </template>
        </van-cell>
        <van-empty v-if="!order.items || order.items.length === 0" description="暂无明细" />
      </van-cell-group>
    </div>
    <van-empty v-else description="加载中..." />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getSalesOrderDetail } from '@/api/sales'
import StatusTag from '@/components/StatusTag.vue'

const route = useRoute()
const router = useRouter()
const orderId = route.params.id

const order = ref(null)

const statusTextMap = {
  draft: '草稿',
  confirmed: '已确认',
  partial: '部分出库',
  completed: '已完成',
  cancelled: '已取消',
}

const statusTypeMap = {
  draft: 'default',
  confirmed: 'primary',
  partial: 'warning',
  completed: 'success',
  cancelled: 'danger',
}

onMounted(async () => {
  if (!orderId) {
    showToast('订单ID不存在')
    router.back()
    return
  }
  try {
    const res = await getSalesOrderDetail(orderId)
    order.value = res.data || null
    if (!order.value) {
      showToast('订单不存在')
    }
  } catch (e) {
    showToast('加载失败')
  }
})

function onClickLeft() {
  router.back()
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.detail-content {
  padding-top: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #666;
  padding: 16px 16px 8px;
}
.item-title {
  font-weight: bold;
  color: #323233;
}
.item-sub {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}
.item-value {
  text-align: right;
  font-size: 13px;
  color: #666;
}
</style>
