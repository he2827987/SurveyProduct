<!--
  @fileoverview 应用根组件
  @description Vue应用的根组件，负责整体布局和路由视图渲染
  @author Survey System Team
  @version 1.0.0
  @since 2024-01-01
-->

<template>
  <!-- 应用根容器 -->
  <div id="app">
    <!-- 路由视图 -->
    <router-view />
  </div>
</template>

<script setup>
/**
 * 应用根组件
 * 使用Vue 3 Composition API
 */

// ===== 组件逻辑 =====

// 这里可以添加全局的逻辑，如：
// - 全局状态管理
// - 全局事件监听
// - 应用初始化逻辑
</script>

<style scoped>
/* 应用根样式 */
#app {
  width: 100%;
  height: 100vh;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style> 