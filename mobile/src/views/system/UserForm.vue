<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑用户' : '新增用户'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.username"
            required
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请输入用户名' }]"
          />
          <van-field
            v-model="form.password"
            :required="!isEdit"
            type="password"
            label="密码"
            placeholder="请输入密码"
            :rules="isEdit ? [] : [{ required: true, message: '请输入密码' }]"
          />
          <van-field
            v-model="form.phone"
            label="手机号"
            placeholder="请输入手机号"
          />
          <van-field
            v-model="form.email"
            label="邮箱"
            placeholder="请输入邮箱"
          />
          <van-field
            v-model="form.dept_name"
            is-link
            readonly
            label="部门"
            placeholder="请选择部门"
            @click="showDeptPicker = true"
          />
          <van-field
            v-model="form.role_names"
            is-link
            readonly
            label="角色"
            placeholder="请选择角色"
            @click="showRolePicker = true"
          />
          <van-field
            v-model="form.status"
            is-link
            readonly
            label="状态"
            placeholder="请选择状态"
            @click="showStatusPicker = true"
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" :loading="submitting">
            {{ isEdit ? '保存' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showDeptPicker" round position="bottom">
      <van-picker :columns="deptColumns" @cancel="showDeptPicker = false" @confirm="onDeptConfirm" />
    </van-popup>

    <van-popup v-model:show="showRolePicker" round position="bottom">
      <van-picker :columns="roleColumns" @cancel="showRolePicker = false" @confirm="onRoleConfirm" />
    </van-popup>

    <van-popup v-model:show="showStatusPicker" round position="bottom">
      <van-picker :columns="statusColumns" @cancel="showStatusPicker = false" @confirm="onStatusConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createUser, updateUser, getUserList } from '@/api/system'
import { getDeptTree } from '@/api/system'
import { getRoleList } from '@/api/system'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const userId = ref(null)

const form = ref({
  username: '',
  password: '',
  phone: '',
  email: '',
  dept: '',
  dept_name: '',
  role_ids: [],
  role_names: '',
  status: '启用',
  is_active: true,
})

const showDeptPicker = ref(false)
const showRolePicker = ref(false)
const showStatusPicker = ref(false)

const deptColumns = ref([])
const roleColumns = ref([])
const statusColumns = [
  { text: '启用', value: true },
  { text: '禁用', value: false },
]

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    userId.value = id
    await loadDetail(id)
  }

  try {
    const deptRes = await getDeptTree()
    const list = deptRes.data || []
    deptColumns.value = flattenDept(list)
  } catch (e) {
    console.error('加载部门失败', e)
  }

  try {
    const roleRes = await getRoleList({ page: 1, size: 500 })
    const list = roleRes.data?.results || roleRes.data?.list || roleRes.results || []
    roleColumns.value = list.map(item => ({ text: item.name || item.label || item, value: item.id || item.value || item }))
  } catch (e) {
    console.error('加载角色失败', e)
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
    const res = await getUserList({ id })
    const list = res.data?.results || res.data?.list || res.results || []
    const item = list.find(i => String(i.id) === String(id)) || list[0]
    if (item) {
      form.value = {
        username: item.username || '',
        password: '',
        phone: item.phone || '',
        email: item.email || '',
        dept: item.dept || '',
        dept_name: item.dept_name || '',
        role_ids: item.role_ids || [],
        role_names: (item.role_names || []).join(', '),
        status: item.is_active ? '启用' : '禁用',
        is_active: item.is_active,
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function onClickLeft() {
  router.back()
}

function onDeptConfirm({ selectedOptions }) {
  form.value.dept = selectedOptions[0].value
  form.value.dept_name = selectedOptions[0].text.trim()
  showDeptPicker.value = false
}

function onRoleConfirm({ selectedOptions }) {
  const role = selectedOptions[0]
  if (!form.value.role_ids.includes(role.value)) {
    form.value.role_ids.push(role.value)
    const names = form.value.role_names ? form.value.role_names.split(', ') : []
    names.push(role.text)
    form.value.role_names = names.join(', ')
  }
  showRolePicker.value = false
}

function onStatusConfirm({ selectedOptions }) {
  form.value.is_active = selectedOptions[0].value
  form.value.status = selectedOptions[0].text
  showStatusPicker.value = false
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    delete data.dept_name
    delete data.role_names
    delete data.status
    if (isEdit.value && !data.password) {
      delete data.password
    }
    if (isEdit.value) {
      await updateUser(userId.value, data)
      showToast('修改成功')
    } else {
      await createUser(data)
      showToast('添加成功')
    }
    router.back()
  } catch (e) {
    showFailToast(e?.response?.data?.message || e.message || '操作失败')
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
