<template>
  <AuthLayout>
    <RegisterForm />
    
    <template #footer>
      <p class="auth-redirect">
        已有账号？<router-link to="/login" class="auth-link">立即登录</router-link>
      </p>
    </template>
  </AuthLayout>
</template>

<script setup lang="ts">
import AuthLayout from '../layouts/auth.vue'
import RegisterForm from '../components/auth/RegisterForm.vue'
</script>

<style scoped>
.auth-redirect {
  text-align: center;
  margin-top: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.auth-link {
  color: #409eff;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>