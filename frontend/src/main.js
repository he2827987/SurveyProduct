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

const app = createApp(App)

// ===== 注册插件 =====

app.use(router)
app.use(ElementPlus)

// ===== 挂载应用 =====

app.mount('#app')