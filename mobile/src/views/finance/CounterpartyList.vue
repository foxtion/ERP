<template>
  <ListPage
    ref="listPageRef"
    :fetch-api="fetchApi"
    :query="query"
    show-search
    search-placeholder="搜索单位名称"
    :show-add="true"
    :has-add-permission="userStore.hasPermission('finance:counterparty:add')"
    @add="onAdd"
  >
    <template #list="{ list }">
      <div
        v-for="item in list"
        :key="item.id"
        class="card"
      >
        <div class="card-header">
          <span class="title">{{ item.name }}</span>
          <van-tag :type="item.is_active ? 'success' : 'danger'">
            {{ item.is_active ? '启用' : '禁用' }}
          </van-tag>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">类型</span>
            <span class="value">{{ typeMap[item.type] || item.type }}</span>
          </div>
          <div class="info-row">
            <span class="label">联系人</span>
            <span class="value">{{ item.contact || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">电话</span>
            <span class="value">{{ item.phone || '-' }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            v-if="userStore.hasPermission('finance:counterparty:edit')"
            size="small"
            type="primary"
            plain
            @click.stop="onEdit(item)"
          >
            编辑
          </van-button>
          <van-button
            v-if="userStore.hasPermission('finance:counterparty:delete')"
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

  <!-- 新增/编辑弹窗 -->
  <van-dialog
    v-model:show="dialogVisible"
    :title="isEdit ? '编辑往来单位' : '新增往来单位'"
    show-cancel-button
    @confirm="onSubmit"
  >
    <van-form>
      <van-field v-model="form.name" label="名称" placeholder="请输入名称" :rules="[{required:true}]" />
      <van-field v-model="form.type" label="类型" placeholder="customer/supplier/both/other" />
      <van-field v-model="form.contact" label="联系人" placeholder="请输入联系人" />
      <van-field v-model="form.phone" label="电话" placeholder="请输入电话" />
    </van-form>
  </van-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { showConfirmDialog, showToast, showFailToast } from 'vant'
import { useUserStore } from '@/store/user'
import { getCounterpartyList, createCounterparty, updateCounterparty, deleteCounterparty } from '@/api/finance'
import ListPage from '@/components/ListPage.vue'

const userStore = useUserStore()
const listPageRef = ref()
const query = ref({})

const typeMap = { customer: '客户', supplier: '供应商', both: '客户+供应商', other: '其他' }

const fetchApi = (params) => getCounterpartyList(params)

const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const form = reactive({ name: '', type: '', contact: '', phone: '' })

const resetForm = () => {
  form.name = ''; form.type = ''; form.contact = ''; form.phone = ''
}

const onAdd = () => {
  isEdit.value = false
  currentId.value = null
  resetForm()
  dialogVisible.value = true
}

const onEdit = (item) => {
  isEdit.value = true
  currentId.value = item.id
  Object.assign(form, item)
  dialogVisible.value = true
}

const onSubmit = async () => {
  if (!form.name) {
    showFailToast('请输入名称')
    return
  }
  try {
    if (isEdit.value) {
      await updateCounterparty(currentId.value, form)
    } else {
      await createCounterparty(form)
    }
    showToast(isEdit.value ? '更新成功' : '新增成功')
    dialogVisible.value = false
    listPageRef.value.onRefresh()
  } catch (e) {
    showFailToast(e?.response?.data?.message || '操作失败')
  }
}

const onDelete = (item) => {
  showConfirmDialog({
    title: '确认删除',
    message: `确定删除往来单位「${item.name}」吗？`,
  }).then(async () => {
    try {
      await deleteCounterparty(item.id)
      showToast('删除成功')
      listPageRef.value.onRefresh()
    } catch (e) {
      showFailToast(e?.response?.data?.message || '删除失败')
    }
  }).catch(() => {})
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
  color: #666;
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
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
</style>
