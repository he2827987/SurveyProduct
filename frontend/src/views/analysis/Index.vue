<!-- analysis.index.vue -->
<template>
  <div class="analysis-container page-container">
    <div class="flex-between">
      <h1 class="page-title">数据分析</h1>
      <div class="actions">
        <el-button type="primary" @click="exportData">导出数据</el-button>
        <el-button type="success" @click="generateSummary">生成总结</el-button>
      </div>
    </div>
    
    <!-- 三个板块的切换按钮 -->
    <div class="tab-container">
      <el-radio-group v-model="activeTab" @change="handleTabChange" class="tab-group">
        <el-radio-button label="filter">筛选分析</el-radio-button>
        <el-radio-button label="tag">标签分析</el-radio-button>
        <el-radio-button label="enterprise">企业对比</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 筛选分析板块 -->
    <div v-show="activeTab === 'filter'" class="tab-content">
      <!-- 筛选条件 -->
      <div class="card filter-panel">
        <div class="filter-row">
          <div class="filter-item">
            <span class="filter-label">选择调研：</span>
            <el-select v-model="selectedSurvey" placeholder="请选择调研" class="filter-select" @change="handleSurveyChange">
              <el-option 
                v-for="item in surveyList" 
                :key="item.id" 
                :label="item.title" 
                :value="item.id"
              />
            </el-select>
            <div v-if="surveyList.length === 0" class="no-surveys-tip">
              暂无调研数据，请先创建调研
            </div>
          </div>
          
          <div class="filter-item">
            <span class="filter-label">统计方式：</span>
            <el-select v-model="statsMode" placeholder="统计方式" class="filter-select" @change="handleStatsModeChange">
              <el-option label="按分数" value="score" />
              <el-option label="按选项次数" value="option_count" />
            </el-select>
          </div>
        </div>
        <div class="filter-row">
          <div class="filter-item">
            <span class="filter-label">分组方式：</span>
            <el-select v-model="groupBy" placeholder="请选择分组方式" class="filter-select" @change="handleGroupChange">
              <el-option v-if="statsMode === 'score'" label="按部门" value="department" />
              <el-option v-if="statsMode === 'score'" label="按职位" value="position" />
              <el-option v-if="statsMode === 'score'" label="按问题得分" value="question" />
              <el-option v-if="statsMode === 'option_count'" label="按部门" value="department" />
              <el-option v-if="statsMode === 'option_count'" label="按职位" value="position" />
            </el-select>
          </div>

          <div class="filter-item" v-if="statsMode === 'option_count'">
            <span class="filter-label">选择题目：</span>
            <el-select v-model="selectedQuestionId" placeholder="请选择题目" class="filter-select-wide" @change="loadAnalysisData">
              <el-option 
                v-for="q in surveyQuestions" 
                :key="q.id" 
                :label="(q.text.startsWith('Q' + q.order) ? '' : 'Q' + q.order + ': ') + q.text" 
                :value="q.id"
              />
            </el-select>
          </div>
        </div>
      </div>
      
      <div class="analysis-content" v-loading="loading">
        <div class="card chart-panel" v-if="selectedSurvey">
          <h2 class="section-title">{{ chartTitle }}</h2>
          
          <div class="chart-type-selector">
            <el-radio-group v-model="chartType" @change="handleChartTypeChange">
              <el-radio-button value="pie">饼图</el-radio-button>
              <el-radio-button value="bar">柱状图</el-radio-button>
              <el-radio-button value="line">折线图</el-radio-button>
            </el-radio-group>
          </div>
          
          <div class="chart-container" v-if="chartData.length > 0">
            <AnalysisChart 
              :type="chartType"
              :data="chartData"
              :title="chartTitle"
              :height="400"
              :series="chartSeries"
              :xAxisData="chartXAxis"
              @chart-click="handleChartClick"
            />
          </div>
        </div>
        
        <div v-else class="no-data-tip">
          <el-empty description="请选择调研查看数据分析" />
        </div>
      </div>
    </div>
    
    <!-- 标签分析板块 -->
    <div v-show="activeTab === 'tag'" class="tab-content">
      <TagAnalyticsSimple />
    </div>
    
    <!-- 企业对比板块 -->
    <div v-show="activeTab === 'enterprise'" class="tab-content">
      <EnterpriseComparison />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AnalysisChart from '@/components/AnalysisChart.vue'
import TagAnalyticsSimple from '@/components/TagAnalyticsSimple.vue'
import EnterpriseComparison from '@/components/EnterpriseComparison.vue'
import * as analyticsApi from '@/api/analytics'
import * as surveyApi from '@/api/survey'

const route = useRoute()
const loading = ref(false)
const activeTab = ref('filter')

const initialSurveyId = computed(() => {
  return route.query.id ? parseInt(route.query.id) : null
})

const surveyList = ref([])
const selectedSurvey = ref(null)
const statsMode = ref('score')
const groupBy = ref('department')
const selectedQuestionId = ref(null)
const surveyQuestions = ref([])

const chartType = ref('pie')
const chartData = ref([])
const chartSeries = ref([])
const chartXAxis = ref([])

const chartTitle = computed(() => {
  if (!selectedSurvey.value) return '请选择调研'
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  const suffix = statsMode.value === 'option_count' ? ' - 选项选择次数' : ' - 平均分'
  return survey ? `${survey.title}${suffix}` : '数据分析'
})

