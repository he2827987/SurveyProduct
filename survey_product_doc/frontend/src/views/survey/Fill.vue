<!-- survey/Fill.vue -->
<template>
  <div class="survey-fill-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-loading-spinner />
      <p>正在加载调研内容...</p>
    </div>

    <!-- 调研内容 -->
    <div v-else class="survey-content">
      <!-- 调研头部信息 -->
      <div class="survey-header">
        <h1 class="survey-title">{{ surveyInfo.title }}</h1>
        <p class="survey-description">{{ surveyInfo.description }}</p>
        <div class="survey-meta">
          <span class="question-count">共 {{ questions.length }} 题</span>
          <span class="estimated-time">预计用时 {{ estimatedTime }} 分钟</span>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-info">
          <span>填写进度</span>
          <span>{{ answeredCount }}/{{ questions.length }}</span>
        </div>
        <el-progress 
          :percentage="progressPercentage" 
          :stroke-width="8"
          color="#409EFF"
        />
      </div>

      <!-- 受访者信息填写 -->
      <div v-if="!respondentInfo.completed" class="respondent-section">
        <h2 class="section-title">请填写您的信息</h2>
        <el-form 
          ref="respondentFormRef"
          :model="respondentInfo"
          :rules="respondentRules"
          label-position="top"
          class="respondent-form"
        >
          <el-form-item label="姓名" prop="name">
            <el-input 
              v-model="respondentInfo.name"
              placeholder="请输入您的姓名"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="部门" prop="department">
            <el-select 
              v-model="respondentInfo.department"
              placeholder="请选择您的部门"
              style="width: 100%"
              clearable
            >
              <el-option 
                v-for="dept in departments"
                :key="dept.id"
                :label="dept.name"
                :value="dept.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="职位" prop="position">
            <el-select 
              v-model="respondentInfo.position"
              placeholder="请选择您的职位"
              style="width: 100%"
              clearable
            >
              <el-option 
                v-for="pos in positions"
                :key="pos.value"
                :label="pos.label"
                :value="pos.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="所属组织" prop="organizationId">
            <el-collapse v-model="orgCollapse" accordion>
              <el-collapse-item title="展开/选择所属组织" name="org">
                <el-select
                  v-model="respondentInfo.organizationId"
                  placeholder="请选择组织（默认使用用户作为组织）"
                  style="width: 100%"
                  filterable
                  clearable
                >
                  <el-option
                    v-for="org in organizations"
                    :key="org.id"
                    :label="org.name"
                    :value="org.id"
                  />
                </el-select>
              </el-collapse-item>
            </el-collapse>
          </el-form-item>
          
          <el-button 
            type="primary" 
            size="large"
            style="width: 100%"
            @click="startSurvey"
            :loading="starting"
          >
            开始填写
          </el-button>
        </el-form>
      </div>

      <!-- 问题填写区域 -->
      <div v-else class="questions-section">
        <!-- 问题导航 -->
        <div class="question-nav">
          <el-button 
            :disabled="currentQuestionIndex === 0"
            @click="previousQuestion"
            size="small"
          >
            上一题
          </el-button>
          
          <span class="question-counter">
            {{ currentQuestionIndex + 1 }} / {{ questions.length }}
          </span>
          
          <el-button 
            :disabled="currentQuestionIndex === questions.length - 1"
            @click="nextQuestion"
            size="small"
          >
            下一题
          </el-button>
        </div>

        <!-- 当前问题 -->
        <div class="current-question">
          <div class="question-header">
            <span class="question-number">Q{{ currentQuestionIndex + 1 }}</span>
            <span v-if="currentQuestion.is_required" class="required-mark">*</span>
          </div>
          
          <h3 class="question-text">{{ currentQuestion.text }}</h3>
          
          <!-- 单选题 -->
          <div v-if="currentQuestion.type === 'single_choice'" class="question-options">
            <el-radio-group v-model="answers[currentQuestion.id]">
              <el-radio 
                v-for="option in currentQuestion.options"
                :key="option"
                :label="option"
                class="option-item"
              >
                {{ option }}
              </el-radio>
            </el-radio-group>
          </div>
          
          <!-- 多选题 -->
          <div v-else-if="currentQuestion.type === 'multi_choice'" class="question-options">
            <el-checkbox-group v-model="answers[currentQuestion.id]">
              <el-checkbox 
                v-for="option in currentQuestion.options"
                :key="option"
                :label="option"
                class="option-item"
              >
                {{ option }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
          
          <!-- 文本输入 -->
          <div v-else-if="currentQuestion.type === 'text_input'" class="question-input">
            <el-input
              v-model="answers[currentQuestion.id]"
              type="textarea"
              :rows="4"
              placeholder="请输入您的答案"
              :maxlength="500"
              show-word-limit
            />
          </div>
          
          <!-- 数字输入 -->
          <div v-else-if="currentQuestion.type === 'number_input'" class="question-input">
            <el-input-number
              v-model="answers[currentQuestion.id]"
              :min="0"
              :max="999999"
              placeholder="请输入数字"
              style="width: 100%"
            />
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="question-actions">
          <el-button 
            v-if="currentQuestionIndex > 0"
            @click="previousQuestion"
            size="large"
          >
            上一题
          </el-button>
          
          <el-button 
            v-if="currentQuestionIndex < questions.length - 1"
            type="primary"
            @click="nextQuestion"
            size="large"
            :disabled="!isCurrentQuestionAnswered"
          >
            下一题
          </el-button>
          
          <el-button 
            v-if="currentQuestionIndex === questions.length - 1"
            type="success"
            @click="submitSurvey"
            size="large"
            :loading="submitting"
            :disabled="!isAllQuestionsAnswered"
          >
            提交调研
          </el-button>
        </div>

        <!-- 保存提示 -->
        <div class="save-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>您的答案已自动保存，可随时中断后继续填写</span>
        </div>
      </div>
    </div>

    <!-- 提交成功对话框 -->
    <el-dialog
      v-model="submitSuccess"
      title="提交成功"
      width="300px"
      :show-close="false"
      :close-on-click-modal="false"
      center
    >
      <div class="success-content">
        <el-icon class="success-icon" color="#67C23A"><CircleCheckFilled /></el-icon>
        <p>感谢您的参与！</p>
        <p>调研已成功提交</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="closeSurvey">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import * as surveyAPI from '@/api/survey'
import * as answerAPI from '@/api/answer'
import * as userAPI from '@/api/user'

// ===== 路由和基础状态 =====
const route = useRoute()
const router = useRouter()
const surveyId = computed(() => route.params.id)

// ===== 加载状态 =====
const loading = ref(true)
const starting = ref(false)
const submitting = ref(false)

// ===== 调研信息 =====
const surveyInfo = ref({
  title: '',
  description: '',
  id: null
})

const questions = ref([])
const estimatedTime = computed(() => Math.ceil(questions.value.length * 1.5))

// ===== 受访者信息 =====
const respondentFormRef = ref(null)
const respondentInfo = ref({
  name: '',
  department: null,
  position: null,
  organizationId: null,
  organizationName: '',
  completed: false
})
const orgCollapse = ref(['org'])

const respondentRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  position: [
    { required: true, message: '请选择职位', trigger: 'change' }
  ],
  organizationId: [
    { required: true, message: '请选择所属组织', trigger: 'change' }
  ]
}

