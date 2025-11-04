<template>
  <div class="main-layout">
    <!-- 内容栏 -->
    <main class="content">
      <router-view />
    </main>
    
    <!-- 导航栏 -->
    <aside class="sidebar">
      <nav class="main-nav">
        <!-- 导航内容将在导航组件中实现 -->
        <slot name="sidebar"></slot>
      </nav>
    </aside>
  </div>
</template>

<script setup lang="ts">
// 主布局组件，实现两栏结构
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  flex-direction: column;
  overflow: hidden; /* 防止整个页面滚动 */
}

/* 桌面端：左右两栏布局 */
@media (min-width: 768px) {
  .main-layout {
    flex-direction: row;
  }
  
  .sidebar {
    width: 280px; /* 使用固定宽度，不受滚动条影响 */
    height: 100vh;
    position: fixed; /* 修改为fixed定位，完全固定在左侧 */
    top: 0;
    left: 0; /* 固定在左侧 */
    overflow-y: auto; /* 导航栏内容超出时可以滚动 */
    background-color:#e3f2fd ;
    border-right: 1px solid #e9ecef;
    z-index: 100; /* 确保导航栏在内容之上 */
    flex-shrink: 0; /* 防止导航栏被压缩 */
  }
  
  .content {
    flex-grow: 1; /* 内容区域占据剩余所有空间 */
    
    margin-left: 280px; /* 为固定的导航栏留出空间 */
    height: 100vh;
    overflow-y: auto; /* 内容区域独立滚动 */
    overflow-x: hidden; /* 防止水平滚动条 */
  }
}

/* 移动端：导航栏固定在底部 */
@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 60px; /* 底部导航栏的高度 */
    background-color:#e3f2fd ;
    border-top: 1px solid #e9ecef;
    z-index: 100;
    order: 2; /* 移动端导航栏在底部 */
  }
  
  .content {
    flex: 1;
    padding-bottom: 60px; /* 为底部导航栏留出空间 */
    order: 1; /* 移动端内容在顶部 */
    overflow-y: auto; /* 移动端内容也可以独立滚动 */
    overflow-x: hidden;
  }
}

/* 添加自定义滚动条样式，使滚动条更美观 */
.content::-webkit-scrollbar {
  width: 8px;
}

.content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>