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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import TagAnalyticsSimple from '@/components/TagAnalyticsSimple.vue'
import EnterpriseComparison from '@/components/EnterpriseComparison.vue'
import * as analyticsApi from '@/api/analytics'
import * as surveyApi from '@/api/survey'

const route = useRoute()
const loading = ref(false)
const activeTab = ref('filter') // 默认显示筛选分析板块

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

// 初始化函数
const setAuthToken = () => {
  // 设置测试token
  localStorage.setItem('access_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjIiLCJleHAiOjE3NzMxMzQ5MjB9.Qm-0-XjMUUcTtbguAb05SEABHZtIDT_qYn57ESpWV_A')
  ElMessage.success('Token已设置，请刷新页面')
}

// 加载调研列表
const loadSurveyList = async () => {
  try {
    loading.value = true
    console.log('正在加载调研列表...')
    // 尝试加载用户的调研
    const response = await surveyApi.getSurveys()
    console.log('调研列表响应:', response)
    
    if (Array.isArray(response)) {
      surveyList.value = response.map(survey => ({
        id: survey.id,
        title: survey.title
      }))
      console.log('处理后的调研列表:', surveyList.value)
      
      // 如果有路由参数，自动选中对应的调研
      if (initialSurveyId.value) {
        const found = surveyList.value.find(s => s.id === initialSurveyId.value)
        if (found) {
          selectedSurvey.value = initialSurveyId.value
          console.log('自动选中调研:', found)
          await loadAnalysisData()
        }
      }
    } else {
      ElMessage.warning('调研数据格式异常')
    }
  } catch (error) {
    console.error('加载调研列表失败:', error)
    ElMessage.error('加载调研列表失败')
    // 如果加载失败，使用模拟数据
    surveyList.value = [
      { id: 37, title: '测试用户调研' },
      { id: 36, title: '测试调研-题目关联修复验证' }
    ]
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

// 处理标签页切换
const handleTabChange = (tab) => {
  console.log('切换到标签页:', tab)
  activeTab.value = tab
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
    console.log('正在加载分析数据，调研ID:', selectedSurvey.value)
    
    // 根据分组方式生成不同的模拟数据
    let mockData = []
    
    switch (groupBy.value) {
      case 'department':
        mockData = [
          { name: '技术部', value: 85 },
          { name: '产品部', value: 78 },
          { name: '市场部', value: 92 },
          { name: '行政部', value: 75 },
          { name: '财务部', value: 88 }
        ]
        break
      case 'position':
        mockData = [
          { name: '初级员工', value: 76 },
          { name: '中级员工', value: 85 },
          { name: '高级员工', value: 90 },
          { name: '管理层', value: 88 }
        ]
        break
      case 'question':
        mockData = [
          { name: '满意度', value: 82 },
          { name: '工作环境', value: 78 },
          { name: '团队合作', value: 86 },
          { name: '薪资福利', value: 73 },
          { name: '发展机会', value: 80 }
        ]
        break
      case 'tag':
        mockData = tagList.value.map(tag => ({
          name: tag.name,
          value: Math.floor(Math.random() * 30) + 70
        }))
        break
      default:
        mockData = [
          { name: '选项A', value: 30 },
          { name: '选项B', value: 45 },
          { name: '选项C', value: 25 }
        ]
    }
    
    chartData.value = mockData
    console.log('分析数据已加载:', chartData.value)
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



// 初始化
onMounted(async () => {
  console.log('数据分析页面已挂载，开始初始化...')
  
  // 检查是否已登录
  const token = localStorage.getItem('access_token')
  if (!token) {
    console.log('未找到认证token')
    ElMessage.warning('请先登录')
    // 设置模拟数据用于展示
    surveyList.value = [
      { id: 37, title: '测试用户调研' },
      { id: 36, title: '测试调研-题目关联修复验证' }
    ]
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