/**
 * @fileoverview 数据分析API模块
 * @description 提供调研数据分析、统计、AI总结等功能的API调用
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import request from './request'
import axios from 'axios'

// 为LLM API创建专门的请求实例，使用更长的超时时间
const llmRequest = axios.create({
  baseURL: '/api/v1',
  timeout: 300000, // 5分钟超时，适合LLM API调用
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求拦截器
llmRequest.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  error => {
    console.error('LLM请求错误:', error);
    return Promise.reject(error);
  }
)

// 添加响应拦截器
llmRequest.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    console.error('LLM响应错误:', error);
    if (error.code === 'ECONNABORTED') {
      console.error('LLM请求超时');
    }
    return Promise.reject(error);
  }
)

// ===== 调研概览统计API =====

/**
 * 获取组织调研概览统计
 * @param {number} organizationId - 组织ID
 * @returns {Promise<Object>} 调研概览数据
 */
export function getSurveyOverview(organizationId) {
  return request.get(`/organizations/${organizationId}/analytics/overview`)
}

/**
 * 获取特定调研的详细分析（按维度统计）
 * @param {number} surveyId - 调研ID
 * @param {string} dimension - 统计维度，默认 department，可选 position
 * @returns {Promise<Object>} 调研详细分析数据
 */
export function getSurveyAnalytics(surveyId, dimension = 'department') {
  return request.get(`/analysis/survey/${surveyId}/stats`, { params: { dimension } })
}

/**
 * 获取调研AI分析总结
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} AI分析总结
 */
export function getSurveyAISummary(surveyId) {
  return request.get(`/analysis/survey/${surveyId}/ai-summary`)
}

/**
 * 按题目汇总总分/平均分，支持部门或职位过滤
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 过滤参数
 * @param {string} [params.department] - 部门名称
 * @param {string} [params.position] - 职务
 * @returns {Promise<Array>} 题目得分汇总
 */
export function getQuestionScores(surveyId, params = {}) {
  return request.get(`/analysis/survey/${surveyId}/questions/scores`, { params })
}

// ===== 趋势分析API =====

/**
 * 获取调研参与趋势
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 查询参数
 * @param {string} params.period - 时间周期 (daily, weekly, monthly)
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @returns {Promise<Object>} 参与趋势数据
 */
export function getParticipationTrend(organizationId, surveyId, params = {}) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/analytics/trend`, { params })
}

/**
 * 获取问题回答趋势
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {number} questionId - 问题ID
 * @returns {Promise<Object>} 问题回答趋势数据
 */
export function getQuestionTrend(organizationId, surveyId, questionId) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/questions/${questionId}/analytics/trend`)
}

// ===== 对比分析API =====

/**
 * 获取部门对比分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 部门对比数据
 */
export function getDepartmentComparison(organizationId, surveyId) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/analytics/department-comparison`)
}

/**
 * 获取职位对比分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 职位对比数据
 */
export function getPositionComparison(organizationId, surveyId) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/analytics/position-comparison`)
}

/**
 * 获取调研对比分析
 * @param {number} organizationId - 组织ID
 * @param {Array<number>} surveyIds - 调研ID列表
 * @returns {Promise<Object>} 调研对比数据
 */
export function getSurveyComparison(organizationId, surveyIds) {
  return request.post(`/organizations/${organizationId}/analytics/survey-comparison`, {
    survey_ids: surveyIds
  })
}

/**
 * 获取企业间对比分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Array<number>} compareOrganizations - 要对比的组织ID列表
 * @returns {Promise<Object>} 企业间对比数据
 */
export function getEnterpriseComparison(organizationId, surveyId, compareOrganizations) {
  const compareOrgString = compareOrganizations.join(',')
  return request.get(`/organizations/${organizationId}/analytics/enterprise-comparison`, {
    params: {
      survey_id: surveyId,
      compare_organizations: compareOrgString
    }
  })
}

/**
 * 获取全局企业间对比分析
 * @param {string} surveyTitle - 调研标题
 * @returns {Promise<Object>} 全局企业间对比数据
 */
export function getGlobalEnterpriseComparison(surveyTitle) {
  return request.get('/analytics/global-enterprise-comparison', {
    params: {
      survey_title: surveyTitle
    }
  })
}

// ===== 详细数据API =====

/**
 * 获取调研详细数据
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {string} params.department - 按部门筛选
 * @param {string} params.position - 按职位筛选
 * @returns {Promise<Object>} 详细数据
 */
export function getSurveyDetailedData(organizationId, surveyId, params = {}) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/analytics/detailed-data`, { params })
}

/**
 * 导出调研数据
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 导出参数
 * @param {string} params.format - 导出格式 (csv, excel)
 * @param {Array<string>} params.fields - 导出字段
 * @returns {Promise<Blob>} 导出的文件
 */
export function exportSurveyData(organizationId, surveyId, params = {}) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/analytics/export`, {
    params,
    responseType: 'blob'
  })
}

// ===== 实时统计API =====

/**
 * 获取实时参与统计
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @returns {Promise<Object>} 实时统计数据
 */
export function getRealTimeStats(organizationId, surveyId) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/analytics/realtime`)
}

/**
 * 获取实时问题回答统计
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {number} questionId - 问题ID
 * @returns {Promise<Object>} 实时问题统计数据
 */
export function getRealTimeQuestionStats(organizationId, surveyId, questionId) {
  return request.get(`/organizations/${organizationId}/surveys/${surveyId}/questions/${questionId}/analytics/realtime`)
}

// ===== 高级分析API =====

/**
 * 获取相关性分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Array<number>} questionIds - 问题ID列表
 * @returns {Promise<Object>} 相关性分析数据
 */
export function getCorrelationAnalysis(organizationId, surveyId, questionIds) {
  return request.post(`/organizations/${organizationId}/surveys/${surveyId}/analytics/correlation`, {
    question_ids: questionIds
  })
}

/**
 * 获取聚类分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 聚类参数
 * @param {number} params.clusters - 聚类数量
 * @param {Array<string>} params.features - 特征字段
 * @returns {Promise<Object>} 聚类分析数据
 */
export function getClusterAnalysis(organizationId, surveyId, params = {}) {
  return request.post(`/organizations/${organizationId}/surveys/${surveyId}/analytics/clustering`, params)
}

/**
 * 获取预测分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 预测参数
 * @param {string} params.target - 预测目标
 * @param {Array<string>} params.features - 特征字段
 * @returns {Promise<Object>} 预测分析数据
 */
export function getPredictionAnalysis(organizationId, surveyId, params = {}) {
  return request.post(`/organizations/${organizationId}/surveys/${surveyId}/analytics/prediction`, params)
}

// ===== 企业对比AI分析API =====

/**
 * 生成企业对比AI分析
 * @param {number} organizationId - 组织ID
 * @param {number} surveyId - 调研ID
 * @param {Object} comparisonData - 对比数据
 * @param {string} comparisonData.dimension - 对比维度
 * @param {Array} comparisonData.companies - 企业列表
 * @param {Array} comparisonData.comparison_data - 对比数据
 * @returns {Promise<Object>} AI分析结果
 */
export function generateEnterpriseComparisonAI(organizationId, surveyId, comparisonData) {
  return llmRequest.post(`/organizations/${organizationId}/surveys/${surveyId}/analytics/enterprise-comparison-ai`, comparisonData)
}

export function getLineScores(surveyId, params = {}) {
  return request.get(`/analysis/survey/${surveyId}/line`, { params })
}

export function getPieOptionDistribution(surveyId, params = {}) {
  return request.get(`/analysis/survey/${surveyId}/pie`, { params })
}
