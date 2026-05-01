<template>
  <div class="page">
    <van-nav-bar title="功能开发中" fixed placeholder left-arrow @click-left="router.back()" />
    <van-empty description="该功能正在开发中，请使用PC端操作">
      <van-button round type="primary" class="bottom-button" @click="router.back()">返回</van-button>
    </van-empty>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.bottom-button {
  width: 160px;
  height: 40px;
}
</style>
