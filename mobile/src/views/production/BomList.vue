<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    search-placeholder="搜索产品名称/编码"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('production:bom:add')"
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
          <span class="title">{{ item.product_name }}</span>
          <van-tag type="primary">v{{ item.version }}</van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">产品编码</span>
            <span class="value">{{ item.product_code }}</span>
          </div>
          <div class="info-row">
            <span class="label">规格型号</span>
            <span class="value">{{ item.spec || '-' }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('production:bom:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('production:bom:delete')"
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
import { getBomList, deleteBom } from '@/api/production'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const listPageRef = ref(null)

const query = ref({ search: '' })

const fetchApi = (params) => getBomList(params)

const onAdd = () => {
  router.push('/production/bom/add')
}

const onDetail = (item) => {
  router.push(`/production/bom/detail/${item.id}`)
}

const onEdit = (item) => {
  router.push(`/production/bom/edit/${item.id}`)
}

const onDelete = async (item) => {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定删除 BOM "${item.product_name}" 吗？`,
    })
    await deleteBom(item.id)
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
