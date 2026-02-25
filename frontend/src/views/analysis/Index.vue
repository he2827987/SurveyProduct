<!-- analysis.index.vue -->
<template>
  <div class="analysis-container page-container">
    <div class="flex-between">
      <h1 class="page-title">数据分析</h1>
      <div class="actions">
        <el-button type="primary" @click="exportData">导出数据</el-button>
        <el-button type="success" @click="generateSummary">生成总结</el-button>
        <el-button type="info" @click="showTagAnalytics = !showTagAnalytics">
          {{ showTagAnalytics ? '数据分析' : '标签分析' }}
        </el-button>
      </div>
    </div>
    
    <!-- 标签分析组件 -->
    <TagAnalytics v-if="showTagAnalytics" />
    
    <!-- 原有数据分析内容 -->
    <div v-else>
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
    
    <!-- 分析图表区域 -->
    <div class="analysis-content" v-loading="loading">
      <div class="card chart-panel" v-if="selectedSurvey">
        <h2 class="section-title">{{ chartTitle }}</h2>
        
        <!-- 图表类型选择 -->
        <div class="chart-type-selector">
          <el-radio-group v-model="chartType" @change="handleChartTypeChange">
            <el-radio-button value="pie">饼图</el-radio-button>
            <el-radio-button value="bar">柱状图</el-radio-button>
            <el-radio-button value="line">折线图</el-radio-button>
            <el-radio-button value="radar" :disabled="!radarChartEnabled">雷达图</el-radio-button>
          </el-radio-group>
          <div v-if="!radarChartEnabled" class="radar-disabled-tip">
            <el-tag type="warning" size="small">雷达图功能正在优化中</el-tag>
          </div>
        </div>
        
        <div class="chart-container" v-if="chartType !== 'bar' && chartType !== 'line' && chartType !== 'pie'">
          <AnalysisChart
            :type="chartType"
            :data="chartData"
            :title="chartTitle"
            :height="400"
            :description="chartDescription"
            @chart-click="handleChartClick"
          />
        </div>

        <!-- 饼图展示 -->
        <div v-if="chartType === 'pie'" class="pie-chart-panel">
          <div class="chart-hint">
            <el-tag type="info" effect="light">选择题目与选项，展示该选项在不同{{ groupBy === 'position' ? '职位' : '部门' }}下的占比；含未作答扇区</el-tag>
          </div>
          <div class="question-selector">
            <el-collapse v-model="questionCollapse">
              <el-collapse-item title="统计对象" name="pie-scope">
                <div class="mb-2">
                  <span style="margin-right:8px;">题目：</span>
                  <el-select v-model="pieSelectedQuestion" placeholder="请选择题目" style="width: 260px">
                    <el-option v-for="(q, idx) in questionOptions" :key="q.id" :label="`Q${q.order || idx + 1}. ${q.title}`" :value="q.id" />
                  </el-select>
                </div>
                <div class="mb-2">
                  <span style="margin-right:8px;">选项：</span>
                  <el-select v-model="pieSelectedOption" placeholder="请选择选项" style="width: 260px">
                    <el-option v-for="opt in pieOptions" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
          <div class="chart-item mb-8 p-4 border rounded">
            <AnalysisChart
              type="pie"
              :data="pieChartData"
              :title="chartTitle"
              :height="400"
              @chart-click="handleChartClick"
            />
          </div>
        </div>

        <!-- 折线图展示 -->

        <div v-if="chartType === 'line'" class="line-chart-panel">
          <div class="chart-hint">
            <el-tag type="info" effect="light">X轴：{{ groupBy === 'position' ? '职位' : '部门' }}；Y轴：平均分；可选择整张问卷或题目作为 series</el-tag>
          </div>
          <!-- 暂时隐藏统计对象选择，默认只统计问卷总分
          <div class="question-selector">
            <el-collapse v-model="questionCollapse">
              <el-collapse-item title="统计对象" name="line-scope">
                <div class="mb-2">
                  <el-checkbox v-model="lineIncludeSurvey">整张问卷总分</el-checkbox>
                </div>
                <el-checkbox-group v-model="lineSelectedQuestions">
                  <div class="question-checkbox" v-for="(q, idx) in questionOptions" :key="q.id">
                    <el-checkbox :value="q.id">Q{{ q.order || idx + 1 }}. {{ q.title }}</el-checkbox>
                  </div>
                </el-checkbox-group>
              </el-collapse-item>
            </el-collapse>
          </div>
          -->
          <div class="chart-item mb-8 p-4 border rounded">
            <AnalysisChart
              type="line"
              :is-multi-series="true"
              :xAxisData="lineCategories"
              :series="lineSeriesForChart"
              :data="[]"
              :title="chartTitle"
              :height="400"
              @chart-click="handleChartClick"
            />
          </div>
        </div>

        <!-- 新增：柱状图展示区域 -->
        <div v-if="chartType === 'bar'" class="bar-charts-list">
            <div class="chart-hint">
              <el-tag type="info" effect="light">
                X轴：题目选项（或“有答案/未作答”）；Y轴：选择次数；柱体按部门/职位堆叠。
              </el-tag>
            </div>
            <div class="question-selector">
              <el-collapse v-model="questionCollapse">
                <el-collapse-item title="选择题目" name="questions">
                  <el-checkbox-group v-model="selectedQuestionIds">
                    <div class="question-checkbox" v-for="(q, idx) in questionOptions" :key="q.id">
                      <el-checkbox :value="q.id">
                        Q{{ q.order || idx + 1 }}. {{ q.title }}
                      </el-checkbox>
                    </div>
                  </el-checkbox-group>
                </el-collapse-item>
              </el-collapse>
            </div>
            <div v-for="chart in filteredOptionCharts" :key="chart.id" class="chart-item mb-8 p-4 border rounded">
                <BarChart 
                    :title="chart.title" 
                    :data="chart.data"
                />
            </div>
            <el-empty v-if="filteredOptionCharts.length === 0" description="暂无选项分布数据" />
        </div>
      </div>
      
      <!-- AI 分析总结 -->
      <div class="card summary-panel" v-if="aiSummary">
        <div class="flex-between">
          <h2 class="section-title">AI 分析总结</h2>
          <el-button type="primary" link @click="regenerateSummary">重新生成</el-button>
        </div>
        
        <div class="summary-content">
          <p v-for="(paragraph, index) in aiSummary.split('\n\n')" :key="index" class="summary-paragraph">
            {{ paragraph }}
          </p>
        </div>
      </div>
      
      <!-- 数据表格 -->
      <div class="card data-table-panel" v-if="selectedSurvey">
        <h2 class="section-title">明细数据</h2>
        
        <el-table :data="tableData" border style="width: 100%">
          <el-table-column prop="question" label="题目" min-width="250"></el-table-column>
          <el-table-column prop="option" label="选项" width="180"></el-table-column>
          <el-table-column prop="count" label="数量" width="100" align="center"></el-table-column>
          <el-table-column prop="percentage" label="占比" width="100" align="center">
            <template #default="scope">
              {{ scope.row.percentage }}%
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AnalysisChart from '@/components/AnalysisChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import TagAnalytics from '@/components/TagAnalytics.vue'
import * as analyticsApi from '@/api/analytics'
import * as surveyApi from '@/api/survey'
import * as llmApi from '@/api/llm'
import axios from '@/api/request'

