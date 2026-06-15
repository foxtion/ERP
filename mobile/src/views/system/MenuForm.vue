<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑菜单' : '新增菜单'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            required
            label="菜单名称"
            placeholder="请输入菜单名称"
            :rules="[{ required: true, message: '请输入菜单名称' }]"
          />
          <van-field
            v-model="form.title"
            required
            label="显示标题"
            placeholder="请输入显示标题"
            :rules="[{ required: true, message: '请输入显示标题' }]"
          />
          <van-field
            v-model="form.path"
            label="路由路径"
            placeholder="请输入路由路径"
          />
          <van-field
            v-model="form.component"
            label="组件路径"
            placeholder="请输入组件路径"
          />
          <van-field
            v-model="form.icon"
            label="图标"
            placeholder="请输入图标名"
          />
          <van-field
            v-model="form.permission"
            label="权限标识"
            placeholder="请输入权限标识"
          />
          <van-field
            v-model="form.menu_type"
            is-link
            readonly
            label="菜单类型"
            placeholder="请选择菜单类型"
            @click="showTypePicker = true"
          />
          <van-field
            v-model="form.parent_name"
            is-link
            readonly
            label="上级菜单"
            placeholder="请选择上级菜单"
            @click="showParentPicker = true"
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

    <van-popup v-model:show="showTypePicker" round position="bottom">
      <van-picker :columns="typeColumns" @cancel="showTypePicker = false" @confirm="onTypeConfirm" />
    </van-popup>

    <van-popup v-model:show="showParentPicker" round position="bottom">
      <van-picker :columns="parentColumns" @cancel="showParentPicker = false" @confirm="onParentConfirm" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createMenu, updateMenu, getMenuTree } from '@/api/system'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const menuId = ref(null)

const form = ref({
  name: '',
  title: '',
  path: '',
  component: '',
  icon: '',
  permission: '',
  menu_type: 'MENU',
  parent: '',
  parent_name: '',
  sort_order: 0,
})

const showTypePicker = ref(false)
const showParentPicker = ref(false)

const typeColumns = [
  { text: '菜单', value: 'MENU' },
  { text: '按钮', value: 'BUTTON' },
]

const parentColumns = ref([{ text: '无', value: null }])

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    menuId.value = id
    await loadDetail(id)
  }

  try {
    const res = await getMenuTree()
    const list = res.data || []
    parentColumns.value = [{ text: '无', value: null }, ...flattenMenu(list)]
  } catch (e) {
    console.error('加载菜单失败', e)
  }
})

function flattenMenu(list, prefix = '') {
  const result = []
  for (const item of list) {
    result.push({ text: prefix + (item.title || item.name), value: item.id })
    if (item.children && item.children.length > 0) {
      result.push(...flattenMenu(item.children, prefix + '  '))
    }
  }
  return result
}

async function loadDetail(id) {
  try {
    const res = await getMenuTree()
    const list = flattenTree(res.data || [])
    const item = list.find(i => String(i.id) === String(id))
    if (item) {
      form.value = {
        name: item.name || '',
        title: item.title || '',
        path: item.path || '',
        component: item.component || '',
        icon: item.icon || '',
        permission: item.permission || '',
        menu_type: item.menu_type || 'MENU',
        parent: item.parent || '',
        parent_name: item.parent_name || '',
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

function onTypeConfirm({ selectedOptions }) {
  form.value.menu_type = selectedOptions[0].value
  showTypePicker.value = false
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
      await updateMenu(menuId.value, data)
      showToast('修改成功')
    } else {
      await createMenu(data)
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
