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
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
}

.auth-container {
  width: 100%;
  max-width: 450px;
}
</style>