const route = useRoute()
const loading = ref(false)
const showTagAnalytics = ref(false)

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
const radarChartEnabled = ref(false) // 暂时禁用雷达图

// 图表数据
const chartData = ref([])

// 图表标题
const chartTitle = computed(() => {
  if (!selectedSurvey.value) return '请选择调研'
  
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  if (!survey) return '请选择调研'
  
  let groupText = ''
  switch(groupBy.value) {
    case 'department':
      groupText = '按部门分布'
      break
    case 'position':
      groupText = '按职位分布'
      break
    case 'question':
      groupText = '按问题分析'
      break
    case 'tag':
      const tag = tagList.value.find(t => t.id === selectedTag.value)
      groupText = tag ? `按"${tag.name}"标签分析` : '按标签分析'
      break
  }
  
  return `${survey.title} - ${groupText}`
})

// 图表描述
const chartDescription = computed(() => {
  if (!selectedSurvey.value) return ''
  
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  if (!survey) return ''
  
  const total = chartData.value.reduce((sum, item) => sum + item.value, 0)
  return `总计 ${total} 个回答，数据更新时间：${new Date().toLocaleString()}`
})

// AI分析总结
const aiSummary = ref(null)

// 表格数据
const tableData = ref([])

// 初始化
onMounted(async () => {
  await loadSurveyList()
  if (initialSurveyId.value) {
    selectedSurvey.value = initialSurveyId.value
    await loadAnalysisData()
  }
})

