<template>
  <AuthLayout>
    <LoginForm />
  </AuthLayout>
</template>

<script setup lang="ts">
import AuthLayout from '../layouts/auth.vue'
import LoginForm from '../components/superadmin/LoginForm.vue'
</script>

<style scoped>
.admin-header {
  text-align: center;
  margin-bottom: 2rem;
}

.admin-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}
</style>
