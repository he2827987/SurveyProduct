/**
 * @fileoverview 用户管理API模块
 * @description 提供用户注册、登录、信息管理等功能的API调用
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import request from './request'

// ===== 用户认证相关API =====

/**
 * 用户登录
 * @param {Object} loginData - 登录数据
 * @param {string} loginData.username - 用户名
 * @param {string} loginData.password - 密码
 * @returns {Promise<Object>} 登录结果，包含token和用户信息
 */
export function login(loginData) {
  // 后端使用Form数据，需要转换为FormData格式
  const formData = new FormData()
  formData.append('username', loginData.username)
  formData.append('password', loginData.password)
  
  return request.post('/users/login/access-token', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 用户注册
 * @param {Object} registerData - 注册数据
 * @param {string} registerData.username - 用户名
 * @param {string} registerData.email - 邮箱
 * @param {string} registerData.password - 密码
 * @returns {Promise<Object>} 注册结果
 */
export function register(registerData) {
  return request.post('/users/register', registerData)
}

/**
 * 用户登出
 * @returns {Promise<Object>} 登出结果
 */
export function logout() {
  // 后端没有专门的登出端点，前端只需要清除本地存储的token
  return Promise.resolve({ message: 'Logged out successfully' })
}

// ===== 用户信息管理API =====

/**
 * 获取当前用户信息
 * @returns {Promise<Object>} 当前用户信息
 */
export function getCurrentUser() {
  return request.get('/users/me')
}

/**
 * 更新用户信息
 * @param {Object} userData - 用户更新数据
 * @returns {Promise<Object>} 更新后的用户信息
 */
export function updateUser(userData) {
  return request.put('/users/me', userData)
}

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_password - 旧密码
 * @param {string} passwordData.new_password - 新密码
 * @returns {Promise<Object>} 修改结果
 */
export function changePassword(passwordData) {
  return request.put('/users/me/password', passwordData)
}

// ===== 用户管理API（管理员功能） =====

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 用户列表
 */
export function getUsers(params = {}) {
  return request.get('/users/', { params })
}

/**
 * 根据ID获取用户信息
 * @param {number} userId - 用户ID
 * @returns {Promise<Object>} 用户信息
 */
export function getUserById(userId) {
  return request.get(`/users/${userId}`)
}

/**
 * 创建新用户
 * @param {Object} userData - 用户创建数据
 * @returns {Promise<Object>} 创建的用户信息
 */
export function createUser(userData) {
  return request.post('/users/', userData)
}

/**
 * 更新用户信息（管理员）
 * @param {number} userId - 用户ID
 * @param {Object} userData - 用户更新数据
 * @returns {Promise<Object>} 更新后的用户信息
 */
export function updateUserById(userId, userData) {
  return request.put(`/users/${userId}`, userData)
}

/**
 * 删除用户
 * @param {number} userId - 用户ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteUser(userId) {
  return request.delete(`/users/${userId}`)
}
