<template>
  <div class="page">
    <van-nav-bar :title="isEdit ? '编辑角色' : '新增角色'" fixed placeholder left-arrow @click-left="onClickLeft" />
    <div class="form-content">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            required
            label="角色名称"
            placeholder="请输入角色名称"
            :rules="[{ required: true, message: '请输入角色名称' }]"
          />
          <van-field
            v-model="form.code"
            required
            label="角色编码"
            placeholder="请输入角色编码"
            :rules="[{ required: true, message: '请输入角色编码' }]"
          />
          <van-field
            v-model="form.description"
            rows="2"
            autosize
            type="textarea"
            label="描述"
            placeholder="请输入描述"
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" :loading="submitting">
            {{ isEdit ? '保存' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createRole, updateRole, getRoleList } from '@/api/system'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const submitting = ref(false)
const roleId = ref(null)

const form = ref({
  name: '',
  code: '',
  description: '',
})

onMounted(async () => {
  const id = route.query.id
  if (id) {
    isEdit.value = true
    roleId.value = id
    await loadDetail(id)
  }
})

async function loadDetail(id) {
  try {
    const res = await getRoleList({ id })
    const list = res.data?.results || res.data?.list || res.results || []
    const item = list.find(i => String(i.id) === String(id)) || list[0]
    if (item) {
      form.value = {
        name: item.name || '',
        code: item.code || '',
        description: item.description || '',
      }
    }
  } catch (e) {
    showToast('加载详情失败')
  }
}

function onClickLeft() {
  router.back()
}

async function onSubmit() {
  submitting.value = true
  try {
    const data = { ...form.value }
    if (isEdit.value) {
      await updateRole(roleId.value, data)
      showToast('修改成功')
    } else {
      await createRole(data)
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
