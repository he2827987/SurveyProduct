/**
 * @fileoverview API统一导出模块
 * @description 集中管理所有API调用函数，提供统一的导入接口
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

// ===== 导入所有API模块 =====

import * as userAPI from './user'
import * as surveyAPI from './survey'
import * as questionAPI from './question'
import * as answerAPI from './answer'
import * as organizationAPI from './organization'
import * as llmAPI from './llm'

// ===== 统一导出 =====

/**
 * 用户管理相关API
 * @type {Object}
 */
export { userAPI }

/**
 * 调研管理相关API
 * @type {Object}
 */
export { surveyAPI }

/**
 * 题目管理相关API
 * @type {Object}
 */
export { questionAPI }

/**
 * 答案管理相关API
 * @type {Object}
 */
export { answerAPI }

/**
 * 组织管理相关API
 * @type {Object}
 */
export { organizationAPI }

/**
 * 大语言模型相关API
 * @type {Object}
 */
export { llmAPI }

// ===== 默认导出 =====

/**
 * 默认导出对象，包含所有API模块
 * @type {Object}
 */
export default {
  user: userAPI,
  survey: surveyAPI,
  question: questionAPI,
  answer: answerAPI,
  organization: organizationAPI,
  llm: llmAPI
}
