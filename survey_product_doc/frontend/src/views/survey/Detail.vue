<template>
  <div class="survey-detail-container page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft" text>返回</el-button>
        <h1 class="page-title">调研详情</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="editSurvey" v-if="survey.status !== 'completed'">
          编辑调研
        </el-button>
        <el-button type="success" @click="generateQrCode" v-if="survey.status !== 'completed'">
          生成二维码
        </el-button>
        <el-button type="warning" @click="viewAnalysis">
          数据分析
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 调研详情内容 -->
    <div v-else-if="survey.id" class="survey-content">
      <!-- 基本信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="getStatusType(survey.status)" size="small">
              {{ getStatusText(survey.status) }}
            </el-tag>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="调研标题">
            {{ survey.title }}
          </el-descriptions-item>
          <el-descriptions-item label="调研状态">
            <el-tag :type="getStatusType(survey.status)">
              {{ getStatusText(survey.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(survey.createdAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(survey.updatedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="答题人数" :span="2">
            {{ survey.responseCount || 0 }} 人
          </el-descriptions-item>
          <el-descriptions-item label="调研描述" :span="2">
            {{ survey.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 调研题目卡片 -->
      <el-card class="questions-card">
        <template #header>
          <div class="card-header">
            <span>调研题目 ({{ survey.questions ? survey.questions.length : 0 }} 题)</span>
          </div>
        </template>
        
        <div v-if="survey.questions && survey.questions.length > 0" class="questions-list">
          <div 
            v-for="(question, index) in survey.questions" 
            :key="question.id" 
            class="question-item"
          >
            <div class="question-header">
              <span class="question-number">Q{{ index + 1 }}</span>
              <el-tag :type="getQuestionTypeTag(question.type).type" size="small">
                {{ getQuestionTypeTag(question.type).label }}
              </el-tag>
            </div>
            <div class="question-text">{{ question.text }}</div>
            <div v-if="question.options && question.options.length > 0" class="question-options">
              <div 
                v-for="option in question.options" 
                :key="option.id" 
                class="option-item"
              >
                {{ option.text }}
              </div>
            </div>
          </div>
        </div>
        
        <el-empty v-else description="暂无题目" />
      </el-card>

      <!-- 答题统计卡片 -->
      <el-card class="stats-card" v-if="survey.responseCount > 0">
        <template #header>
          <div class="card-header">
            <span>答题统计</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ survey.responseCount }}</div>
              <div class="stat-label">总答题人数</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ survey.completionRate || 0 }}%</div>
              <div class="stat-label">完成率</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ survey.avgTime || 0 }}分钟</div>
              <div class="stat-label">平均用时</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-result
        icon="error"
        title="调研不存在"
        sub-title="抱歉，您访问的调研不存在或已被删除"
      >
        <template #extra>
          <el-button type="primary" @click="goBack">返回列表</el-button>
        </template>
      </el-result>
    </div>

    <!-- 二维码对话框 -->
    <el-dialog
      v-model="qrDialog.visible"
      :title="qrDialog.title"
      width="400px"
      center
    >
      <QRCodeGenerator
        :survey-id="qrDialog.surveyId"
        :survey-title="qrDialog.title"
        :survey-description="qrDialog.description"
        :response-count="qrDialog.responseCount"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElSkeleton, ElResult } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import QRCodeGenerator from '@/components/QRCodeGenerator.vue'
import * as surveyApi from '@/api/survey'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const survey = ref({})
const qrDialog = ref({
  visible: false,
  title: '',
  surveyId: null,
  description: '',
  responseCount: 0
})

// 页面加载时获取调研详情
onMounted(() => {
  const surveyId = route.params.id
  if (surveyId) {
    fetchSurveyDetail(surveyId)
  }
})

// 获取调研详情
const fetchSurveyDetail = async (surveyId) => {
  try {
    loading.value = true
    
    // 使用新的调研详情API端点
    const response = await surveyApi.getSurveyDetail(surveyId)
    survey.value = response
    
    console.log('调研详情:', survey.value)
  } catch (error) {
    console.error('获取调研详情失败:', error)
    ElMessage.error('获取调研详情失败')
    survey.value = {}
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 编辑调研
const editSurvey = () => {
  router.push(`/survey?edit=${survey.value.id}`)
}

// 生成二维码
const generateQrCode = () => {
  qrDialog.value.title = survey.value.title
  qrDialog.value.surveyId = survey.value.id
  qrDialog.value.description = survey.value.description || ''
  qrDialog.value.responseCount = survey.value.responseCount || 0
  qrDialog.value.visible = true
}

// 查看数据分析
const viewAnalysis = () => {
  router.push(`/analysis?id=${survey.value.id}`)
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    'draft': 'info',
    'active': 'success',
    'completed': 'warning',
    'archived': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'active': '进行中',
    'completed': '已完成',
    'archived': '已归档'
  }
  return statusMap[status] || '未知'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取题目类型标签
const getQuestionTypeTag = (type) => {
  const typeMap = {
    'single_choice': { label: '单选题', type: 'primary' },
    'multi_choice': { label: '多选题', type: 'success' },
    'text_input': { label: '填空题', type: 'warning' },
    'number_input': { label: '数字题', type: 'info' }
  }
  return typeMap[type] || { label: '未知', type: 'info' }
}
</script>

<style scoped>
.survey-detail-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 40px;
}

.survey-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card,
.questions-card,
.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.question-number {
  font-weight: bold;
  color: #409eff;
}

.question-text {
  font-size: 16px;
  margin-bottom: 10px;
  color: #303133;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.option-item {
  padding: 8px 12px;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.error-container {
  padding: 40px;
  text-align: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
