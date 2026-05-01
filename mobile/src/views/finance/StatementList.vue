<template>
  <div class="list-page">
    <div class="search-bar">
      <van-search
        v-model="query.search"
        placeholder="搜索单位名称"
        shape="round"
        @search="onSearch"
      />
      <div class="filter-row">
        <van-field
          v-model="query.start_date"
          label="开始日期"
          placeholder="选择日期"
          readonly
          @click="showStartPicker = true"
        />
        <van-field
          v-model="query.end_date"
          label="结束日期"
          placeholder="选择日期"
          readonly
          @click="showEndPicker = true"
        />
      </div>
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
            <span class="title">{{ item.doc_no || item.id }}</span>
            <van-tag :type="item.doc_type === 'receivable' ? 'danger' : 'success'">
              {{ item.doc_type === 'receivable' ? '应收' : '应付' }}
            </van-tag>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">往来单位</span>
              <span class="value">{{ item.counterparty || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">金额</span>
              <span class="value text-danger">¥{{ item.amount || 0 }}</span>
            </div>
            <div class="info-row">
              <span class="label">已结清</span>
              <span class="value">¥{{ item.paid_amount || 0 }}</span>
            </div>
            <div class="info-row">
              <span class="label">日期</span>
              <span class="value">{{ item.doc_date || '-' }}</span>
            </div>
          </div>
        </div>

        <van-empty v-if="!loading && list.length === 0" description="暂无数据" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showStartPicker" position="bottom">
      <van-date-picker @confirm="(v) => { query.start_date = formatDate(v); showStartPicker = false }" @cancel="showStartPicker = false" />
    </van-popup>
    <van-popup v-model:show="showEndPicker" position="bottom">
      <van-date-picker @confirm="(v) => { query.end_date = formatDate(v); showEndPicker = false }" @cancel="showEndPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getStatement } from '@/api/finance'

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const query = ref({ search: '', start_date: '', end_date: '' })
const pagination = ref({ page: 1, size: 10, total: 0 })
const showStartPicker = ref(false)
const showEndPicker = ref(false)

const formatDate = (selectedValues) => {
  return selectedValues.selectedValues.join('-')
}

const onLoad = async () => {
  if (refreshing.value) {
    list.value = []
    pagination.value.page = 1
    refreshing.value = false
  }
  loading.value = true
  try {
    const res = await getStatement({
      page: pagination.value.page,
      size: pagination.value.size,
      ...query.value,
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
.filter-row {
  padding: 0 12px;
  background-color: #fff;
}
.card {
  margin: 8px 12px;
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}
</style>
