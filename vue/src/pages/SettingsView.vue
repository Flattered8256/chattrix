<template>
  <div class="settings-container">
    <h1>设置</h1>
    
    <!-- 用户头像和信息部分 -->
    <div class="user-profile-section">
      <div class="user-avatar-section">
        <Avatar 
          size="xlarge" 
          @error="handleAvatarError"
        />
      </div>
      <div class="user-info-section">
        <h2>{{ user?.username || '未登录' }}</h2>
        <p>用户ID: {{ user?.id || '未知' }}</p>
                
      </div>
    </div>
    
    <!-- 其他设置项可以在这里添加 -->
    <div><Username v-if="user" :user="user" @usernameUpdated="handleUsernameUpdated" @error="handleUsernameError" /></div>
    <!-- 添加密码修改组件 -->
    <div class="password-section"><Password v-if="user" /></div>
    <!-- 添加登出按钮 -->
    <div class="logout-section">
      <Logout />
    </div>
  </div>
</template>

<script setup lang="ts">
// 从 Pinia 导入 storeToRefs
import { storeToRefs } from 'pinia';
import { useAuthStore } from '../store/auth';
import Avatar from '../components/auth/Avatar.vue';
import Username from '../components/auth/username.vue';
import Password from '../components/auth/password.vue';
import Logout from '../components/auth/Logout.vue';
import type { User } from '../api/auth';

// 获取认证信息
const authStore = useAuthStore();
// 使用storeToRefs来解构store中的响应式属性
const { user } = storeToRefs(authStore);

// 处理头像上传错误
const handleAvatarError = (message: string) => {
  // 这里可以添加错误处理逻辑，如显示提示信息
  console.error('头像上传错误:', message);
};

// 处理用户名更新
const handleUsernameUpdated = (updatedUser: User) => {
  console.log('用户名已更新:', updatedUser.username);
};

// 处理用户名更新错误
const handleUsernameError = (message: string) => {
  console.error('更新用户名时出错:', message);
};
</script>

<style scoped>
.settings-container {
  padding: 20px;
  position: relative;
  min-height: auto;
}

.user-profile-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-details h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.user-id {
  color: #666;
  margin: 0;
}

/* 调整用户名组件的样式以适应设置页面 */
.user-info-section,
.password-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin: 20px 0;
  padding: 0;
}

/* 登出按钮区域样式 */
.logout-section {
  margin-top: 40px;
  text-align: right;
}

@media (prefers-color-scheme: dark) {
  .user-profile-section {
    background-color: #333;
    color: rgba(255, 255, 255, 0.87);
  }
}
</style>