// ===== 部门职位数据 =====
const departments = ref([
  { id: 1, name: '技术部' },
  { id: 2, name: '产品部' },
  { id: 3, name: '运营部' },
  { id: 4, name: '市场部' },
  { id: 5, name: '人事部' },
  { id: 6, name: '财务部' }
])

// ===== 组织列表（使用用户列表作为组织）
const organizations = ref([])

const positions = ref([
  { value: 'executive', label: '高管' },
  { value: 'manager', label: '经理/主管' },
  { value: 'senior', label: '高级员工' },
  { value: 'junior', label: '初级员工' },
  { value: 'intern', label: '实习生' }
])

// ===== 问题填写状态 =====
const currentQuestionIndex = ref(0)
const answers = ref({})

const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value] || {}
})

const answeredCount = computed(() => {
  return Object.keys(answers.value).filter(key => {
    const answer = answers.value[key]
    return answer !== null && answer !== undefined && answer !== ''
  }).length
})

const progressPercentage = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((answeredCount.value / questions.value.length) * 100)
})

watch(
  () => respondentInfo.value.organizationId,
  (val) => {
    const org = organizations.value.find((o) => o.id === val)
    respondentInfo.value.organizationName = org?.name || ''
  }
)

const isCurrentQuestionAnswered = computed(() => {
  const question = currentQuestion.value
  const answer = answers.value[question.id]
  
  if (!question.is_required) return true
  
  if (question.type === 'multi_choice') {
    return Array.isArray(answer) && answer.length > 0
  }
  
  return answer !== null && answer !== undefined && answer !== ''
})

