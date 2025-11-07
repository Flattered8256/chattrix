<template>
  <button
    class="theme-toggle"
    @click="toggleTheme"
    :aria-label="themeStore.isDark() ? '切换到亮色模式' : '切换到暗色模式'"
    :title="themeStore.isDark() ? '切换到亮色模式' : '切换到暗色模式'"
  >
    <!-- 太阳图标（亮色模式） -->
    <svg
      v-if="!themeStore.isDark()"
      class="icon sun-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <circle cx="12" cy="12" r="5"></circle>
      <line x1="12" y1="1" x2="12" y2="3"></line>
      <line x1="12" y1="21" x2="12" y2="23"></line>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
      <line x1="1" y1="12" x2="3" y2="12"></line>
      <line x1="21" y1="12" x2="23" y2="12"></line>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
    </svg>

    <!-- 月亮图标（暗色模式） -->
    <svg
      v-else
      class="icon moon-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
    </svg>
  </button>
</template>

<script setup lang="ts">
import { useThemeStore } from "../../store/theme";

const themeStore = useThemeStore();

const toggleTheme = () => {
  themeStore.toggleTheme();
};
</script>

<style scoped>
.theme-toggle {
  position: fixed;
  bottom: 24px;
  left: 24px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--color-bg-secondary);
  border: 2px solid var(--color-border-primary);
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 9999;
  overflow: hidden;
}

.theme-toggle:hover {
  transform: scale(1.1) rotate(10deg);
  box-shadow: var(--shadow-xl);
  background-color: var(--color-bg-hover);
  border-color: var(--color-primary);
}

.theme-toggle:active {
  transform: scale(0.95) rotate(-10deg);
}

.icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-primary);
  transition: all 0.3s ease;
}

/* 太阳图标动画 */
.sun-icon {
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 月亮图标动画 */
.moon-icon {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-toggle {
    bottom: 16px;
    left: 16px;
    width: 44px;
    height: 44px;
  }

  .icon {
    width: 20px;
    height: 20px;
  }
}

/* 避免被其他元素遮挡 */
.theme-toggle::before {
  content: "";
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: transparent;
  z-index: -1;
}
</style>
