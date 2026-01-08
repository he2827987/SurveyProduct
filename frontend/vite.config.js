// vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    // 配置开发服务器
    host: '0.0.0.0', // 允许局域网访问
    port: 3000, // 前端开发服务器端口，你可以根据需要修改
    proxy: {
      // 代理所有以 /api/v1 开头的请求到后端 FastAPI
      // 例如，前端请求 /api/v1/users/ 会被代理到 http://localhost:8000/api/v1/users/
      '/api/v1': {
        target: 'http://localhost:8000', // 你的后端 FastAPI 服务器地址
        changeOrigin: true, // 改变源，将请求头中的 Host 字段改为目标 URL
        // rewrite: (path) => path.replace(/^\/api\/v1/, ''), // 如果后端没有 /api/v1 前缀，则需要重写
                                                            // 但根据我们的API设计，后端有 /api/v1 前缀，所以这里不需要重写
      },
      // 代理 /login 开头的请求（用于 OAuth2 登录接口）
      // 例如，前端请求 /login/access-token 会被代理到 http://localhost:8000/login/access-token
      '/login': {
        target: 'http://localhost:8000', // 你的后端 FastAPI 服务器地址
        changeOrigin: true,
      },
      // 如果你的后端还有其他不带 /api/v1 前缀的接口，也需要在这里添加代理规则
      // 例如，如果 /users/ 接口不带 /api/v1 前缀，你需要添加：
      // '/users': {
      //   target: 'http://localhost:8000',
      //   changeOrigin: true,
      // },
    }
  },
  // 定义环境变量，供前端代码使用
  // 这将确保 request.js 中的 baseURL 能够正确获取到
  define: {
    'import.meta.env.VITE_APP_BASE_API': JSON.stringify('/api/v1'), // 你的后端 API 基础路径
    'import.meta.env.VITE_LOCAL_NETWORK_IP': JSON.stringify('192.168.0.17'), // 默认局域网IP
  },
})