const isAllQuestionsAnswered = computed(() => {
  return questions.value.every(question => {
    if (!question.is_required) return true
    
    const answer = answers.value[question.id]
    if (question.type === 'multi_choice') {
      return Array.isArray(answer) && answer.length > 0
    }
    
    return answer !== null && answer !== undefined && answer !== ''
  })
})

// ===== 提交状态 =====
const submitSuccess = ref(false)

// ===== 自动保存定时器 =====
let autoSaveTimer = null

// ===== 生命周期钩子 =====

onMounted(() => {
  loadOrganizations()
  loadSurveyData()
  setupAutoSave()
})

onBeforeUnmount(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})

// ===== 数据加载函数 =====

/**
 * 加载组织（使用用户列表代替）
 */
const loadOrganizations = async () => {
  try {
    const res = await userAPI.getUsers({ skip: 0, limit: 200 })
    const items = res?.items || res || []
    organizations.value = items.map((u) => ({
      id: u.id,
      name: u.username || u.email || `用户${u.id}`
    }))
  } catch (err) {
    console.error('加载组织列表失败', err)
    organizations.value = []
  }
}

/**
 * 加载调研数据
 */
const loadSurveyData = async () => {
  try {
    loading.value = true
    
    // 获取调研基本信息
    const surveyResponse = await surveyAPI.getSurveyForFilling(surveyId.value)
    surveyInfo.value = {
      id: surveyResponse.id,
      title: surveyResponse.title,
      description: surveyResponse.description || '',
      organization_id: surveyResponse.organization_id || null
    }
    
    // 获取调研问题
    const questionsResponse = await surveyAPI.getSurveyQuestions(surveyId.value)
    questions.value = questionsResponse || []
    
    // 初始化答案对象
    questions.value.forEach(question => {
      if (question.type === 'multi_choice') {
        answers.value[question.id] = []
      } else {
        answers.value[question.id] = null
      }
    })
    
    // 尝试恢复保存的进度
    await restoreProgress()
    
  } catch (error) {
    console.error('加载调研数据失败:', error)
    ElMessage.error('加载调研数据失败，请检查链接是否正确')
  } finally {
    loading.value = false
  }
}

/**
 * 恢复保存的进度
 */
const restoreProgress = async () => {
  const savedData = localStorage.getItem(`survey_progress_${surveyId.value}`)
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      if (data.respondentInfo) {
        respondentInfo.value = { ...respondentInfo.value, ...data.respondentInfo }
      }
      if (data.answers) {
        answers.value = { ...answers.value, ...data.answers }
      }
      if (data.currentQuestionIndex !== undefined) {
        currentQuestionIndex.value = data.currentQuestionIndex
      }
    } catch (error) {
      console.error('恢复进度失败:', error)
    }
  }
}

// ===== 自动保存功能 =====

/**
 * 设置自动保存
 */
const setupAutoSave = () => {
  autoSaveTimer = setInterval(() => {
    if (respondentInfo.value.completed) {
      saveProgress()
    }
  }, 30000) // 每30秒自动保存一次
}

/**
 * 保存进度
 */
