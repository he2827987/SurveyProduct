<!--
  @fileoverview 404页面组件
  @description 当用户访问不存在的页面时显示的404错误页面
  @author Survey System Team
  @version 1.0.0
  @since 2024-01-01
-->

<template>
  <div class="not-found-container">
    <!-- 404错误内容 -->
    <div class="not-found-content">
      <!-- 错误图标 -->
      <div class="error-icon">
        <el-icon size="120" color="#909399">
          <Warning />
        </el-icon>
      </div>

      <!-- 错误标题 -->
      <h1 class="error-title">404</h1>
      <h2 class="error-subtitle">页面未找到</h2>

      <!-- 错误描述 -->
      <p class="error-description">
        抱歉，您访问的页面不存在或已被移除。
      </p>

      <!-- 操作按钮 -->
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          <el-icon><Back /></el-icon>
          返回上页
        </el-button>
      </div>

      <!-- 帮助链接 -->
      <div class="help-links">
        <p>您也可以尝试：</p>
        <ul>
          <li>
            <el-link type="primary" @click="goToDashboard">访问仪表板</el-link>
          </li>
          <li>
            <el-link type="primary" @click="goToSurvey">调研管理</el-link>
          </li>
          <li>
            <el-link type="primary" @click="goToQuestion">题库管理</el-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 404页面组件
 * 提供友好的错误提示和导航选项
 */

import { useRouter } from 'vue-router'
import { Warning, House, Back } from '@element-plus/icons-vue'

// ===== 组件逻辑 =====

const router = useRouter()

/**
 * 返回首页
 */
const goHome = () => {
  router.push('/')
}

/**
 * 返回上一页
 */
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}

/**
 * 跳转到仪表板
 */
const goToDashboard = () => {
  router.push('/')
}

/**
 * 跳转到调研管理
 */
const goToSurvey = () => {
  router.push('/survey')
}

/**
 * 跳转到题库管理
 */
const goToQuestion = () => {
  router.push('/question')
}
</script>

<style scoped>
/* 404页面样式 */
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.not-found-content {
  text-align: center;
  background: white;
  border-radius: 16px;
  padding: 60px 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.error-icon {
  margin-bottom: 20px;
}

.error-title {
  font-size: 72px;
  font-weight: bold;
  color: #409eff;
  margin: 0 0 10px 0;
  line-height: 1;
}

.error-subtitle {
  font-size: 24px;
  color: #606266;
  margin: 0 0 20px 0;
  font-weight: 500;
}

.error-description {
  font-size: 16px;
  color: #909399;
  margin: 0 0 40px 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.help-links {
  border-top: 1px solid #ebeef5;
  padding-top: 30px;
}

.help-links p {
  color: #909399;
  margin: 0 0 15px 0;
  font-size: 14px;
}

.help-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.help-links li {
  margin: 0;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .not-found-content {
    padding: 40px 20px;
  }

  .error-title {
    font-size: 48px;
  }

  .error-subtitle {
    font-size: 20px;
  }

  .error-actions {
    flex-direction: column;
    align-items: center;
  }

  .help-links ul {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
