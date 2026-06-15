<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑部门' : '新增部门'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            required
            label="部门名称"
            placeholder="请输入部门名称"
            :rules="[{ required: true, message: '请输入部门名称' }]"
          />
          <van-field
            v-model="form.code"
            label="部门编码"
            placeholder="请输入部门编码"
          />
          <van-field
            v-model="form.parent_name"
            is-link
            readonly
            label="上级部门"
            placeholder="请选择上级部门"
            @click="showParentPicker = true"
          />
          <van-field
            v-model="form.leader"
            label="负责人"
            placeholder="请输入负责人"
          />
          <van-field
            v-model="form.phone"
            label="联系电话"
            placeholder="请输入联系电话"
          />
          <van-field
            v-model="form.email"
            label="邮箱"
            placeholder="请输入邮箱"
          />
          <van-field
            v-model="form.address"
            label="地址"
            placeholder="请输入地址"
          />
          <van-field
            v-model.number="form.sort_order"
            type="digit"
            label="排序"
            placeholder="请输入排序号"
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" :loading="submitting">
            {{ isEdit ? '保存' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showParentPicker" round position="bottom">
      <van-picker :columns="parentColumns" @cancel="showParentPicker = false" @confirm="onParentConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createDept, updateDept, getDeptTree } from '@/api/system'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const deptId = ref(null)

const form = ref({
  name: '',
  code: '',
  parent: '',
  parent_name: '',
  leader: '',
  phone: '',
  email: '',
  address: '',
  sort_order: 0,
})

const showParentPicker = ref(false)
const parentColumns = ref([{ text: '无', value: null }])

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    deptId.value = id
    await loadDetail(id)
  }

  try {
    const res = await getDeptTree()
    const list = res.data || []
    parentColumns.value = [{ text: '无', value: null }, ...flattenDept(list)]
  } catch (e) {
    console.error('加载部门失败', e)
  }
})

function flattenDept(list, prefix = '') {
  const result = []
  for (const item of list) {
    result.push({ text: prefix + item.name, value: item.id })
    if (item.children && item.children.length > 0) {
      result.push(...flattenDept(item.children, prefix + '  '))
    }
  }
  return result
}

async function loadDetail(id) {
  try {
    const res = await getDeptTree()
    const list = flattenTree(res.data || [])
    const item = list.find(i => String(i.id) === String(id))
    if (item) {
      form.value = {
        name: item.name || '',
        code: item.code || '',
        parent: item.parent || '',
        parent_name: item.parent_name || '',
        leader: item.leader || '',
        phone: item.phone || '',
        email: item.email || '',
        address: item.address || '',
        sort_order: item.sort_order || 0,
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function flattenTree(tree, result = []) {
  for (const node of tree) {
    result.push(node)
    if (node.children && node.children.length > 0) {
      flattenTree(node.children, result)
    }
  }
  return result
}

function onClickLeft() {
  router.back()
}

function onParentConfirm({ selectedOptions }) {
  form.value.parent = selectedOptions[0].value
  form.value.parent_name = selectedOptions[0].text.trim()
  showParentPicker.value = false
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    delete data.parent_name
    if (isEdit.value) {
      await updateDept(deptId.value, data)
      showToast('修改成功')
    } else {
      await createDept(data)
      showToast('添加成功')
    }
    router.back()
  } catch (e) {
    showFailToast(e?.response?.data?.message || e?.response?.data?.detail || e.message || '操作失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.form-content {
  padding-top: 12px;
}
.submit-btn {
  margin: 24px 16px;
}
</style>
