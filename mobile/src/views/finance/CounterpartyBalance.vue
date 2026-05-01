<template>
  <div class="list-page">
    <div class="search-bar">
      <van-search
        v-model="query.search"
        placeholder="搜索往来单位"
        shape="round"
        @search="onSearch"
      />
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div
          v-for="item in list"
          :key="item.id"
          class="card"
        >
          <div class="card-header">
            <span class="title">{{ item.name }}</span>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">应收金额</span>
              <span class="value text-danger">¥{{ item.receivable_amount || 0 }}</span>
            </div>
            <div class="info-row">
              <span class="label">应付金额</span>
              <span class="value text-success">¥{{ item.payable_amount || 0 }}</span>
            </div>
            <div class="info-row">
              <span class="label">余额</span>
              <span class="value text-primary">¥{{ item.balance || 0 }}</span>
            </div>
          </div>
        </div>

        <van-empty v-if="!loading && list.length === 0" description="暂无数据" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getBalanceSheet } from '@/api/finance'

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const query = ref({ search: '' })
const pagination = ref({ page: 1, size: 10, total: 0 })

const onLoad = async () => {
  if (refreshing.value) {
    list.value = []
    pagination.value.page = 1
    refreshing.value = false
  }
  loading.value = true
  try {
    const res = await getBalanceSheet({
      page: pagination.value.page,
      size: pagination.value.size,
      search: query.value.search,
    })
    const data = res.data
    list.value.push(...(data.list || []))
    pagination.value.total = data.pagination?.total || 0
    if (list.value.length >= pagination.value.total) {
      finished.value = true
    } else {
      pagination.value.page += 1
    }
  } catch (e) {
    // 错误已由 request 拦截器处理
  } finally {
    loading.value = false
  }
}

const onRefresh = () => {
  finished.value = false
  list.value = []
  pagination.value.page = 1
  onLoad()
}

const onSearch = () => {
  finished.value = false
  list.value = []
  pagination.value.page = 1
  onLoad()
}
</script>

<style scoped>
.card {
  margin: 8px 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.card-header {
  margin-bottom: 8px;
}
.card-header .title {
  font-size: 15px;
  font-weight: bold;
  color: #323233;
}
.card-body {
  font-size: 13px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
.info-row .label {
  color: #969799;
}
.info-row .value {
  color: #323233;
  font-weight: 500;
}
</style>
