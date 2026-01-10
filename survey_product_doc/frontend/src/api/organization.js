/**
 * @fileoverview 组织管理API模块
 * @description 提供组织、成员、部门等管理功能的API调用
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import request from './request'

// ===== 组织管理API =====

/**
 * 创建组织
 * @param {Object} organizationData - 组织数据
 * @param {string} organizationData.name - 组织名称
 * @param {string} organizationData.description - 组织描述
 * @param {string} organizationData.address - 组织地址
 * @param {string} organizationData.contact_email - 联系邮箱
 * @param {string} organizationData.contact_phone - 联系电话
 * @returns {Promise<Object>} 创建的组织对象
 */
export function createOrganization(organizationData) {
  return request.post('/organizations/', organizationData)
}

/**
 * 获取组织列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {string} params.name - 组织名称筛选
 * @returns {Promise<Array>} 组织列表
 */
export function getOrganizations(params = {}) {
  return request.get('/organizations/', { params })
}

/**
 * 获取公开的组织列表（用于企业对比）
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 公开的组织列表
 */
export function getPublicOrganizations(params = {}) {
  return request.get('/organizations/public/', { params })
}

export function getPublicDepartments(organizationId, params = {}) {
  return request.get(`/organizations/${organizationId}/departments/public`, { params })
}

/**
 * 根据ID获取组织详情
 * @param {number} organizationId - 组织ID
 * @returns {Promise<Object>} 组织详情
 */
export function getOrganizationById(organizationId) {
  return request.get(`/organizations/${organizationId}`)
}

/**
 * 更新组织信息
 * @param {number} organizationId - 组织ID
 * @param {Object} organizationData - 更新的组织数据
 * @returns {Promise<Object>} 更新后的组织对象
 */
export function updateOrganization(organizationId, organizationData) {
  return request.put(`/organizations/${organizationId}`, organizationData)
}

/**
 * 删除组织
 * @param {number} organizationId - 组织ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteOrganization(organizationId) {
  return request.delete(`/organizations/${organizationId}`)
}

// ===== 组织成员管理API =====

/**
 * 添加组织成员
 * @param {number} organizationId - 组织ID
 * @param {Object} memberData - 成员数据
 * @param {number} memberData.user_id - 用户ID
 * @param {string} memberData.role - 成员角色（admin/member/viewer）
 * @param {number} memberData.department_id - 部门ID
 * @returns {Promise<Object>} 添加的成员对象
 */
export function addOrganizationMember(organizationId, memberData) {
  return request.post(`/organizations/${organizationId}/members`, memberData)
}

/**
 * 获取组织成员列表
 * @param {number} organizationId - 组织ID
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {string} params.role - 角色筛选
 * @param {number} params.department_id - 部门筛选
 * @returns {Promise<Array>} 成员列表
 */
export function getOrganizationMembers(organizationId, params = {}) {
  return request.get(`/organizations/${organizationId}/members`, { params })
}

/**
 * 获取单个组织成员信息
 * @param {number} organizationId - 组织ID
 * @param {number} memberId - 成员ID
 * @returns {Promise<Object>} 成员信息
 */
export function getOrganizationMember(organizationId, memberId) {
  return request.get(`/organizations/${organizationId}/members/${memberId}`)
}

/**
 * 更新组织成员信息
 * @param {number} organizationId - 组织ID
 * @param {number} memberId - 成员ID
 * @param {Object} memberData - 更新的成员数据
 * @returns {Promise<Object>} 更新后的成员对象
 */
export function updateOrganizationMember(organizationId, memberId, memberData) {
  return request.put(`/organizations/${organizationId}/members/${memberId}`, memberData)
}

/**
 * 移除组织成员
 * @param {number} organizationId - 组织ID
 * @param {number} memberId - 成员ID
 * @returns {Promise<Object>} 移除结果
 */
export function removeOrganizationMember(organizationId, memberId) {
  return request.delete(`/organizations/${organizationId}/members/${memberId}`)
}

// ===== 部门管理API =====

/**
 * 创建部门
 * @param {number} organizationId - 组织ID
 * @param {Object} departmentData - 部门数据
 * @param {string} departmentData.name - 部门名称
 * @param {string} departmentData.description - 部门描述
 * @param {number} departmentData.parent_id - 父部门ID
 * @returns {Promise<Object>} 创建的部门对象
 */
export function createDepartment(organizationId, departmentData) {
  return request.post(`/organizations/${organizationId}/departments`, departmentData)
}

/**
 * 获取部门列表
 * @param {number} organizationId - 组织ID
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {number} params.parent_id - 父部门筛选
 * @returns {Promise<Array>} 部门列表
 */
export function getDepartments(organizationId, params = {}) {
  return request.get(`/organizations/${organizationId}/departments`, { params })
}

/**
 * 更新部门信息
 * @param {number} organizationId - 组织ID
 * @param {number} departmentId - 部门ID
 * @param {Object} departmentData - 更新的部门数据
 * @returns {Promise<Object>} 更新后的部门对象
 */
export function updateDepartment(organizationId, departmentId, departmentData) {
  return request.put(`/organizations/${organizationId}/departments/${departmentId}`, departmentData)
}

/**
 * 删除部门
 * @param {number} organizationId - 组织ID
 * @param {number} departmentId - 部门ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteDepartment(organizationId, departmentId) {
  return request.delete(`/organizations/${organizationId}/departments/${departmentId}`)
}
