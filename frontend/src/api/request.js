/**
 * @fileoverview HTTP请求工具模块
 * @description 基于Axios的HTTP客户端，提供统一的请求/响应拦截器和错误处理
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import axios from 'axios';
import { ElMessage } from 'element-plus';
import router from '@/router';

/**
 * 验证 JWT token 是否有效
 * @param {string} token - JWT token
 * @returns {Promise<boolean>} token 是否有效
 */
export function verifyToken(token) {
  if (!token) return Promise.resolve(false);

  try {
    // 解码 JWT token 检查过期时间
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);

    // 检查是否过期
    if (payload.exp && payload.exp < currentTime) {
      return Promise.resolve(false);
    }

    return Promise.resolve(true);
  } catch (error) {
    console.error('Token 解码失败:', error);
    return Promise.resolve(false);
  }
}

/**
 * 验证当前用户 token 并处理认证失败
 * @returns {Promise<boolean>} 验证是否通过
 */
export function validateAuthToken() {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return Promise.resolve(false);
  }

  return verifyToken(token).then(isValid => {
    if (!isValid) {
      // Token 无效，清除本地存储并重定向到登录页
      localStorage.removeItem('access_token');
      ElMessage.warning('认证已过期，请重新登录');
      router.push('/login');
      return false;
    }
    return true;
  });
}

// ===== 创建Axios实例 =====

/**
 * Axios实例配置
 * @type {import('axios').AxiosInstance}
 */
const service = axios.create({
  // Render 部署：通过环境变量指定后端完整域名；本地默认为 '/api/v1' 走代理
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 300000, // 5分钟超时，适合LLM API调用
});

// ===== 请求拦截器 =====

/**
 * 请求拦截器
 * 在发送请求前自动添加认证token
 */
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  error => {
    console.error('请求错误 (Request Interceptor):', error);
    return Promise.reject(error);
  }
);

// ===== 响应拦截器 =====

/**
 * 响应拦截器
 * 统一处理响应数据和错误
 */
service.interceptors.response.use(
  response => {
    // 直接返回response.data，简化API调用
    return response.data;
  },
  error => {
    console.error('响应错误 (Response Interceptor):', error);
    
    // ===== 错误处理逻辑 =====
    let message = '请求失败，请稍后再试。';

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      const detail = data?.detail;

      // 处理FastAPI返回的详细错误信息
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        message = detail.map(err => 
          `${Array.isArray(err.loc) ? err.loc.join('.') : 'Field'} ${err.msg}`
        ).join('; ');
      } else if (error.response.statusText) {
        message = error.response.statusText;
      }

      // ===== HTTP状态码处理 =====
      switch (status) {
        case 400:
          ElMessage.error(`请求错误: ${message}`);
          break;
        case 401:
          ElMessage.error(`认证失败: ${message || '请重新登录。'}`);
          localStorage.removeItem('access_token');
          router.push('/login').catch(err => {
            if (err.name !== 'NavigationDuplicated') {
              console.error('路由跳转错误:', err);
            }
          });
          break;
        case 403:
          ElMessage.error(`权限不足: ${message || '您没有权限执行此操作。'}`);
          break;
        case 404:
          ElMessage.error(`资源未找到: ${message || '请求的资源不存在。'}`);
          break;
        case 422:
          ElMessage.error(`数据验证失败: ${message}`);
          break;
        case 500:
          ElMessage.error(`服务器内部错误: ${message || '服务器发生未知错误。'}`);
          break;
        default:
          ElMessage.error(`错误 ${status}: ${message}`);
      }
    } else if (error.request) {
      // 网络错误处理
      console.error('网络错误 (No Response):', error.request);
      ElMessage.error('网络连接失败，请检查网络设置');
    } else {
      // 其他错误处理
      console.error('其他错误:', error.message);
      ElMessage.error('请求配置错误');
    }

    return Promise.reject(error);
  }
);

// ===== 导出 =====

export default service;
