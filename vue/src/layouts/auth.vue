<template>
  <div class="auth-layout">
    <div class="auth-container">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// 认证布局组件，用于登录和注册页面
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  width: 100%;
  background-color: #e3f2fd; /* 浅蓝色背景 - 浅色模式 */
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
  transition: background-color 0.3s ease;
}

.auth-container {
  width: 100%;
  max-width: 400px; /* 限制表单最大宽度 */
  padding: 20px;
  box-sizing: border-box;
}

/* 深色模式样式 */
@media (prefers-color-scheme: dark) {
  .auth-layout {
    background-color: #1a1a1a; /* 深色背景 */
  }
}
</style>