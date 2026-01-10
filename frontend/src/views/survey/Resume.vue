<!-- survey/Resume.vue -->
<template>
    <div class="resume-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-loading-spinner />
        <p>正在验证身份...</p>
      </div>
  
      <!-- 身份验证 -->
      <div v-else-if="!verified" class="verify-section">
        <div class="verify-content">
          <h1 class="page-title">继续填写调研</h1>
          <p class="page-description">请输入您的姓名以继续之前中断的调研</p>
          
          <el-form 
            ref="verifyFormRef"
            :model="verifyForm"
            :rules="verifyRules"
            class="verify-form"
          >
            <el-form-item prop="name">
              <el-input 
                v-model="verifyForm.name"
                placeholder="请输入您的姓名"
                size="large"
                clearable
                @keyup.enter="verifyIdentity"
              />
            </el-form-item>
            
            <el-button 
              type="primary" 
              size="large"
              style="width: 100%"
              @click="verifyIdentity"
              :loading="verifying"
            >
              继续填写
            </el-button>
          </el-form>
          
          <div class="back-link">
            <el-link type="primary" @click="goBack">返回首页</el-link>
          </div>
        </div>
      </div>
  
      <!-- 调研列表 -->
      <div v-else class="survey-list-section">
        <div class="survey-list-content">
          <h1 class="page-title">您的调研记录</h1>
          <p class="page-description">请选择要继续的调研</p>
          
          <div class="survey-list">
            <div 
              v-for="survey in userSurveys"
              :key="survey.id"
              class="survey-item"
              @click="continueSurvey(survey)"
            >
              <div class="survey-info">
                <h3 class="survey-title">{{ survey.title }}</h3>
                <p class="survey-progress">
                  进度: {{ survey.progress }}% ({{ survey.answeredCount }}/{{ survey.totalQuestions }})
                </p>
                <p class="survey-time">
                  最后填写时间: {{ formatTime(survey.lastUpdateTime) }}
                </p>
              </div>
              <div class="survey-actions">
                <el-button type="primary" size="small">
                  继续填写
                </el-button>
              </div>
            </div>
          </div>
          
          <div v-if="userSurveys.length === 0" class="empty-state">
            <el-empty description="暂无未完成的调研">
              <el-button type="primary" @click="goBack">返回首页</el-button>
            </el-empty>
          </div>
          
          <div class="back-link">
            <el-link type="primary" @click="goBack">返回首页</el-link>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  
  // ===== 路由和基础状态 =====
  const router = useRouter()
  
  // ===== 加载状态 =====
  const loading = ref(false)
  const verifying = ref(false)
  const verified = ref(false)
  
  // ===== 验证表单 =====
  const verifyFormRef = ref(null)
  const verifyForm = ref({
    name: ''
  })
  
  const verifyRules = {
    name: [
      { required: true, message: '请输入姓名', trigger: 'blur' },
      { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
    ]
  }
  
  // ===== 用户调研列表 =====
  const userSurveys = ref([])
  
  // ===== 生命周期钩子 =====
  
  onMounted(() => {
    // 检查是否有保存的调研进度
    checkSavedSurveys()
  })
  
  // ===== 数据检查函数 =====
  
  /**
   * 检查本地保存的调研进度
   */
  const checkSavedSurveys = () => {
    const savedSurveys = []
    
    // 遍历localStorage查找保存的调研进度
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith('survey_progress_')) {
        try {
          const surveyId = key.replace('survey_progress_', '')
          const data = JSON.parse(localStorage.getItem(key))
          
          if (data && data.respondentInfo && data.respondentInfo.name) {
            savedSurveys.push({
              id: surveyId,
              name: data.respondentInfo.name,
              data: data
            })
          }
        } catch (error) {
          console.error('解析保存的调研数据失败:', error)
        }
      }
    }
    
    // 如果有保存的调研，直接显示列表
    if (savedSurveys.length > 0) {
      userSurveys.value = savedSurveys.map(survey => ({
        id: survey.id,
        title: `调研 #${survey.id}`,
        progress: calculateProgress(survey.data),
        answeredCount: Object.keys(survey.data.answers || {}).filter(key => {
          const answer = survey.data.answers[key]
          return answer !== null && answer !== undefined && answer !== ''
        }).length,
        totalQuestions: Object.keys(survey.data.answers || {}).length,
        lastUpdateTime: survey.data.timestamp || Date.now()
      }))
      verified.value = true
    }
  }
  
  /**
   * 计算调研进度
   */
  const calculateProgress = (data) => {
    if (!data.answers) return 0
    
    const totalQuestions = Object.keys(data.answers).length
    if (totalQuestions === 0) return 0
    
    const answeredCount = Object.keys(data.answers).filter(key => {
      const answer = data.answers[key]
      return answer !== null && answer !== undefined && answer !== ''
    }).length
    
    return Math.round((answeredCount / totalQuestions) * 100)
  }
  
  // ===== 事件处理函数 =====
  
  /**
   * 验证身份
   */
  const verifyIdentity = async () => {
    try {
      const valid = await verifyFormRef.value.validate()
      if (!valid) return
      
      verifying.value = true
      
      // 查找该用户的调研进度
      const userSurveys = []
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && key.startsWith('survey_progress_')) {
          try {
            const surveyId = key.replace('survey_progress_', '')
            const data = JSON.parse(localStorage.getItem(key))
            
            if (data && data.respondentInfo && data.respondentInfo.name === verifyForm.value.name) {
              userSurveys.push({
                id: surveyId,
                title: `调研 #${surveyId}`,
                progress: calculateProgress(data),
                answeredCount: Object.keys(data.answers || {}).filter(key => {
                  const answer = data.answers[key]
                  return answer !== null && answer !== undefined && answer !== ''
                }).length,
                totalQuestions: Object.keys(data.answers || {}).length,
                lastUpdateTime: data.timestamp || Date.now()
              })
            }
          } catch (error) {
            console.error('解析保存的调研数据失败:', error)
          }
        }
      }
      
      if (userSurveys.length > 0) {
        userSurveys.value = userSurveys
        verified.value = true
        ElMessage.success(`找到 ${userSurveys.length} 个未完成的调研`)
      } else {
        ElMessage.warning('未找到该姓名的调研记录')
      }
      
    } catch (error) {
      console.error('验证身份失败:', error)
      ElMessage.error('验证失败，请重试')
    } finally {
      verifying.value = false
    }
  }
  
  /**
   * 继续调研
   */
  const continueSurvey = (survey) => {
    router.push(`/survey/fill/${survey.id}`)
  }
  
  /**
   * 返回首页
   */
  const goBack = () => {
    router.push('/')
  }
  
  /**
   * 格式化时间
   */
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  </script>
  
  <style scoped>
  .resume-container {
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
  
  .verify-section,
  .survey-list-section {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
  
  .verify-content,
  .survey-list-content {
    text-align: center;
  }
  
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }
  
  .page-description {
    color: #606266;
    margin-bottom: 32px;
    line-height: 1.5;
  }
  
  .verify-form {
    max-width: 400px;
    margin: 0 auto 24px;
  }
  
  .survey-list {
    margin-bottom: 24px;
  }
  
  .survey-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s;
  }
  
  .survey-item:hover {
    border-color: #409EFF;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  }
  
  .survey-info {
    flex: 1;
    text-align: left;
  }
  
  .survey-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }
  
  .survey-progress {
    color: #409EFF;
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .survey-time {
    color: #909399;
    font-size: 12px;
  }
  
  .survey-actions {
    margin-left: 16px;
  }
  
  .empty-state {
    margin: 40px 0;
  }
  
  .back-link {
    margin-top: 24px;
  }
  
  /* 移动端适配 */
  @media (max-width: 768px) {
    .resume-container {
      padding: 16px;
    }
    
    .verify-section,
    .survey-list-section {
      padding: 24px;
    }
    
    .survey-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
    
    .survey-actions {
      margin-left: 0;
      width: 100%;
    }
    
    .survey-actions .el-button {
      width: 100%;
    }
  }
  </style>