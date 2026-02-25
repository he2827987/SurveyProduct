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
    
    <!-- 标签分析组件 -->
    <TagAnalyticsSimple />
    
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
            <br>
            <el-button type="primary" size="small" @click="setAuthToken" style="margin-top: 10px;">
              设置认证Token
            </el-button>
          </div>
        </div>
        
        <div class="filter-item">
          <span class="filter-label">分组方式：</span>
          <el-select v-model="groupBy" placeholder="请选择分组方式" class="filter-select" @change="handleGroupChange">
            <el-option label="按部门" value="department" />
            <el-option label="按职位" value="position" />
            <el-option label="按问题" value="question" />
            <el-option label="按标签" value="tag" />
          </el-select>
        </div>
        
        <div class="filter-item" v-if="groupBy === 'tag'">
          <span class="filter-label">选择标签：</span>
          <el-select v-model="selectedTag" placeholder="请选择标签" class="filter-select" @change="refreshData">
            <el-option 
              v-for="tag in tagList" 
              :key="tag.id" 
              :label="tag.name" 
              :value="tag.id"
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
        
        <div class="chart-container">
          <AnalysisChart 
            :type="chartType"
            :data="chartData"
            :title="chartTitle"
            :height="400"
            @chart-click="handleChartClick"
          />
        </div>
      </div>
      
      <div v-else class="no-data-tip">
        <el-empty description="请选择调研查看数据分析" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import TagAnalyticsSimple from '@/components/TagAnalyticsSimple.vue'
import * as analyticsApi from '@/api/analytics'
import * as surveyApi from '@/api/survey'

const route = useRoute()
const loading = ref(false)

// 从路由获取初始调研ID
const initialSurveyId = computed(() => {
  return route.query.id ? parseInt(route.query.id) : null
})

// 数据源
const surveyList = ref([])
const tagList = ref([
  { id: 1, name: '工作环境' },
  { id: 2, name: '员工福利' },
  { id: 3, name: '团队协作' },
  { id: 4, name: '领导力' },
  { id: 5, name: '职业发展' }
])

// 筛选条件
const selectedSurvey = ref(null)
const groupBy = ref('department')
const selectedTag = ref(null)

// 图表类型
const chartType = ref('pie')
const chartData = ref([])

// 图表标题
const chartTitle = computed(() => {
  if (!selectedSurvey.value) return '请选择调研'
  
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  return survey ? `${survey.title} - 数据分析` : '数据分析'
})

// 加载调研列表
const loadSurveyList = async () => {
  try {
    loading.value = true
    const response = await surveyApi.getSurveys()
    surveyList.value = response.map(survey => ({
      id: survey.id,
      title: survey.title
    }))
  } catch (error) {
    console.error('加载调研列表失败:', error)
    ElMessage.error('加载调研列表失败')
  } finally {
    loading.value = false
  }
}

// 处理调研变更
const handleSurveyChange = async () => {
  if (selectedSurvey.value) {
    await loadAnalysisData()
  }
}

// 处理分组变更
const handleGroupChange = async () => {
  if (selectedSurvey.value) {
    await loadAnalysisData()
  }
}

// 刷新数据
const refreshData = async () => {
  if (selectedSurvey.value) {
    await loadAnalysisData()
  }
}

// 加载分析数据
const loadAnalysisData = async () => {
  if (!selectedSurvey.value) return
  
  try {
    loading.value = true
    
    // 简化的数据模拟
    const mockData = [
      { name: '部门A', value: 30 },
      { name: '部门B', value: 25 },
      { name: '部门C', value: 45 }
    ]
    
    chartData.value = mockData
  } catch (error) {
    console.error('加载分析数据失败:', error)
    ElMessage.error('加载分析数据失败')
  } finally {
    loading.value = false
  }
}

// 处理图表点击
const handleChartClick = (event) => {
  console.log('Chart clicked:', event)
}

// 处理图表类型变更
const handleChartTypeChange = (type) => {
  console.log('Chart type changed to:', type)
  if (selectedSurvey.value) {
    loadAnalysisData()
  }
}

// 导出数据
const exportData = () => {
  ElMessage.success('数据导出功能开发中')
}

// 生成总结
const generateSummary = () => {
  ElMessage.success('总结生成功能开发中')
}

// 设置认证Token
const setAuthToken = () => {
  ElMessage.success('Token设置功能开发中')
}

// 初始化
onMounted(async () => {
  await loadSurveyList()
  if (initialSurveyId.value) {
    selectedSurvey.value = initialSurveyId.value
    await loadAnalysisData()
  }
})
</script>