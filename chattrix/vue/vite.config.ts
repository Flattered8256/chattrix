import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      
      // 将所有以/api开头的请求转发到后端服务器
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,

      },
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,

      },
       // 添加媒体文件路径的代理配置
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
        // WebSocket代理配置
        '/ws': {
            target: 'ws://localhost:8000',
            changeOrigin: true,
            ws: true,
        },
        // 静态文件路径的代理配置
        '/static': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
    }
  }
})
