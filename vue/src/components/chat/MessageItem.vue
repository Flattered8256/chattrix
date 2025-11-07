<template>
  <div
    :id="`message-${message.id}`"
    class="message-item"
    :class="isSent ? 'sent' : 'received'"
  >
    <!-- 接收的消息 -->
    <template v-if="!isSent">
      <div class="message-avatar">
        <Avatar_look :user="message.sender" size="small" />
        <!-- 在群聊中显示用户名 -->
        <div v-if="isGroupChat" class="message-username">
          {{ message.sender?.username || "未知用户" }}
        </div>
      </div>
      <div class="message-content">
        <MessageContent
          :message="message"
          :is-sent="isSent"
          @preview-media="(url, type) => emit('previewMedia', url, type)"
        />
      </div>
    </template>

    <!-- 发送的消息 -->
    <template v-else>
      <div class="message-content">
        <MessageContent
          :message="message"
          :is-sent="isSent"
          @preview-media="(url, type) => emit('previewMedia', url, type)"
        />
      </div>
      <div class="message-avatar">
        <Avatar_look :user="currentUser" size="small" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import Avatar_look from "../auth/Avatar_look.vue";
import MessageContent from "./MessageContent.vue";

interface Props {
  message: any;
  currentUserId: number;
  currentUser: any;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  previewMedia: [url: string, type: "image" | "video"];
}>();

const isSent = computed(() => props.message.sender?.id === props.currentUserId);

// 判断是否为群聊
const isGroupChat = computed(() => {
  // 根据消息的room_type属性判断是否为群聊
  return props.message.room_type === "group";
});
</script>

<style scoped>
.message-item {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 12px;
  width: 100%;
}

.message-item.received {
  justify-content: flex-start;
}

.message-item.sent {
  justify-content: flex-end;
}

.message-avatar {
  flex-shrink: 0;
  order: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.message-item.sent .message-avatar {
  order: 3;
}

.message-username {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: center;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-content {
  max-width: 60%;
  min-width: 0;
  flex: 0 1 auto;
  order: 2;
}

.message-item.sent .message-content {
  order: 1;
}
</style>
