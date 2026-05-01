<template>
  <div class="error-page">
    <van-empty image="error" description="页面不存在" />
    <div class="back-btn">
      <van-button type="primary" round @click="goHome">返回首页</van-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goHome = () => {
  router.replace('/dashboard')
}
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}
.back-btn {
  margin-top: 20px;
}
</style>
