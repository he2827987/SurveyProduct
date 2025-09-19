// frontend/src/api/usage-example.js
/**
 * API使用示例
 * 展示如何在Vue组件中使用各种API函数
 */

import { userAPI, surveyAPI, questionAPI, answerAPI, organizationAPI, llmAPI } from './index'

// ===== 用户相关API使用示例 =====

/**
 * 用户登录示例
 */
export async function loginExample() {
  try {
    const response = await userAPI.loginUser('user@example.com', 'password123')
    console.log('登录成功:', response)
    
    // 保存token到localStorage
    localStorage.setItem('access_token', response.access_token)
    
    return response
  } catch (error) {
    console.error('登录失败:', error)
    throw error
  }
}

/**
 * 获取当前用户信息示例
 */
export async function getCurrentUserExample() {
  try {
    const user = await userAPI.getCurrentUser()
    console.log('当前用户:', user)
    return user
  } catch (error) {
    console.error('获取用户信息失败:', error)
    throw error
  }
}

// ===== 问卷相关API使用示例 =====

/**
 * 创建问卷示例
 */
export async function createSurveyExample() {
  try {
    const surveyData = {
      title: '员工满意度调研',
      description: '了解员工对公司各方面的满意度',
      is_active: true
    }
    
    const survey = await surveyAPI.createSurvey(surveyData)
    console.log('问卷创建成功:', survey)
    return survey
  } catch (error) {
    console.error('创建问卷失败:', error)
    throw error
  }
}

/**
 * 获取问卷列表示例
 */
export async function getSurveysExample() {
  try {
    const params = {
      skip: 0,
      limit: 10,
      is_active: true
    }
    
    const surveys = await surveyAPI.getSurveys(params)
    console.log('问卷列表:', surveys)
    return surveys
  } catch (error) {
    console.error('获取问卷列表失败:', error)
    throw error
  }
}

// ===== 问题相关API使用示例 =====

/**
 * 创建全局问题示例
 */
export async function createQuestionExample() {
  try {
    const questionData = {
      text: '您对公司的工作环境满意吗？',
      type: 'single_choice',
      options: ['非常满意', '满意', '一般', '不满意', '非常不满意'],
      is_required: true
    }
    
    const question = await questionAPI.createGlobalQuestion(questionData)
    console.log('问题创建成功:', question)
    return question
  } catch (error) {
    console.error('创建问题失败:', error)
    throw error
  }
}

/**
 * 为问卷添加问题示例
 */
export async function addQuestionToSurveyExample(surveyId) {
  try {
    const questionData = {
      text: '您认为公司最需要改进的方面是什么？',
      type: 'text_input',
      is_required: false,
      order: 1
    }
    
    const question = await questionAPI.addQuestionToSurvey(surveyId, questionData)
    console.log('问题添加成功:', question)
    return question
  } catch (error) {
    console.error('添加问题失败:', error)
    throw error
  }
}

// ===== 答案相关API使用示例 =====

/**
 * 提交问卷答案示例
 */
export async function submitAnswerExample(surveyId) {
  try {
    const answerData = {
      respondent_name: '张三',
      department: '技术部',
      position: '软件工程师',
      answers: {
        '1': '满意',
        '2': '公司应该提供更多的培训机会'
      }
    }
    
    const answer = await answerAPI.submitSurveyAnswer(surveyId, answerData)
    console.log('答案提交成功:', answer)
    return answer
  } catch (error) {
    console.error('提交答案失败:', error)
    throw error
  }
}

/**
 * 获取问卷答案列表示例
 */
export async function getAnswersExample(surveyId) {
  try {
    const params = {
      skip: 0,
      limit: 50
    }
    
    const answers = await answerAPI.getSurveyAnswers(surveyId, params)
    console.log('答案列表:', answers)
    return answers
  } catch (error) {
    console.error('获取答案列表失败:', error)
    throw error
  }
}

// ===== 组织相关API使用示例 =====

/**
 * 获取组织列表示例
 */
export async function getOrganizationsExample() {
  try {
    const organizations = await organizationAPI.getOrganizations()
    console.log('组织列表:', organizations)
    return organizations
  } catch (error) {
    console.error('获取组织列表失败:', error)
    throw error
  }
}

/**
 * 添加组织成员示例
 */
export async function addMemberExample(orgId, userId) {
  try {
    const memberData = {
      user_id: userId,
      role: 'member'
    }
    
    const member = await organizationAPI.addOrganizationMember(orgId, memberData)
    console.log('成员添加成功:', member)
    return member
  } catch (error) {
    console.error('添加成员失败:', error)
    throw error
  }
}

// ===== 大模型相关API使用示例 =====

/**
 * 生成问题示例
 */
export async function generateQuestionsExample() {
  try {
    const response = await llmAPI.generateQuestions('员工满意度调研', 5)
    console.log('生成的问题:', response.questions)
    return response.questions
  } catch (error) {
    console.error('生成问题失败:', error)
    throw error
  }
}

/**
 * 总结答案示例
 */
export async function summarizeAnswersExample() {
  try {
    const questionText = '您对公司的工作环境满意吗？'
    const answers = [
      '非常满意，环境很好',
      '满意，但希望有更多休息区',
      '一般，需要改善',
      '不满意，太吵了',
      '非常满意，设施齐全'
    ]
    
    const summary = await llmAPI.summarizeAnswers(questionText, answers)
    console.log('答案总结:', summary.summary)
    return summary
  } catch (error) {
    console.error('总结答案失败:', error)
    throw error
  }
}

// ===== Vue组件中的使用示例 =====

/**
 * 在Vue组件中使用API的示例
 * 
 * <script setup>
 * import { ref, onMounted } from 'vue'
 * import { surveyAPI, questionAPI } from '@/api'
 * 
 * const surveys = ref([])
 * const loading = ref(false)
 * 
 * const fetchSurveys = async () => {
 *   loading.value = true
 *   try {
 *     surveys.value = await surveyAPI.getSurveys()
 *   } catch (error) {
 *     console.error('获取问卷失败:', error)
 *   } finally {
 *     loading.value = false
 *   }
 * }
 * 
 * const createSurvey = async (surveyData) => {
 *   try {
 *     const newSurvey = await surveyAPI.createSurvey(surveyData)
 *     surveys.value.push(newSurvey)
 *     return newSurvey
 *   } catch (error) {
 *     console.error('创建问卷失败:', error)
 *     throw error
 *   }
 * }
 * 
 * onMounted(() => {
 *   fetchSurveys()
 * })
 * </script>
 */
