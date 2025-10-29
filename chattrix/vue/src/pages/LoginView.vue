<template>
  <AuthLayout>
    <LoginForm />
    
    <template #footer>
      <p class="auth-redirect">
        还没有账号？<router-link to="/register" class="auth-link">立即注册</router-link>
      </p>
    </template>
  </AuthLayout>
</template>

<script setup lang="ts">
import AuthLayout from '../layouts/auth.vue'
import LoginForm from '../components/auth/LoginForm.vue'
</script>