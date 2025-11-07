<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <template v-if="Component">
        <component :is="Component">
          <template #sidebar>
            <MainNavigation />
          </template>
        </component>
      </template>
      <template v-else>
        <component :is="Component" />
      </template>
    </router-view>

    <!-- 主题切换按钮 -->
    <ThemeToggle />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useAuthStore } from "./store/auth";
import { useFriendsStore } from "./store/friends";
import { useChatStore } from "./store/chat";
import { useMessagesStore } from "./store/messages";
import { useThemeStore } from "./store/theme";

import MainNavigation from "./components/home/navigation.vue";
import ThemeToggle from "./components/utils/ThemeToggle.vue";

// 初始化认证状态
const authStore = useAuthStore();
const friendsStore = useFriendsStore();
const chatStore = useChatStore();
const messagesStore = useMessagesStore();
const themeStore = useThemeStore();

const initializeStores = async () => {
  try {
    // 先初始化好友和聊天数据
    await friendsStore.initializeFriends();
    // 确保聊天房间数据完全加载后再初始化消息
    await chatStore.initStore();
    // 最后初始化消息存储，此时privateChatRooms已经有数据了
    await messagesStore.initStore();
  } catch (error) {
    console.error("初始化store失败:", error);
  }
};
onMounted(() => {
  // 初始化主题
  themeStore.initTheme();

  authStore.initializeAuth();

  // 检查用户是否已登录，如果已登录则初始化好友数据
  if (authStore.isAuthenticated) {
    initializeStores();
  }
});

watch(
  () => authStore.isAuthenticated,
  (newValue, oldValue) => {
    if (newValue && !oldValue) {
      initializeStores();
    }
  }
);
</script>

<style>
/* 现有样式保持不变 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* color: #2c3e50; */
  min-height: 100vh;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
</style>
