/**
 * @fileoverview 路由配置模块
 * @description 定义应用的路由规则、导航守卫等
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { validateAuthToken } from '@/api/request'

// ===== 路由配置 =====

const routes = [
  // ===== 认证相关路由 =====
  {
    path: '/login',
    name: 'LoginRegister',
    component: () => import('@/views/LoginRegister.vue'),
    meta: { title: '登录注册', requiresAuth: false }
  },

  // ===== 主应用路由（需要Layout布局） =====
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板', requiresAuth: true }
      },
      {
        path: 'survey',
        name: 'Survey',
        component: () => import('@/views/survey/Index.vue'),
        meta: { title: '调研管理', requiresAuth: true }
      },
      {
        path: 'surveys/:id',
        name: 'SurveyDetail',
        component: () => import('@/views/survey/Detail.vue'),
        meta: { title: '调研详情', requiresAuth: true }
      },
      {
        path: 'question',
        name: 'Question',
        component: () => import('@/views/question/Index.vue'),
        meta: { title: '题库管理', requiresAuth: true }
      },
      {
        path: 'organization',
        name: 'Organization',
        component: () => import('@/views/organization/Index.vue'),
        meta: { title: '组织架构管理', requiresAuth: true }
      },
      {
        path: 'organization/list',
        name: 'OrganizationList',
        component: () => import('@/views/organization/OrganizationList.vue'),
        meta: { title: '组织管理', requiresAuth: true }
      },
      {
        path: 'analysis',
        name: 'Analysis',
        component: () => import('@/views/analysis/Index.vue'),
        meta: { title: '数据分析', requiresAuth: true }
      },
      {
        path: 'compare',
        name: 'Compare',
        component: () => import('@/views/compare/Index.vue'),
        meta: { title: '企业对比', requiresAuth: true }
      },
      {
        path: 'survey/:id/subjective-answers',
        name: 'SubjectiveAnswers',
        component: () => import('@/views/survey/SubjectiveAnswers.vue'),
        meta: { title: '主观题详情', requiresAuth: true }
      },

      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人信息', requiresAuth: true }
      }
    ]
  },

  // ===== 移动端调研填写路由（不需要登录，不需要Layout） =====
  {
    path: '/survey/fill/:id',
    name: 'SurveyFill',
    component: () => import('@/views/survey/Fill.vue'),
    meta: { title: '调研填写', requiresAuth: false }
  },

  // ===== 断点续答路由 =====
  {
    path: '/survey/resume',
    name: 'SurveyResume',
    component: () => import('@/views/survey/Resume.vue'),
    meta: { title: '继续填写', requiresAuth: false }
  },

  // ===== 404页面路由 =====
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到', requiresAuth: false }
  }
]

// ===== 创建路由实例 =====

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ===== 全局前置守卫 =====

/**
 * 路由前置守卫
 * 处理认证检查、页面标题设置等
 */
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 调研系统`
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      // 保存当前路径，登录后可以跳转回来
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 异步验证 token 有效性
    validateAuthToken().then(isValid => {
      if (!isValid) {
        // token 无效，已经在 validateAuthToken 中处理了重定向
        return
      }
      // token 有效，继续路由
      next()
    }).catch(() => {
      // 验证失败，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    })
    return
  }

  next()
})

// ===== 全局后置钩子 =====

/**
 * 路由后置钩子
 * 处理页面切换后的清理工作
 */
router.afterEach((to, from) => {
  // 可以在这里添加页面切换后的逻辑
  // 例如：滚动到顶部、清理状态等
})

export default router
