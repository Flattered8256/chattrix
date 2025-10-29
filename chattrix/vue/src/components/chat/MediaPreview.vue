<template>
  <div v-if="show" class="media-preview-overlay" @click="handleOverlayClick">
    <div class="media-preview-container" @click.stop>
      <button class="close-preview" @click="close" aria-label="关闭预览">×</button>
      
      <!-- 图片预览 -->
      <img 
        v-if="previewType === 'image'" 
        :src="previewUrl" 
        class="preview-image" 
        :alt="altText"
        @load="handleImageLoad"
        @error="handleImageError"
      />
      
      <!-- 视频预览 -->
      <video 
        v-else-if="previewType === 'video'" 
        :src="previewUrl" 
        class="preview-video" 
        controls
        @loadeddata="handleVideoLoad"
        @error="handleVideoError"
      >
        您的浏览器不支持视频播放
      </video>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-indicator">
        加载中...
      </div>
      
      <!-- 错误状态 -->
      <div v-if="showError" class="error-message">
        加载失败，请重试
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

// 定义组件 Props
interface Props {
  show: boolean;
  previewUrl: string;
  previewType: 'image' | 'video';
  altText?: string;
}

// 定义组件事件
const emit = defineEmits<{
  close: [];
  'update:show': [value: boolean];
}>();

// Props
const props = withDefaults(defineProps<Props>(), {
  altText: '媒体预览',
  show: false
});

// 组件状态
const isLoading = ref(true);
const showError = ref(false);

// 关闭预览
const close = () => {
  emit('close');
  emit('update:show', false);
};

// 点击遮罩层关闭
const handleOverlayClick = () => {
  close();
};

// 图片加载完成
const handleImageLoad = () => {
  isLoading.value = false;
  showError.value = false;
};

// 图片加载失败
const handleImageError = () => {
  isLoading.value = false;
  showError.value = true;
};

// 视频加载完成
const handleVideoLoad = () => {
  isLoading.value = false;
  showError.value = false;
};

// 视频加载失败
const handleVideoError = () => {
  isLoading.value = false;
  showError.value = true;
};

// 监听显示状态变化
watch(() => props.show, (newValue) => {
  if (newValue) {
    // 显示时重置状态
    isLoading.value = true;
    showError.value = false;
  }
});

// 监听预览URL变化
watch(() => props.previewUrl, () => {
  if (props.show) {
    isLoading.value = true;
    showError.value = false;
  }
});
</script>

<style scoped>
.media-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.media-preview-container {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-preview {
  position: absolute;
  top: -40px;
  right: -40px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.close-preview:hover {
  background: rgba(255, 255, 255, 0.3);
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
  animation: zoomIn 0.3s ease;
}

.preview-video {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
  animation: zoomIn 0.3s ease;
}

.loading-indicator {
  color: white;
  font-size: 16px;
  padding: 20px;
}

.error-message {
  color: #ff6b6b;
  font-size: 16px;
  padding: 20px;
  text-align: center;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes zoomIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 767px) {
  .media-preview-container {
    max-width: 95%;
    max-height: 95%;
  }
  
  .close-preview {
    top: -50px;
    right: 0;
    background: rgba(0, 0, 0, 0.5);
  }
  
  .preview-image,
  .preview-video {
    max-height: 70vh;
  }
}
</style>