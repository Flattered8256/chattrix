<template>
  <div class="contacts-view">
  
    <!-- 搜索用户组件 -->
    <SearchUser />
    <!-- 好友列表组件 -->
    <FriendsList />
    <!-- 好友列表将在这里显示 -->
  </div>
</template>

<script setup lang="ts">
// 导入搜索用户组件
import SearchUser from '../components/auth/SearchUser.vue';
import FriendsList from '../components/friends/FriendsList.vue';
import { onMounted } from 'vue'
import { useFriendsStore } from '../store/friends'

const friendsStore = useFriendsStore()

onMounted(() => {
  // 不需要重置未读消息状态，保持未读标徽显示
})
</script>

<style scoped>
.contacts-view {
  padding: 20px;
}

.contacts-view h2 {
  margin-bottom: 20px;
  color: #333;
  font-size: 24px;
}
</style>