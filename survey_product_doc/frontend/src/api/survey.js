/**
 * @fileoverview 调研管理API模块
 * @description 提供调研创建、查询、更新、删除、发布等功能的API调用
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import request from './request'

// ===== 调研基础管理API =====

/**
 * 获取当前用户创建的所有调研列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 调研列表
 */
export function getSurveys(params = {}) {
  return request.get('/surveys/', { params })
}

/**
 * 获取全局调研库中的所有调研
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status_filter - 状态筛选
 * @param {string} params.sort_by - 排序方式
 * @returns {Promise<Array>} 调研列表
 */
export function getGlobalSurveys(params = {}) {
  return request.get('/surveys/global/all', { params })
}

/**
 * 根据ID获取单个调研详情
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 调研详情
 */
export function getSurveyById(surveyId) {
  return request.get(`/surveys/${surveyId}`)
}

/**
 * 根据ID获取调研详情（公开访问，包含题目）
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 调研详情（包含题目列表）
 */
export function getSurveyDetail(surveyId) {
  return request.get(`/surveys/${surveyId}/detail`)
}

/**
 * 创建新的调研
 * @param {Object} surveyData - 调研数据
 * @param {string} surveyData.title - 调研标题
 * @param {string} surveyData.description - 调研描述
 * @param {Array<number>} surveyData.question_ids - 题目ID列表
 * @returns {Promise<Object>} 创建的调研对象
 */
export function createSurvey(surveyData) {
  return request.post('/surveys/', surveyData)
}

/**
 * 更新调研信息
 * @param {number} surveyId - 要更新的调研ID
 * @param {Object} surveyData - 更新的数据
 * @returns {Promise<Object>} 更新后的调研对象
 */
export function updateSurvey(surveyId, surveyData) {
  return request.put(`/surveys/${surveyId}`, surveyData)
}

/**
 * 删除调研
 * @param {number} surveyId - 要删除的调研ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteSurvey(surveyId) {
  return request.delete(`/surveys/${surveyId}`)
}

// ===== 调研状态管理API =====

/**
 * 发布调研
 * @param {number} surveyId - 要发布的调研ID
 * @returns {Promise<Object>} 发布结果
 */
export function publishSurvey(surveyId) {
  return request.post(`/surveys/${surveyId}/publish`)
}

/**
 * 取消发布调研
 * @param {number} surveyId - 要取消发布的调研ID
 * @returns {Promise<Object>} 取消发布结果
 */
export function unpublishSurvey(surveyId) {
  return request.post(`/surveys/${surveyId}/unpublish`)
}

// ===== 调研填写相关API =====

/**
 * 获取用于填写的调研内容（公开信息）
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 调研填写内容
 */
export function getSurveyForFilling(surveyId) {
  return request.get(`/surveys/${surveyId}/fill`)
}

/**
 * 获取调研的题目列表（用于填写）
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Array>} 题目列表
 */
export function getSurveyQuestions(surveyId) {
  return request.get(`/surveys/${surveyId}/questions`)
}

/**
 * 提交调研答卷
 * @param {number} surveyId - 调研ID
 * @param {Object} responseData - 答卷数据
 * @param {string} responseData.respondent_name - 受访者姓名
 * @param {string} responseData.respondent_department - 受访者部门
 * @param {string} responseData.respondent_position - 受访者职位
 * @param {Array<Object>} responseData.answers - 答案列表
 * @returns {Promise<Object>} 提交的答卷对象
 */
export function submitSurveyResponse(surveyId, responseData) {
  return request.post(`/surveys/${surveyId}/responses`, responseData)
}

/**
 * 获取某个调研的所有答卷（给调研创建者）
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 答卷列表
 */
export function getSurveyResponses(surveyId, params = {}) {
  return request.get(`/surveys/${surveyId}/responses`, { params })
}

// ===== 调研统计和分析API =====

/**
 * 获取调研统计信息
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 调研统计数据
 */
export function getSurveyStatistics(surveyId) {
  return request.get(`/surveys/${surveyId}/statistics`)
}

/**
 * 生成调研二维码
 * @param {number} surveyId - 调研ID
 * @param {Object} qrOptions - 二维码选项
 * @param {number} qrOptions.width - 二维码宽度
 * @param {number} qrOptions.height - 二维码高度
 * @returns {Promise<string>} 二维码图片URL
 */
export function generateSurveyQRCode(surveyId, qrOptions = {}) {
  return request.post(`/surveys/${surveyId}/qrcode`, qrOptions)
}

/**
 * 复制调研
 * @param {number} surveyId - 要复制的调研ID
 * @param {Object} copyData - 复制选项
 * @param {string} copyData.title - 新调研标题
 * @param {boolean} copyData.include_responses - 是否包含答卷数据
 * @returns {Promise<Object>} 复制的调研对象
 */
export function copySurvey(surveyId, copyData) {
  return request.post(`/surveys/${surveyId}/copy`, copyData)
}
