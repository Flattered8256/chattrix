<template>
  <div class="message-sender">
    <!-- 左侧上传 -->
    <button class="upload-button" :disabled="disabled" @click="openFileSelect">
      <img src="../../assets/添加.svg" class="upload-icon" />
    </button>

    <!-- 隐藏文件框 -->
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      accept="image/*,video/*,.pdf,.doc,.docx,.txt,.zip,.rar"
      @change="onFileChange"
    />

    <!-- 中间输入框 -->
    <textarea
      v-model="text"
      class="message-input"
      :disabled="disabled"
      placeholder="输入消息…"
      @keydown="onKeyDown"
      rows="1"
    />

    <!-- 右侧发送 -->
    <button
      class="send-button"
      :disabled="disabled || !canSend"
      @click="doSendText"
    >
      {{ disabled ? "发送中…" : "发送" }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

/* ========== 组件接口 ========== */
defineProps<{
  disabled?: boolean; // 父级可强制禁用
}>();

const emit = defineEmits<{
  "send-text": [content: string]; // 纯文本
  "send-file": [file: File, type: MsgType]; // 文件
}>();

type MsgType = "text" | "image" | "video" | "file";

/* ========== 内部状态 ========== */
const text = ref("");
const fileInput = ref<HTMLInputElement>();

const canSend = computed(() => text.value.trim().length > 0);

/* ========== 文本发送 ========== */
function doSendText() {
  if (!canSend.value) return;
  emit("send-text", text.value.trim());
  text.value = ""; // 父级确认成功后自行滚动等
}

function onKeyDown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    doSendText();
  }
}

/* ========== 文件发送 ========== */
function openFileSelect() {
  fileInput.value?.click();
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  // 简单类型判断
  let msgType: MsgType = "file";
  if (file.type.startsWith("image/")) msgType = "image";
  else if (file.type.startsWith("video/")) msgType = "video";

  emit("send-file", file, msgType);

  // 清空 input，允许连续选同一个文件
  target.value = "";
}
</script>

<style scoped>
.message-sender {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-secondary);
}

.hidden {
  display: none;
}

/* 文件上传按钮样式 */
.upload-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--color-text-primary);
}

.upload-button:hover:not(:disabled) {
  background-color: var(--color-bg-hover);
}

.upload-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-icon {
  width: 20px;
  height: 20px;
}

/* 消息输入框样式 */
.message-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--color-border-primary);
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
  resize: none;
  max-height: 120px;
  overflow-y: auto;
  font-family: inherit;
  line-height: 1.4;
  background-color: var(--color-input-bg);
  color: var(--color-text-primary);
}

.message-input:focus {
  border-color: var(--color-primary);
}

.message-input:disabled {
  background-color: var(--color-bg-tertiary);
  cursor: not-allowed;
}

/* 发送按钮样式 */
.send-button {
  padding: 10px 20px;
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  min-width: 80px;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.send-button:disabled {
  background-color: var(--color-bg-tertiary);
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
