// frontend/src/utils/request.js
import axios from 'axios'

// 创建 axios 实例
const service = axios.create({
  // Vite 环境变量: VITE_API_BASE_URL
  // 请在你的 .env 文件中设置 VITE_API_BASE_URL
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000', // 默认后端地址
  timeout: 15000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // --- 调试信息 0: 拦截器被触发 ---
    console.log('>>> Request Interceptor Triggered <<<');
    console.log('>>> Original Config:', config);
    // --- 调试信息 0 结束 ---

    // 1. 在发送请求之前做些什么，比如添加 token
    // --- 修改开始 ---
    // 假设你把 JWT token 存在 localStorage 中，键名为 'access_token'
    // 请根据你实际的键名和存储方式进行调整
    console.log('>>> Attempting to retrieve token from localStorage with key "access_token" <<<'); // 调试信息
    const token = localStorage.getItem('access_token'); 
    console.log('>>> Token retrieved:', token); // 调试信息 (如果 token 不存在，这里会是 null)
    
    // 如果获取到了 token，则添加到请求头中
    if (token) {
      // 2. 确保 Authorization 头的格式符合后端要求
      // 常见格式有: 
      // - Bearer <token> (最常见的 JWT 格式)
      // - Token <token> 
      // - 自定义格式
      // 请根据你的后端 API 文档调整
      console.log('>>> Token found, setting Authorization header <<<'); // 调试信息
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('>>> Authorization header set to:', config.headers['Authorization']); // 调试信息
    } else {
      console.log('>>> No token found in localStorage. Authorization header will NOT be set. <<<'); // 调试信息
    }
    // --- 修改结束 ---
    
    // --- 调试信息 3: 最终配置 ---
    console.log('>>> Final Config before request is sent:', config);
    // --- 调试信息 3 结束 ---

    return config;
  },
  (error) => {
    // 对请求错误做些什么
    console.error('Request Interceptor Error:', error); // 使用 console.error 更醒目
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    // 可以在这里统一处理 HTTP 状态码 2xx 的情况
    return response.data
  },
  (error) => {
    // 对响应错误做点什么
    console.log('Response Error:', error) // for debug
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          // router.push('/login'); // 需要引入 router
          break
        case 403:
          // 禁止访问
          break
        case 404:
          // 请求地址出错
          break
        case 500:
          // 服务器内部错误
          break
        default:
          // 其他错误
      }
    }
    return Promise.reject(error)
  }
)

export default service
