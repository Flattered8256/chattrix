<template>
  <div class="avatar-container" @click="triggerFileInput">
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
      
      <!-- 上传遮罩层 -->
      <div class="upload-overlay">
        <span class="upload-icon">+</span>
      </div>
    </div>
    
    <!-- 文件输入框（隐藏） -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
    
    <!-- 上传加载状态 -->
    <div v-if="isUploading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
  
  <!-- Toast 组件用于显示提示信息 -->
  <Toast 
    v-if="toastMessage"
    :message="toastMessage"
    :type="toastType"
    :duration="3000"
    @close="clearToast"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../../store/auth';
import type { User } from '../../api/auth';
import Toast from '../utils/toast.vue';

// 定义props
interface Props {
  user?: User | null;
  size?: 'small' | 'medium' | 'large' | 'xlarge';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium'
});

// 定义emits
const emit = defineEmits<{
  avatarUpdated: [user: User];
  error: [message: string];
}>();

// 引用auth store
const authStore = useAuthStore();

// 文件输入框引用
const fileInput = ref<HTMLInputElement | null>(null);

// 组件状态
const isUploading = ref(false);
const toastMessage = ref('');
const toastType = ref<'success' | 'error'>('success');

// 计算属性
// 计算属性
const userAvatar = computed(() => {
  const avatarUrl = props.user?.user_avatar || authStore.user?.user_avatar || '';
  
  // 如果头像URL存在但不是完整URL且不以'/media/'开头，则使用代理路径
  if (avatarUrl && !avatarUrl.startsWith('http')) {
    return avatarUrl.startsWith('/media/') ? avatarUrl : `/media/${avatarUrl}`;
  }
  
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

// 触发文件选择对话框
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// 处理文件选择
const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (!file) return;
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    showToast('请选择图片文件', 'error');
    return;
  }
  
  // 验证文件大小（5MB限制）
  if (file.size > 5 * 1024 * 1024) {
    showToast('图片大小不能超过5MB', 'error');
    return;
  }
  
  // 上传文件
  await uploadAvatarFile(file);
  
  // 重置文件输入框
  if (target) {
    target.value = '';
  }
};

// 上传头像文件
const uploadAvatarFile = async (file: File) => {
  isUploading.value = true;
  
  try {
    // 调用auth store中的更新个人资料方法
    const result = await authStore.updateProfile({ user_avatar: file });
    
    if (result.success && authStore.user) {
      // 使用Toast组件显示成功消息
      showToast('头像更新成功！', 'success');
      // 触发头像更新事件
      emit('avatarUpdated', authStore.user);
    } else {
      throw new Error('上传失败');
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '上传失败，请重试';
    showToast(errorMessage, 'error');
  } finally {
    isUploading.value = false;
  }
};

// 显示Toast提示
const showToast = (message: string, type: 'success' | 'error') => {
  toastMessage.value = message;
  toastType.value = type;
};

// 清除Toast提示
const clearToast = () => {
  toastMessage.value = '';
};

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
  cursor: pointer;
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

/* 上传遮罩层 */
.upload-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 50%;
}

/* 上传图标 */
.upload-icon {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

/* 加载遮罩层 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  z-index: 10;
}

/* 加载动画 */
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 悬停效果 */
.avatar-container:hover .upload-overlay {
  opacity: 1;
}

.avatar-container:hover .avatar-wrapper {
  border-color: #1da1f2;
}

.avatar-container:hover .avatar-image {
  transform: scale(1.05);
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

/* 动画定义 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>