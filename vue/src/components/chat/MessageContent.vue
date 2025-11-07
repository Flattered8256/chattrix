<template>
  <div class="message-content-wrapper">
    <!-- 文本消息 -->
    <div
      v-if="message.messages_type === 'text'"
      class="message-bubble"
      :class="isSent ? 'sent-bubble' : 'received-bubble'"
    >
      {{ message.content }}
    </div>

    <!-- 图片消息 -->
    <div v-else-if="message.messages_type === 'image'" class="media-container">
      <img
        :src="message.file"
        :alt="message.filename || message.content || ''"
        class="message-image"
        @click="handleMediaClick(message.file, 'image')"
      />
    </div>

    <!-- 视频消息 -->
    <div v-else-if="message.messages_type === 'video'" class="media-container">
      <video :src="message.file" controls class="message-video"></video>
    </div>

    <!-- 文件消息 -->
    <div v-else-if="message.messages_type === 'file'" class="media-container">
      <a
        :href="message.file"
        :download="message.filename || ''"
        class="file-download"
      >
        <img src="../../assets/文件.svg" alt="文件" class="file-icon-svg" />
      </a>
      <span v-if="message.filename" class="media-filename">
        {{ truncateFilename(message.filename) }}
      </span>
    </div>

    <div class="message-time" :class="{ 'time-right': isSent }">
      {{ formatMessageTime(message.timestamp) }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: any;
  isSent: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  previewMedia: [url: string, type: "image" | "video"];
}>();

// 格式化消息时间
const formatMessageTime = (timestamp: string | undefined): string => {
  if (!timestamp) {
    return "";
  }
  const date = new Date(timestamp);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } else {
    return date.toLocaleDateString("zh-CN", {
      month: "2-digit",
      day: "2-digit",
    });
  }
};

// 截断文件名
const truncateFilename = (filename: string, maxLength: number = 20): string => {
  if (filename.length <= maxLength) {
    return filename;
  }

  const lastDotIndex = filename.lastIndexOf(".");
  if (lastDotIndex === -1) {
    return filename.substring(0, maxLength) + "...";
  }

  const name = filename.substring(0, lastDotIndex);
  const ext = filename.substring(lastDotIndex);
  const availableNameLength = maxLength - ext.length - 3;

  if (availableNameLength <= 0) {
    return "..." + ext.substring(0, maxLength - 3);
  }

  return name.substring(0, availableNameLength) + "..." + ext;
};

// 处理媒体点击
const handleMediaClick = (url: string, type: "image" | "video") => {
  if (type === "image") {
    emit("previewMedia", url, type);
  }
};
</script>

<style scoped>
.message-content-wrapper {
  display: flex;
  flex-direction: column;
}

/* 接收方气泡样式 - 统一圆角，无尖角 */
.message-bubble.received-bubble {
  background-color: var(--color-chat-bubble-received);
  padding: 10px 12px;
  border-radius: 18px; /* 统一圆角，无尖角 */
  border: 1px solid var(--color-border-primary);
  word-wrap: break-word;
  word-break: break-word;
  font-size: 14px;
  color: var(--color-chat-text-received);
  max-width: 100%;
  align-self: flex-start;
  white-space: pre-wrap;
}

/* 发送方气泡样式 - 统一圆角，无尖角 */
.message-bubble.sent-bubble {
  background-color: var(--color-chat-bubble-sent);
  padding: 10px 12px;
  border-radius: 18px; /* 统一圆角，无尖角 */
  border: 1px solid transparent;
  word-wrap: break-word;
  word-break: break-word;
  font-size: 14px;
  color: var(--color-chat-text-sent);
  max-width: 100%;
  align-self: flex-end;
  white-space: pre-wrap;
}

.message-time {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-top: 4px;
  text-align: left;
  align-self: flex-start;
}

.time-right {
  text-align: right;
  align-self: flex-end;
}

.media-container {
  padding: 8px;
  max-width: 300px;
  margin: 4px 0;
}

.message-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
  background-color: transparent;
}

.message-image:hover {
  transform: scale(1.05);
}

.message-video {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  background-color: transparent;
}

.file-download {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  text-decoration: none;
  padding: 12px;
  background-color: var(--color-bg-secondary);
  border-radius: 8px;
  transition: background-color 0.2s ease;
  width: fit-content;
}

.file-download:hover {
  background-color: var(--color-bg-hover);
}

.file-icon-svg {
  width: 48px;
  height: 48px;
}

.media-filename {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  text-align: center;
}
</style>
