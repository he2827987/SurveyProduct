/**
 * @fileoverview 应用入口文件
 * @description Vue应用的主入口，负责应用的初始化、插件配置等
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'

// ===== 创建Vue应用实例 =====

console.log('[Vue App] 开始初始化应用...')

const app = createApp(App)

// ===== 注册插件 =====

app.use(router)
app.use(ElementPlus)

// ===== 添加全局错误处理 =====

app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err, info)
}

app.config.warnHandler = (msg, instance, trace) => {
  console.warn('[Vue Warning]', msg, trace)
}

// ===== 挂载应用 =====

// 等待DOM加载完成
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    mountApp()
  })
} else {
  mountApp()
}

function mountApp() {
  console.log('[Vue App] 准备挂载应用...')
  
  // 等待路由准备就绪
  router.isReady().then(() => {
    console.log('[Vue App] 路由准备就绪')
    
    // 挂载应用到 #app 元素
    app.mount('#app')
    
    console.log('[Vue App] ✅ 应用挂载成功')
    
    // 标记应用已挂载（用于自动化测试检测）
    window.__VUE_APP_MOUNTED__ = true
    
    // 检查挂载结果
    const appElement = document.querySelector('#app')
    if (appElement && appElement.children.length > 0) {
      console.log('[Vue App] ✅ 应用内容已渲染')
    } else {
      console.error('[Vue App] ❌ 应用内容未渲染')
    }
  }).catch(err => {
    console.error('[Vue App] ❌ 路由准备失败:', err)
    
    // 标记挂载失败
    window.__VUE_APP_MOUNTED__ = false
    window.__VUE_APP_ERROR__ = err
    
    // 显示错误信息
    const appElement = document.querySelector('#app')
    if (appElement) {
      appElement.innerHTML = `
        <div style="padding: 20px; text-align: center;">
          <h2>应用加载失败</h2>
          <p>错误信息: ${err.message}</p>
          <p>请刷新页面重试，或联系管理员</p>
        </div>
      `
    }
  })
}

// ===== 开发环境调试 =====

if (import.meta.env.DEV) {
  console.log('[Vue App] 开发模式')
  console.log('[Vue App] API Base URL:', import.meta.env.VITE_API_BASE_URL || '/api/v1')
}