<template>
  <div class="list-page">
    <!-- 搜索栏 -->
    <div class="search-bar" v-if="showSearch">
      <van-search
        v-model="query.search"
        :placeholder="searchPlaceholder"
        shape="round"
        @search="onSearch"
        @clear="onSearch"
      />
      <slot name="filters" :query="query" />
    </div>

    <!-- 下拉刷新 + 列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <slot name="list" :list="list" />

        <van-empty v-if="!loading && list.length === 0" description="暂无数据" />
      </van-list>
    </van-pull-refresh>

    <!-- 新增按钮（浮动） -->
    <van-button
      v-if="showAdd && hasAddPermission"
      class="fab-add"
      icon="plus"
      type="primary"
      round
      @click="onAddClick"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  showSearch: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: '搜索' },
  showAdd: { type: Boolean, default: false },
  hasAddPermission: { type: Boolean, default: true },
  fetchApi: { type: Function, required: true },
  query: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['add', 'update:query'])

const onAddClick = () => {
  console.log('[ListPage] add button clicked')
  emit('add')
}

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const pagination = ref({ page: 1, size: 10, total: 0 })

const onLoad = async () => {
  if (refreshing.value) {
    list.value = []
    pagination.value.page = 1
    refreshing.value = false
  }

  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size,
      ...props.query,
    }
    const res = await props.fetchApi(params)
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

// 监听 query 变化，重新加载
watch(
  () => props.query,
  () => {
    finished.value = false
    list.value = []
    pagination.value.page = 1
    onLoad()
  },
  { deep: true }
)

defineExpose({ list, onRefresh })
</script>

<style scoped>
.list-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.search-bar {
  background-color: #fff;
}
.fab-add {
  position: fixed;
  right: 20px;
  bottom: 70px;
  z-index: 99;
  width: 50px;
  height: 50px;
}
</style>