// 获取当前用户ID
const getCurrentUserId = () => {
  try {
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      return user.id
    }
    return null
  } catch (error) {
    console.error('获取用户ID失败:', error)
    return null
  }
}

// 加载调研列表
const loadSurveyList = async () => {
  try {
    loading.value = true

    // 检查认证状态 - 暂时注释掉
    // const token = localStorage.getItem('access_token')
    // if (!token) {
    //   console.warn('没有找到认证token')
    //   ElMessage.warning('请先设置认证Token')
    //   return
    // }

    const response = await surveyApi.getSurveys()

    // 获取当前用户ID
    const currentUserId = getCurrentUserId()

    // 显示当前用户创建的调研，或者所有调研（如果没有用户信息）
    let filteredSurveys
    if (currentUserId) {
      filteredSurveys = response.filter(survey => survey.created_by_user_id === currentUserId)
    } else {
      // 如果无法获取用户信息，显示所有调研
      filteredSurveys = response
    }

    surveyList.value = filteredSurveys.map(survey => ({
      id: survey.id,
      title: survey.title
    }))

    console.log('用户调研列表:', surveyList.value, '用户ID:', currentUserId)
  } catch (error) {
    console.error('加载调研列表失败:', error)
    if (error.response && error.response.status === 401) {
      ElMessage.error('认证失败，请重新设置Token')
    } else {
      ElMessage.error('加载调研列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 处理图表点击事件
const handleChartClick = (event) => {
  console.log('Chart clicked:', event)
  // 实际项目中可以跳转到详情页面或展示更多数据
}

// 处理图表类型变更
const handleChartTypeChange = (type) => {
  console.log('Chart type changed to:', type)
  
  // 安全检查：如果选择雷达图但功能被禁用，则回退到饼图
  if (type === 'radar' && !radarChartEnabled.value) {
    ElMessage.warning('雷达图功能暂时不可用，已切换到饼图')
    chartType.value = 'pie'
    return
  }
  
  // 重新格式化当前数据以适应新的图表类型
  if (selectedSurvey.value) {
    if (type === "line") {
      loadLineData()
    } else {
      loadAnalysisData()
    }
  }
}

// 处理调研变更
const handleSurveyChange = () => {
  loadAnalysisData()
  if (chartType.value === "line") {
    loadLineData()
  }
}

// 处理分组方式变更
const handleGroupChange = () => {
  loadAnalysisData()
}

// 刷新数据
const refreshData = () => {
  loadAnalysisData()
}

const optionCharts = ref([])
const questionScores = ref([])
const questionOptions = ref([]) // 题目列表（供多选）
const lineIncludeSurvey = ref(true) // 折线图是否包含整张问卷总分
const lineSelectedQuestions = ref([]) // 折线图选中的题目
const lineChartData = ref({ categories: [], series: [] })
const pieChartData = ref([])
const pieSelectedQuestion = ref(null)
const pieSelectedOption = ref(null)
const pieOptions = ref([])
const lineSeriesForChart = computed(() => (lineChartData.value.series || []).map(s => ({ name: s.name, value: s.data || [] })))
const lineCategories = computed(() => lineChartData.value.categories || [])

const selectedQuestionIds = ref([]) // 默认全选
const questionCollapse = ref(['questions'])

const filteredOptionCharts = computed(() => {
  if (!selectedQuestionIds.value || selectedQuestionIds.value.length === 0) {
    return []
  }
  return optionCharts.value.filter(item => {
    const idNum = Number(item.id)
    return selectedQuestionIds.value.includes(idNum)
  })
})

watch(lineSelectedQuestions, () => {
  loadLineData()
})
watch(lineIncludeSurvey, () => {
  loadLineData()
})
watch(pieSelectedQuestion, () => {
  if (!pieSelectedQuestion.value) return
  const chart = optionCharts.value.find(c => Number(c.id) === Number(pieSelectedQuestion.value))
  pieOptions.value = chart && chart.data ? chart.data.map(d => d.name) : []
  if (pieOptions.value.length > 0) {
    pieSelectedOption.value = pieOptions.value[0]
  }
  loadPieData()
})
watch(pieSelectedOption, () => {
  loadPieData()
})
// 新增：加载选项分布图表数据
const loadOptionCharts = async () => {
  if (!selectedSurvey.value) return
  
  loading.value = true
  try {
    const response = await axios.get(`/analysis/survey/${selectedSurvey.value}/charts/options`)
    optionCharts.value = response

    // 构建题目多选列表，默认全选
    questionOptions.value = response.map((item, index) => ({
      id: Number(item.id ?? index),
      title: item.title || `题目${index + 1}`,
      order: item.order || index + 1
    }))
    selectedQuestionIds.value = questionOptions.value.map(q => q.id)
  } catch (error) {
    console.error('加载选项图表失败:', error)
    // ElMessage.error('加载选项图表失败')
  } finally {
    loading.value = false
  }
}

// 加载分析数据

const loadLineData = async () => {
  if (!selectedSurvey.value) return
  try {
    const paramsSurvey = { scope: lineIncludeSurvey.value ? 'survey' : 'question', dimension: groupBy.value === 'position' ? 'position' : 'department' }
    let mergedSeries = []
    let categories = []

    if (lineIncludeSurvey.value) {
      const resp = await analyticsApi.getLineScores(selectedSurvey.value, paramsSurvey)
      categories = resp.categories || []
      mergedSeries = mergedSeries.concat(resp.series || [])
    }

    if (lineSelectedQuestions.value && lineSelectedQuestions.value.length > 0) {
      const respQ = await analyticsApi.getLineScores(selectedSurvey.value, {
        scope: lineIncludeSurvey.value ? 'both' : 'question',
        dimension: paramsSurvey.dimension,
        question_ids: lineSelectedQuestions.value.map(Number)
      })
      // 如果 categories 为空，用题目返回的；否则沿用已有
      if (!categories.length) categories = respQ.categories || []
      mergedSeries = mergedSeries.concat(respQ.series || [])
    }

    lineChartData.value = { categories, series: mergedSeries }
  } catch (err) {
    console.error('加载折线图数据失败:', err)
  }
}

const loadPieData = async () => {
  if (!selectedSurvey.value || !pieSelectedQuestion.value || !pieSelectedOption.value) return
  try {
    const resp = await analyticsApi.getPieOptionDistribution(selectedSurvey.value, {
      question_id: pieSelectedQuestion.value,
      option_text: pieSelectedOption.value,
      dimension: groupBy.value === 'position' ? 'position' : 'department',
      include_unanswered: true
    })
    pieChartData.value = resp.data || []
  } catch (err) {
    console.error('加载饼图数据失败:', err)
  }
}

const loadAnalysisData = async () => {
  if (!selectedSurvey.value) return
  
  loading.value = true
  try {
    // 加载选项分布图表
    await loadOptionCharts()
    // 加载折线图数据
    await loadLineData()
    // 加载饼图数据
    if (chartType.value === "pie") {
      if (!pieSelectedQuestion.value && questionOptions.value.length > 0) {
        pieSelectedQuestion.value = questionOptions.value[0].id
      }
      if ((!pieSelectedOption.value || !pieOptions.value.includes(pieSelectedOption.value)) && pieOptions.value.length > 0) {
        pieSelectedOption.value = pieOptions.value[0]
      }
      await loadPieData()
    }

    // 获取调研维度分析数据
    const response = await analyticsApi.getSurveyAnalytics(selectedSurvey.value, groupBy.value === 'position' ? 'position' : 'department')
    
    // 更新图表数据
    updateChartDataFromResponse(response)
    
    // 更新表格数据
    updateTableDataFromResponse(response)

    // 获取按题目得分汇总（当前不展示，可用于后续雷达/折线等）
    questionScores.value = await analyticsApi.getQuestionScores(selectedSurvey.value, {
      // 可根据需要传 department / position
    })
    
    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载分析数据失败:', error)
    ElMessage.error('加载分析数据失败')
  } finally {
    loading.value = false
  }
}

// 从API响应更新图表数据
const updateChartDataFromResponse = (response) => {
  if (!response || !response.question_analytics) {
    chartData.value = []
    return
  }
  
  let rawData = []
  
  // 适配新的 stats 响应结构：{ dimension: 'department' | 'position', stats: [{ dimension_value, response_count, total_score_sum, average_score }] }
  if (response && response.dimension && Array.isArray(response.stats)) {
    rawData = response.stats.map(item => ({
      name: item.dimension_value || '未知',
      value: item.response_count || 0
    }))
  } else {
    chartData.value = []
    return
  }
  
  // 根据图表类型格式化数据
  chartData.value = formatDataForChartType(rawData)
}

// 根据图表类型格式化数据
const formatDataForChartType = (rawData) => {
  if (!rawData || rawData.length === 0) {
    return []
  }
  
  switch (chartType.value) {
    case 'pie':
      // 饼图：直接使用原始数据
      return rawData
      
    case 'bar':
    case 'line':
      // 柱状图和折线图：需要分离名称和数值
      return {
        categories: rawData.map(item => item.name),
        series: [{
          name: '数量',
          data: rawData.map(item => item.value)
        }]
      }
      
    case 'radar':
      return rawData.map(item => item.value)
    default:
      return rawData
  }
}

// 从API响应更新表格数据
const updateTableDataFromResponse = (response) => {
  // 适配新的 stats 响应：维度统计，填充到表格中展示响应数
  if (!response || !response.dimension || !Array.isArray(response.stats)) {
    tableData.value = []
    return
  }

  const totalResponses = response.stats.reduce((sum, item) => sum + (item.response_count || 0), 0)
  const newTableData = response.stats.map(item => {
    const count = item.response_count || 0
    const percentage = totalResponses > 0 ? parseFloat(((count / totalResponses) * 100).toFixed(1)) : 0
    return {
      question: `维度：${response.dimension}`,
      option: item.dimension_value || '未知',
      count,
      percentage
    }
  })

  tableData.value = newTableData
}

// 更新图表数据（重新加载真实数据）
const updateChartData = () => {
  // 重新加载分析数据以确保使用真实数据
  if (selectedSurvey.value) {
    if (type === "line") {
      loadLineData()
    } else {
      loadAnalysisData()
    }
  }
}

// 导出数据
const exportData = async () => {
  if (!selectedSurvey.value) {
    ElMessage.warning('请先选择调研')
    return
  }
  
      try {
      loading.value = true
      const organizationId = 2 // 使用组织2，因为我们的测试数据在组织2中
      const params = {
      format: 'csv',
      fields: ['question', 'option', 'count', 'percentage']
    }
    
    const blob = await analyticsApi.exportSurveyData(organizationId, selectedSurvey.value, params)
    
    // 下载文件
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${chartTitle.value}_数据导出_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出数据失败:', error)
    // 如果API导出失败，使用本地导出
    try {
      const csvContent = [
        ['题目', '选项', '数量', '占比(%)'],
        ...tableData.value.map(row => [
          row.question,
          row.option,
          row.count,
          row.percentage
        ])
      ].map(row => row.join(',')).join('\n')
      
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `${chartTitle.value}_数据导出_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      
      ElMessage.success('数据导出成功')
    } catch (localError) {
      console.error('本地导出也失败:', localError)
      ElMessage.error('导出数据失败')
    }
  } finally {
    loading.value = false
  }
}

// 生成AI总结
const generateSummary = async () => {
  if (!selectedSurvey.value) {
    ElMessage.warning('请先选择调研')
    return
  }
  
  try {
    loading.value = true
    const organizationId = 2 // 使用组织2，因为我们的测试数据在组织2中
    
    // 首先获取调研的详细数据
    const surveyData = await analyticsApi.getSurveyAnalytics(selectedSurvey.value, groupBy.value === 'position' ? 'position' : 'department')
    
    if (!surveyData) {
      throw new Error('无法获取调研数据')
    }
    
    // 调用LLM API生成总结
    try {
      const llmData = await llmApi.generateSurveyReport({
        survey_data: {
          survey_title: surveyData.survey_title || '调研分析',
          total_answers: surveyData.total_answers || 0,
          question_analytics: surveyData.question_analytics || [],
          participant_analysis: surveyData.participant_analysis || {},
          participation_rate: surveyData.participation_rate || 0
        }
      })
      
      if (llmData && llmData.summary) {
        aiSummary.value = llmData.summary
        ElMessage.success('AI分析总结生成成功')
      } else {
        throw new Error('LLM API返回的数据格式不正确')
      }
    } catch (llmError) {
      console.error('LLM API调用失败:', llmError)
      // 如果LLM API失败，尝试使用analytics API的AI总结
      // 如果LLM API失败，尝试使用analytics API的AI总结
      const response = await analyticsApi.getSurveyAISummary(selectedSurvey.value)
      
      if (response && response.summary) {
        aiSummary.value = response.summary
        ElMessage.success('AI分析总结生成成功')
      } else {
        throw new Error('无法生成AI总结')
      }
    }
  } catch (error) {
    console.error('生成AI总结失败:', error)
    ElMessage.error('生成AI总结失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重新生成总结
const regenerateSummary = () => {
  aiSummary.value = null
  generateSummary()
}

// 设置认证Token
const setAuthToken = async () => {
  try {
    // 获取最新的token
    const response = await fetch('/api/v1/users/login/access-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'username=admin&password=admin123'
    })
    
    if (response.ok) {
      const data = await response.json()
      const token = data.access_token
      
      // 设置到localStorage
      localStorage.setItem('access_token', token)
      
      ElMessage.success('认证Token设置成功，正在重新加载调研列表...')
      
      // 重新加载调研列表
      await loadSurveyList()
    } else {
      ElMessage.error('获取Token失败，请检查后端服务')
    }
  } catch (error) {
    console.error('设置Token失败:', error)
    ElMessage.error('设置Token失败，请手动设置')
    
    // 提供手动设置的指导
    ElMessage.info('请在浏览器控制台执行: localStorage.setItem("access_token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NTgzMjAwOX0.eesA4459KkZtGd7XfOtyHUewJgQIhQ1uj9fUJPjA6VI")')
  }
}
</script>

<style scoped>
.filter-panel {
  margin-top: 20px;
  padding: 20px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-label {
  margin-right: 10px;
  white-space: nowrap;
}

.filter-select {
  width: 180px;
}

.no-surveys-tip {
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}

.analysis-content {
  margin-top: 20px;
}

.section-title {
  font-size: 18px;
  margin-bottom: 20px;
  color: #303133;
}

.chart-panel {
  margin-bottom: 20px;
}

.chart-type-selector {
  margin-bottom: 20px;
  position: relative;
}

.radar-disabled-tip {
  margin-top: 8px;
}

.chart-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.mock-chart {
  max-width: 100%;
  border-radius: 4px;
}

.summary-panel {
  margin-bottom: 20px;
}

.summary-content {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.summary-paragraph {
  margin-bottom: 15px;
  line-height: 1.6;
}

.data-table-panel {
  margin-bottom: 20px;
}

.line-chart-panel {
  margin-bottom: 16px;
}

.chart-hint {
  margin-bottom: 12px;
}

.pie-chart-panel {
  margin-bottom: 16px;
}

.question-selector {
  margin-bottom: 16px;
}

.question-checkbox {
  margin: 4px 0;
}

.actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-item {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .actions {
    flex-direction: column;
    gap: 10px;
  }
}
</style> 