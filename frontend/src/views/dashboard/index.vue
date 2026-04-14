<template>
  <div class="dashboard-container">
    <el-card>
      <h2>欢迎使用 ERP 管理系统</h2>
      <p>当前登录用户：{{ userStore.userInfo?.username || '-' }}</p>
      <p>登录时间：{{ currentTime }}</p>
    </el-card>

    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-title">系统模块</div>
            <div class="stat-value">7</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-title">在线人数</div>
            <div class="stat-value">1</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-title">待办事项</div>
            <div class="stat-value">0</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-title">通知消息</div>
            <div class="stat-value">0</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const currentTime = ref('')

onMounted(() => {
  currentTime.value = new Date().toLocaleString()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.stat-row {
  margin-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}
</style>
