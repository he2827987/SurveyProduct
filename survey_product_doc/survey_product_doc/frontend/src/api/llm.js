/**
 * @fileoverview 大语言模型API模块
 * @description 提供AI驱动的题目生成、答案分析、报告生成等功能的API调用
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

// ===== 题目生成API =====

/**
 * 基于主题生成调研题目
 * @param {Object} generationData - 生成参数
 * @param {string} generationData.topic - 调研主题
 * @param {number} generationData.question_count - 题目数量
 * @param {Array<string>} generationData.question_types - 题目类型列表
 * @param {string} generationData.target_audience - 目标受众
 * @returns {Promise<Array>} 生成的题目列表
 */
export function generateQuestions(generationData) {
  return request.post('/llm/generate-questions', generationData)
}

/**
 * 优化题目文本
 * @param {Object} optimizationData - 优化参数
 * @param {string} optimizationData.question_text - 原题目文本
 * @param {string} optimizationData.optimization_type - 优化类型（clarity/brevity/neutrality）
 * @returns {Promise<string>} 优化后的题目文本
 */
export function optimizeQuestionText(optimizationData) {
  return request.post('/llm/optimize-question', optimizationData)
}

/**
 * 生成题目建议
 * @param {Object} suggestionData - 建议参数
 * @param {string} suggestionData.survey_topic - 调研主题
 * @param {Array<Object>} suggestionData.existing_questions - 现有题目列表
 * @returns {Promise<Array>} 题目建议列表
 */
export function generateQuestionSuggestions(suggestionData) {
  return request.post('/llm/question-suggestions', suggestionData)
}

// ===== 答案分析API =====

/**
 * 总结调研答案
 * @param {Object} summaryData - 总结参数
 * @param {number} summaryData.survey_id - 调研ID
 * @param {Array<Object>} summaryData.answers - 答案数据
 * @param {string} summaryData.summary_type - 总结类型（overview/key_findings/trends）
 * @returns {Promise<Object>} 答案总结
 */
export function summarizeAnswers(summaryData) {
  return request.post('/llm/summarize-answers', summaryData)
}

/**
 * 生成调研洞察
 * @param {Object} insightData - 洞察参数
 * @param {number} insightData.survey_id - 调研ID
 * @param {Array<Object>} insightData.answers - 答案数据
 * @param {Array<string>} insightData.insight_types - 洞察类型列表
 * @returns {Promise<Array>} 洞察列表
 */
export function generateInsights(insightData) {
  return request.post('/llm/generate-insights', insightData)
}

/**
 * 分析调研数据
 * @param {Object} analysisData - 分析参数
 * @param {number} analysisData.survey_id - 调研ID
 * @param {Array<Object>} analysisData.answers - 答案数据
 * @param {string} analysisData.analysis_type - 分析类型（sentiment/trends/patterns）
 * @returns {Promise<Object>} 分析结果
 */
export function analyzeSurveyData(analysisData) {
  return request.post('/llm/analyze-data', analysisData)
}

// ===== 报告生成API =====

/**
 * 生成调研报告
 * @param {Object} reportData - 报告参数
 * @param {number} reportData.survey_id - 调研ID
 * @param {string} reportData.report_type - 报告类型（executive/detailed/visual）
 * @param {Object} reportData.options - 报告选项
 * @param {boolean} reportData.options.include_charts - 是否包含图表
 * @param {boolean} reportData.options.include_recommendations - 是否包含建议
 * @returns {Promise<Object>} 生成的报告
 */
export function generateSurveyReport(reportData) {
  return llmRequest.post('/llm/generate_survey_summary', reportData)
}

/**
 * 比较多个调研
 * @param {Object} comparisonData - 比较参数
 * @param {Array<number>} comparisonData.survey_ids - 调研ID列表
 * @param {string} comparisonData.comparison_type - 比较类型（performance/trends/patterns）
 * @returns {Promise<Object>} 比较结果
 */
export function compareSurveys(comparisonData) {
  return request.post('/llm/compare-surveys', comparisonData)
}
