/**
 * @fileoverview 答案管理API模块
 * @description 提供调研答案提交、查询、统计、导出等功能的API调用
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import request from './request'

// ===== 答案提交和查询API =====

/**
 * 提交调研答案
 * @param {number} surveyId - 调研ID
 * @param {Object} answerData - 答案数据
 * @param {string} answerData.respondent_name - 受访者姓名
 * @param {string} answerData.respondent_department - 受访者部门
 * @param {string} answerData.respondent_position - 受访者职位
 * @param {Array<Object>} answerData.answers - 答案列表
 * @returns {Promise<Object>} 提交的答案对象
 */
export function submitSurveyAnswer(surveyId, answerData) {
  return request.post(`/surveys/${surveyId}/answers/`, answerData)
}

/**
 * 获取调研的所有答案
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {string} params.respondent_name - 受访者姓名筛选
 * @param {string} params.department - 部门筛选
 * @returns {Promise<Array>} 答案列表
 */
export function getSurveyAnswers(surveyId, params = {}) {
  return request.get(`/surveys/${surveyId}/answers`, { params })
}

/**
 * 获取单个答案详情
 * @param {number} surveyId - 调研ID
 * @param {number} answerId - 答案ID
 * @returns {Promise<Object>} 答案详情
 */
export function getSingleAnswer(surveyId, answerId) {
  return request.get(`/surveys/${surveyId}/answers/${answerId}`)
}

// ===== 答案统计和分析API =====

/**
 * 获取调研答案统计信息
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 统计参数
 * @param {string} params.group_by - 分组方式（question/department/date）
 * @returns {Promise<Object>} 统计数据
 */
export function getAnswerStatistics(surveyId, params = {}) {
  return request.get(`/surveys/${surveyId}/answers/statistics`, { params })
}

// ===== 答案导出API =====

/**
 * 导出调研答案
 * @param {number} surveyId - 调研ID
 * @param {Object} exportOptions - 导出选项
 * @param {string} exportOptions.format - 导出格式（excel/csv/json）
 * @param {Array<string>} exportOptions.fields - 导出字段
 * @param {Object} exportOptions.filters - 筛选条件
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportAnswers(surveyId, exportOptions = {}) {
  return request.post(`/surveys/${surveyId}/answers/export`, exportOptions, {
    responseType: 'blob'
  })
}
