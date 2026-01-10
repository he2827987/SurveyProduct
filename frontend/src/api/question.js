/**
 * @fileoverview 题目管理API模块
 * @description 提供题目创建、查询、更新、删除、分类管理等功能的API调用
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import request from './request'

// ===== 全局题目管理API =====

/**
 * 获取全局题库题目列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @param {string} params.type - 题目类型筛选
 * @param {number} params.category_id - 分类ID筛选
 * @returns {Promise<Array>} 题目列表
 */
export function getGlobalQuestions(params = {}) {
  return request.get('/questions/', { params })
}

/**
 * 根据ID获取单个题目详情
 * @param {number} questionId - 题目ID
 * @returns {Promise<Object>} 题目详情
 */
export function getQuestionById(questionId) {
  return request.get(`/questions/${questionId}`)
}

/**
 * 创建全局题目
 * @param {Object} questionData - 题目数据
 * @param {string} questionData.title - 题目标题
 * @param {string} questionData.type - 题目类型（single/multiple/text/number）
 * @param {Array<string>} questionData.options - 选项列表（单选/多选题）
 * @param {boolean} questionData.is_required - 是否必答
 * @param {string} questionData.hint - 题目提示
 * @returns {Promise<Object>} 创建的题目对象
 */
export function createGlobalQuestion(questionData) {
  return request.post('/questions/', questionData)
}

/**
 * 更新题目信息
 * @param {number} questionId - 题目ID
 * @param {Object} questionData - 更新的题目数据
 * @returns {Promise<Object>} 更新后的题目对象
 */
export function updateQuestion(questionId, questionData) {
  return request.put(`/questions/${questionId}`, questionData)
}

/**
 * 删除题目
 * @param {number} questionId - 题目ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteQuestion(questionId) {
  return request.delete(`/questions/${questionId}`)
}

// ===== 调研内题目管理API =====

/**
 * 为调研添加题目
 * @param {number} surveyId - 调研ID
 * @param {Object} questionData - 题目数据
 * @returns {Promise<Object>} 添加的题目对象
 */
export function addQuestionToSurvey(surveyId, questionData) {
  return request.post(`/surveys/${surveyId}/questions/`, questionData)
}

/**
 * 获取调研的所有题目
 * @param {number} surveyId - 调研ID
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 调研题目列表
 */
export function getSurveyQuestions(surveyId, params = {}) {
  return request.get(`/surveys/${surveyId}/questions/`, { params })
}

/**
 * 更新调研内的题目
 * @param {number} surveyId - 调研ID
 * @param {number} questionId - 题目ID
 * @param {Object} questionData - 更新的题目数据
 * @returns {Promise<Object>} 更新后的题目对象
 */
export function updateSurveyQuestion(surveyId, questionId, questionData) {
  return request.put(`/surveys/${surveyId}/questions/${questionId}`, questionData)
}

/**
 * 删除调研内的题目
 * @param {number} surveyId - 调研ID
 * @param {number} questionId - 题目ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteSurveyQuestion(surveyId, questionId) {
  return request.delete(`/surveys/${surveyId}/questions/${questionId}`)
}

/**
 * 重新排序调研题目
 * @param {number} surveyId - 调研ID
 * @param {Array<number>} questionIds - 题目ID排序列表
 * @returns {Promise<Object>} 排序结果
 */
export function reorderQuestions(surveyId, questionIds) {
  return request.put(`/surveys/${surveyId}/questions/reorder`, { question_ids: questionIds })
}

// ===== 题目分类管理API =====

/**
 * 获取题目分类列表
 * @param {Object} params - 查询参数
 * @param {number} params.organization_id - 组织ID，为空表示获取全局分类
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 分类列表
 */
export function getQuestionCategories(params = {}) {
  return request.get('/categories', { params })
}

/**
 * 获取题目分类树结构
 * @param {Object} params - 查询参数
 * @param {number} params.organization_id - 组织ID，为空表示获取全局分类树
 * @returns {Promise<Array>} 分类树列表
 */
export function getQuestionCategoryTree(params = {}) {
  return request.get('/categories/tree', { params })
}

/**
 * 获取分类详情
 * @param {number} categoryId - 分类ID
 * @returns {Promise<Object>} 分类详情
 */
export function getQuestionCategoryDetail(categoryId) {
  return request.get(`/categories/${categoryId}`)
}

/**
 * 创建题目分类
 * @param {Object} categoryData - 分类数据
 * @param {string} categoryData.name - 分类名称
 * @param {string} categoryData.description - 分类描述
 * @param {string} categoryData.code - 分类编码
 * @param {number} categoryData.parent_id - 父分类ID
 * @param {number} categoryData.organization_id - 组织ID
 * @param {number} categoryData.sort_order - 排序字段
 * @param {boolean} categoryData.is_active - 是否激活
 * @returns {Promise<Object>} 创建的分类对象
 */
export function createQuestionCategory(categoryData) {
  return request.post('/categories', categoryData)
}

/**
 * 更新题目分类
 * @param {number} categoryId - 分类ID
 * @param {Object} categoryData - 更新的分类数据
 * @returns {Promise<Object>} 更新后的分类对象
 */
export function updateQuestionCategory(categoryId, categoryData) {
  return request.put(`/categories/${categoryId}`, categoryData)
}

/**
 * 删除题目分类
 * @param {number} categoryId - 分类ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteQuestionCategory(categoryId) {
  return request.delete(`/categories/${categoryId}`)
}

/**
 * 移动分类
 * @param {number} categoryId - 要移动的分类ID
 * @param {Object} moveData - 移动数据
 * @param {number} moveData.target_parent_id - 目标父分类ID
 * @param {number} moveData.position - 在同级中的位置
 * @returns {Promise<Object>} 移动结果
 */
export function moveQuestionCategory(categoryId, moveData) {
  return request.post(`/categories/${categoryId}/move`, moveData)
}

/**
 * 获取分类的子分类列表
 * @param {number} categoryId - 分类ID
 * @returns {Promise<Array>} 子分类列表
 */
export function getQuestionCategoryChildren(categoryId) {
  return request.get(`/categories/${categoryId}/children`)
}

// ===== 题目标签管理API =====

/**
 * 获取题目标签列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过的记录数
 * @param {number} params.limit - 返回的最大记录数
 * @returns {Promise<Array>} 标签列表
 */
export function getQuestionTags(params = {}) {
  return request.get('/question-tags/', { params })
}

/**
 * 创建题目标签
 * @param {Object} tagData - 标签数据
 * @param {string} tagData.name - 标签名称
 * @param {string} tagData.color - 标签颜色
 * @returns {Promise<Object>} 创建的标签对象
 */
export function createQuestionTag(tagData) {
  return request.post('/question-tags/', tagData)
}

/**
 * 删除题目标签
 * @param {number} tagId - 标签ID
 * @returns {Promise<Object>} 删除结果
 */
export function deleteQuestionTag(tagId) {
  return request.delete(`/question-tags/${tagId}`)
}