const loadSurveyList = async () => {
  try {
    loading.value = true
    let allSurveys = []
    try {
      const myResponse = await surveyApi.getSurveys()
      if (Array.isArray(myResponse)) allSurveys = allSurveys.concat(myResponse)
    } catch (e) { /* ignore */ }
    try {
      const globalResponse = await surveyApi.getGlobalSurveys()
      if (Array.isArray(globalResponse)) {
        const existingIds = new Set(allSurveys.map(s => s.id))
        for (const s of globalResponse) {
          if (!existingIds.has(s.id)) allSurveys.push(s)
        }
      }
    } catch (e) { /* ignore */ }

    surveyList.value = allSurveys.map(survey => ({
      id: survey.id,
      title: survey.title
    }))

    if (initialSurveyId.value) {
      const found = surveyList.value.find(s => s.id === initialSurveyId.value)
      if (found) {
        selectedSurvey.value = initialSurveyId.value
        await onSurveySelected()
      }
    }
  } catch (error) {
    console.error('加载调研列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadSurveyQuestions = async () => {
  if (!selectedSurvey.value) return
  try {
    const response = await surveyApi.getSurveyQuestions(selectedSurvey.value)
    surveyQuestions.value = (response || []).map((q, i) => ({
      id: q.id,
      text: q.text,
      type: q.type,
      order: i + 1
    }))
    if (surveyQuestions.value.length > 0) {
      if (!selectedQuestionId.value || !surveyQuestions.value.find(q => q.id === selectedQuestionId.value)) {
        selectedQuestionId.value = surveyQuestions.value[0].id
      }
    }
  } catch (error) {
    console.error('加载题目列表失败:', error)
    surveyQuestions.value = []
  }
}

const handleSurveyChange = async () => {
  selectedQuestionId.value = null
  surveyQuestions.value = []
  await onSurveySelected()
}

const onSurveySelected = async () => {
  await loadSurveyQuestions()
  await loadAnalysisData()
}

const handleStatsModeChange = async () => {
  groupBy.value = 'department'
  await loadAnalysisData()
}

const handleGroupChange = async () => {
  await loadAnalysisData()
}

const handleTabChange = (tab) => {
  activeTab.value = tab
}

const handleChartTypeChange = () => {}

const loadAnalysisData = async () => {
  if (!selectedSurvey.value) return

  try {
    loading.value = true
    chartData.value = []
    chartSeries.value = []
    chartXAxis.value = []

    if (statsMode.value === 'score') {
      await loadScoreData()
    } else {
      await loadOptionCountData()
    }

    if (chartData.value.length === 0) {
      chartData.value = [{ name: '暂无数据', value: 0 }]
    }
  } catch (error) {
    console.error('加载分析数据失败:', error)
    chartData.value = []
  } finally {
    loading.value = false
  }
}

const loadScoreData = async () => {
  if (groupBy.value === 'question') {
    const scores = await analyticsApi.getQuestionScores(selectedSurvey.value)
    chartData.value = (scores || []).map(item => ({
      name: item.question_text
        ? (item.question_text.length > 12 ? item.question_text.substring(0, 12) + '...' : item.question_text)
        : `Q${item.question_id}`,
      value: item.avg_score || 0
    }))
  } else {
    const response = await analyticsApi.getSurveyAnalytics(selectedSurvey.value, groupBy.value)
    const stats = response?.stats || response || []
    chartData.value = stats.map(item => ({
      name: item.key || item.dimension_value || '未知',
      value: item.average_score || item.avg_score || item.total_score_sum || 0
    }))
  }
}

const loadOptionCountData = async () => {
  if (!selectedQuestionId.value) return

  const chartsData = await analyticsApi.getOptionCharts(selectedSurvey.value, { dimension: groupBy.value })

  const questionData = (chartsData || []).find(q => String(q.id) === String(selectedQuestionId.value))
  if (!questionData || !questionData.data) {
    chartData.value = [{ name: '暂无数据', value: 0 }]
    return
  }

  chartData.value = questionData.data.map(opt => ({
    name: opt.name,
    value: opt.value
  }))

  const allGroups = new Set()
  for (const opt of questionData.data) {
    for (const b of (opt.breakdown || [])) {
      allGroups.add(b.name)
    }
  }
  const groups = [...allGroups].sort()

  chartXAxis.value = questionData.data
    .filter(opt => opt.name !== '(未作答)')
    .map(opt => opt.name)
  
  chartSeries.value = groups.map(group => ({
    name: group,
    value: questionData.data
      .filter(opt => opt.name !== '(未作答)')
      .map(opt => {
        const found = (opt.breakdown || []).find(b => b.name === group)
        return found ? found.value : 0
      })
  }))
}

const handleChartClick = (event) => {
  console.log('Chart clicked:', event)
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中')
}

const generateSummary = () => {
  ElMessage.success('总结生成功能开发中')
}

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    ElMessage.warning('请先登录')
    return
  }
  await loadSurveyList()
})
 </script>

<style scoped>
.page-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: 100vh;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.tab-container {
  margin-bottom: 20px;
}

.tab-group {
  width: 100%;
}

.tab-content {
  margin-top: 20px;
}

.card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.filter-panel {
  padding: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  white-space: nowrap;
}

.filter-select {
  width: 200px;
}

.filter-select-wide {
  width: 300px;
}

.filter-row + .filter-row {
  margin-top: 15px;
}

.no-surveys-tip {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.analysis-content {
  margin-top: 20px;
}

.chart-panel {
  padding: 20px;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}

.chart-type-selector {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.no-data-tip {
  text-align: center;
  padding: 40px 0;
}
</style>