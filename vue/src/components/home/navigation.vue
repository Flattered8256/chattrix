<template>
  <div class="main-navigation">
    <div class="logo">
      <h2>Chattrix</h2>
    </div>
    
    <ul class="nav-links">
      <li v-for="item in navItems" :key="item.path">
        <router-link 
          :to="item.path" 
          class="nav-link"
          :class="{ active: $route.path === item.path }"
          @click="handleNavClick(item.path)"
        >
          <span class="nav-icon">
            <!-- 使用导入的SVG图标 -->
            <img v-if="item.svgPath" :src="item.svgPath" class="svg-icon" :alt="item.text" />
                        <!-- 未读消息标徽 -->
            <span v-if="item.path === '/contacts' && showContactsBadge" class="badge">
              {{ friendsStore.unreadFriendMessagesCount > 99 ? '99+' : friendsStore.unreadFriendMessagesCount }}
            </span>
            <!-- 聊天未读消息标徽 -->
            <span v-if="item.path === '/chat' && showChatBadge" class="badge">
              {{ totalUnreadMessages > 99 ? '99+' : totalUnreadMessages }}
            </span>
          </span>
          <span class="nav-text">{{ item.text }}</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useFriendsStore } from '../../store/friends'
import { useMessagesStore } from '../../store/messages'
import { useRoute } from 'vue-router'
import { computed } from 'vue' 
import chatIcon from '@/assets/chat-dot-round.svg'
import friendsIcon from '@/assets/好友.svg'
import settingsIcon from '@/assets/设置.svg'
const friendsStore = useFriendsStore()
const messagesStore = useMessagesStore()
const route = useRoute()

// 计算是否显示联系人图标标徽
const showContactsBadge = computed(() => {
  // 只有当有未读好友消息且不在好友页面时才显示
  return friendsStore.hasUnreadFriendMessages && route.path !== '/contacts'
})

// 计算是否显示聊天图标标徽
const showChatBadge = computed(() => {
  // 只有当有未读聊天消息且不在聊天页面时才显示
  return messagesStore.hasUnreadMessages && route.path !== '/chat'
})

// 计算总未读聊天消息数
const totalUnreadMessages = computed(() => {
  return Array.from(messagesStore.unreadMessagesCount.values()).reduce((total, count) => total + count, 0)
})

const navItems = [
  // 使用导入的SVG图标
  { path: '/chat', text: '聊天', svgPath: chatIcon },
  { path: '/contacts', text: '好友', svgPath: friendsIcon },
  { path: '/settings', text: '设置', svgPath: settingsIcon },
]

// 处理导航点击事件
const handleNavClick = (path: string) => {
  // 当点击好友页面时，重置未读消息状态
  if (path === '/contacts') {
    friendsStore.resetUnreadFriendMessages()
  }

}
</script>
<style scoped>
.main-navigation {
  padding: 20px;
}

/* 添加SVG图标样式 */
.svg-icon {
  width: 24px;
  height: 24px;
  display: inline-block;
  vertical-align: middle;
}

.logo {
  text-align: center;
  margin-bottom: 30px;
}

/* 未读消息标徽样式 */
.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: #ff4757;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
}

.nav-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  text-decoration: none;
  color: #495057;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-bottom: 5px;
}

.nav-link:hover {
  background-color: #e9ecef;
  color: #007bff;
}

.nav-link.active {
  background-color: #007bff;
  color: white;
}

.nav-icon {
  font-size: 18px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
  position: relative
}

.nav-text {
  font-size: 16px;
}

/* 移动端样式：导航项水平排列 */
@media (max-width: 767px) {
  .main-navigation {
    padding: 0;
    height: 100%;
    display: flex;
    align-items: center;
  }
  
  .logo {
    display: none; /* 隐藏logo，节省底部导航栏空间 */
  }
  
  .nav-links {
    display: flex;
    width: 100%;
    height: 100%;
  }
  
  .nav-links li {
    flex: 1; /* 每个导航项平均占据宽度 */
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .nav-link {
    flex-direction: column; /* 图标在上，文字在下 */
    padding: 5px;
    margin-bottom: 0;
    height: 100%;
    width: 100%;
    justify-content: center;
    border-radius: 0;
  }
  
  .nav-icon {
    margin-right: 0;
    margin-bottom: 2px;
    font-size: 20px;
  }
  
  .nav-text {
    font-size: 12px;
  }
}
</style>