const saveProgress = () => {
  const progressData = {
    respondentInfo: {
      name: respondentInfo.value.name,
      department: respondentInfo.value.department,
      position: respondentInfo.value.position,
      completed: respondentInfo.value.completed
    },
    answers: answers.value,
    currentQuestionIndex: currentQuestionIndex.value,
    timestamp: Date.now()
  }
  
  localStorage.setItem(`survey_progress_${surveyId.value}`, JSON.stringify(progressData))
}

// ===== 事件处理函数 =====

/**
 * 开始调研
 */
const startSurvey = async () => {
  try {
    const valid = await respondentFormRef.value.validate()
    if (!valid) return
    
    starting.value = true
    respondentInfo.value.completed = true
    saveProgress()
    
    ElMessage.success('开始填写调研')
  } catch (error) {
    console.error('开始调研失败:', error)
    ElMessage.error('开始调研失败')
  } finally {
    starting.value = false
  }
}

/**
 * 上一题
 */
const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    saveProgress()
  }
}

/**
 * 下一题
 */
const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    saveProgress()
  }
}

/**
 * 提交调研
 */
const submitSurvey = async () => {
  try {
    // 确认提交
    await ElMessageBox.confirm(
      '确定要提交调研吗？提交后将无法修改答案。',
      '确认提交',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '继续填写',
        type: 'warning'
      }
    )
    
    submitting.value = true
    
    // 准备提交数据
    const selectedOrg = organizations.value.find(org => org.id === respondentInfo.value.organizationId)
    const submitData = {
      respondent_name: respondentInfo.value.name,
      department: departments.value.find(d => d.id === respondentInfo.value.department)?.name || '',
      position: positions.value.find(p => p.value === respondentInfo.value.position)?.label || '',
      department_id: respondentInfo.value.department,
      organization_id: respondentInfo.value.organizationId || surveyInfo.value.organization_id,
      organization_name: respondentInfo.value.organizationName || selectedOrg?.name || '',
      answers: answers.value
    }
    
    // 提交答案
    await answerAPI.submitSurveyAnswer(surveyId.value, submitData)
    
    // 清除本地保存的进度
    localStorage.removeItem(`survey_progress_${surveyId.value}`)
    
    // 显示成功对话框
    submitSuccess.value = true
    
    ElMessage.success('调研提交成功！')
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交调研失败:', error)
      ElMessage.error('提交失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

/**
 * 关闭调研
 */
const closeSurvey = () => {
  submitSuccess.value = false
  router.push('/')
}
</script>

<style scoped>
.survey-fill-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: #909399;
}

.survey-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.survey-header {
  text-align: center;
  margin-bottom: 24px;
}

.survey-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.survey-description {
  color: #606266;
  margin-bottom: 16px;
  line-height: 1.5;
}

.survey-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  color: #909399;
  font-size: 14px;
}

.progress-section {
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.respondent-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.respondent-form {
  max-width: 400px;
  margin: 0 auto;
}

.questions-section {
  margin-bottom: 24px;
}

.question-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.question-counter {
  font-weight: 600;
  color: #409EFF;
}

.current-question {
  margin-bottom: 24px;
}

.question-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  background: #409EFF;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-right: 8px;
}

.required-mark {
  color: #f56c6c;
  font-size: 16px;
  margin-left: 4px;
}

.question-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
  line-height: 1.5;
}

.question-options {
  margin-bottom: 16px;
}

.option-item {
  display: block;
  margin-bottom: 12px;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
}

.option-item:hover {
  border-color: #409EFF;
  background: #f0f9ff;
}

.question-input {
  margin-bottom: 16px;
}

.question-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.question-actions .el-button {
  flex: 1;
}

.save-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 8px;
  color: #409EFF;
  font-size: 14px;
}

.success-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .survey-fill-container {
    padding: 16px;
  }
  
  .survey-content {
    padding: 20px;
  }
  
  .survey-title {
    font-size: 20px;
  }
  
  .question-actions {
    flex-direction: column;
  }
  
  .question-actions .el-button {
    width: 100%;
  }
}
</style>
