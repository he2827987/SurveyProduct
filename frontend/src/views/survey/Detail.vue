<template>
  <div class="survey-detail-container page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button type="primary" @click="goBack">返回</el-button>
        <h1 class="page-title">调研详情</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="editSurvey" v-if="survey.status !== 'completed'">
          编辑调研
        </el-button>
        <el-button type="success" @click="openPublishDialog" v-if="survey.status !== 'completed'">
          发布调研
        </el-button>
        <el-button type="success" @click="republishSurvey" v-if="survey.status === 'completed'">
          再次发布
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
                v-for="(option, optionIndex) in question.options"
                :key="optionIndex"
                class="option-item"
              >
                {{ option }}
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

    <!-- 发布调研对话框 -->
    <el-dialog
      v-model="publishDialog.visible"
      title="发布调研"
      width="500px"
      center
    >
      <el-form label-width="100px" label-position="top">
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="publishDialog.startTime"
            type="datetime"
            placeholder="选择开始时间（可选）"
            style="width: 100%"
            :teleported="false"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="publishDialog.endTime"
            type="datetime"
            placeholder="选择结束时间（可选）"
            style="width: 100%"
            :teleported="false"
          />
        </el-form-item>
      </el-form>
      <div class="publish-actions">
        <el-button @click="publishDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="confirmPublish" :loading="publishing">
          发布并生成链接
        </el-button>
      </div>

      <el-divider v-if="publishDialog.published" />

      <div v-if="publishDialog.published">
        <QRCodeGenerator
          :survey-id="publishDialog.surveyId"
          :survey-title="publishDialog.title"
          :survey-description="publishDialog.description"
          :response-count="publishDialog.responseCount"
          :auto-generate="true"
          :end-time="publishDialog.endTime"
        />
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElSkeleton, ElResult } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import QRCodeGenerator from '@/components/QRCodeGenerator.vue'
import * as surveyApi from '@/api/survey'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const publishing = ref(false)
const survey = ref({})
const publishDialog = ref({
  visible: false,
  title: '',
  surveyId: null,
  description: '',
  responseCount: 0,
  startTime: null,
  endTime: null,
  published: false
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

// 返回调研管理页
const goBack = () => {
  router.push('/survey')
}

// 编辑调研
const editSurvey = () => {
  router.push(`/survey?edit=${survey.value.id}`)
}

const republishSurvey = async () => {
  try {
    const baseTitle = survey.value.title || ''
    const baseTitleClean = baseTitle.replace(/-\s*\d+$/, '').replace(/\(\d+\)\s*$/, '').trim()
    const questions = survey.value.questions || []
    const questionIds = questions.map(q => q.id)

    const newTitle = `${baseTitleClean} - 2`
    const newSurvey = await surveyApi.createSurvey({
      title: newTitle,
      description: survey.value.description || '',
      organization_id: survey.value.organization_id || null,
      question_ids: questionIds,
      is_anonymous: survey.value.is_anonymous || false
    })

    await ElMessageBox.confirm(
      `调研"${newTitle}"已创建，是否立即发布？`,
      '再次发布',
      { confirmButtonText: '立即发布', cancelButtonText: '查看详情', type: 'info' }
    ).then(async () => {
      const endTime = new Date()
      endTime.setHours(endTime.getHours() + 24)
      await surveyApi.updateSurveyStatus(newSurvey.id, {
        status: 'active',
        start_time: new Date().toISOString(),
        end_time: endTime.toISOString()
      })
      ElMessage.success('调研已发布')
      router.push(`/surveys/${newSurvey.id}`)
    }).catch(() => {
      router.push(`/surveys/${newSurvey.id}`)
    })
  } catch (error) {
    if (error !== 'cancel' && error?.toString() !== 'cancel') {
      console.error('再次发布失败:', error)
      ElMessage.error('再次发布失败')
    }
  }
}

const openPublishDialog = () => {
  publishDialog.value.title = survey.value.title
  publishDialog.value.surveyId = survey.value.id
  publishDialog.value.description = survey.value.description || ''
  publishDialog.value.responseCount = survey.value.responseCount || 0
  publishDialog.value.startTime = survey.value.startTime ? new Date(survey.value.startTime) : null
  publishDialog.value.endTime = survey.value.endTime ? new Date(survey.value.endTime) : null
  publishDialog.value.published = false
  publishDialog.value.visible = true
}

const confirmPublish = async () => {
  try {
    publishing.value = true
    await surveyApi.updateSurveyStatus(publishDialog.value.surveyId, {
      status: 'active',
      start_time: publishDialog.value.startTime ? publishDialog.value.startTime.toISOString() : null,
      end_time: publishDialog.value.endTime ? publishDialog.value.endTime.toISOString() : null
    })
    publishDialog.value.published = true
    survey.value.status = 'active'
    ElMessage.success('调研已发布')
  } catch (error) {
    console.error('发布调研失败:', error)
    ElMessage.error('发布调研失败')
  } finally {
    publishing.value = false
  }
}

// 查看数据分析
const viewAnalysis = () => {
  router.push(`/analysis?id=${survey.value.id}`)
}

const openSubjectiveDetailAnswers = () => {
  router.push(`/survey/${survey.value.id}/subjective-answers`)
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

.publish-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 10px;
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
