<template>
  <div 
    v-if="message" 
    class="toast-notification" 
    :class="type"
    @click="close"
  >
    <span class="toast-icon" v-if="type === 'success'">✓</span>
    <span class="toast-icon" v-else-if="type === 'error'">✗</span>
    <span class="toast-message">{{ message }}</span>
    <button class="toast-close" @click.stop="close">×</button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

interface Props {
  message: string
  type: 'success' | 'error'
  duration?: number
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000
})

const emit = defineEmits<{
  close: []
}>()

let timer: ReturnType<typeof setTimeout> | null = null

// 打开提示框并设置自动关闭定时器
onMounted(() => {
  if (props.duration > 0) {
    timer = setTimeout(() => {
      close()
    }, props.duration)
  }
})

// 关闭提示框
const close = () => {
  emit('close')
}

// 组件卸载时清理定时器
onUnmounted(() => {
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
})
</script>

<style scoped>
/* 提示框容器 */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 250px;
  max-width: 400px;
  animation: slideIn 0.3s ease;
  cursor: pointer;
  transition: transform 0.2s ease;
}

/* 悬停效果 */
.toast-notification:hover {
  transform: translateY(-2px);
}

/* 成功提示样式 */
.toast-notification.success {
  background-color: #67c23a;
  color: white;
}

/* 错误提示样式 */
.toast-notification.error {
  background-color: #f56c6c;
  color: white;
}

/* 图标样式 */
.toast-icon {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

/* 消息文本 */
.toast-message {
  flex: 1;
  word-wrap: break-word;
}

/* 关闭按钮 */
.toast-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.toast-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 动画定义 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>