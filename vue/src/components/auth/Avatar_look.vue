<template>
  <div class="avatar-container">
    <div class="avatar-wrapper" :class="avatarSizeClass">
      <!-- 显示用户头像，如果没有则显示默认头像 -->
      <img
        v-if="userAvatar"
        :src="userAvatar"
        :alt="username || 'User avatar'"
        class="avatar-image"
        @error="handleImageError"
      />
      <div v-else class="default-avatar">
        <!-- 显示用户名首字母作为默认头像 -->
        <span v-if="username">{{ username.charAt(0).toUpperCase() }}</span>
        <span v-else>U</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '../../store/auth';
import type { User } from '../../api/auth';

// 定义props
interface Props {
  user?: User | null;
  size?: 'small' | 'medium' | 'large' | 'xlarge';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium'
});

// 引用auth store
const authStore = useAuthStore();


const userAvatar = computed(() => {
  const avatarUrl = props.user?.user_avatar || authStore.user?.user_avatar || '';
    
  return avatarUrl;
});



const username = computed(() => {
  if (props.user?.username) {
    return props.user.username;
  }
  return authStore.user?.username || '';
});

const avatarSizeClass = computed(() => {
  return `avatar-${props.size}`;
});

// 处理头像加载错误
const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
};
</script>

<style scoped>
/* 头像容器 */
.avatar-container {
  position: relative;
  display: inline-block;
}

/* 头像包装器 */
.avatar-wrapper {
  position: relative;
  overflow: hidden;
  border-radius: 50%;
  border: 2px solid #e1e8ed;
  transition: all 0.3s ease;
}

/* 头像图片 */
.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

/* 默认头像 */
.default-avatar {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

/* 头像大小类 */
.avatar-small {
  width: 32px;
  height: 32px;
}

.avatar-small .default-avatar {
  font-size: 14px;
}

.avatar-medium {
  width: 48px;
  height: 48px;
}

.avatar-medium .default-avatar {
  font-size: 20px;
}

.avatar-large {
  width: 64px;
  height: 64px;
}

.avatar-large .default-avatar {
  font-size: 28px;
}

.avatar-xlarge {
  width: 96px;
  height: 96px;
}

.avatar-xlarge .default-avatar {
  font-size: 40px;
}
</style>