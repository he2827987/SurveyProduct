<!-- EnterpriseComparison.vue - 企业对比分析组件 -->
<template>
  <div class="enterprise-comparison">
    <el-card class="comparison-card">
      <template #header>
        <div class="card-header">
          <h3>企业对比分析</h3>
          <div class="header-controls">
            <el-button type="primary" @click="startNewComparison">
              <el-icon><Plus /></el-icon>
              新建对比
            </el-button>
            <el-button @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 对比设置表单 -->
      <div v-if="showComparisonForm" class="comparison-form">
        <h4>设置对比参数</h4>
        <el-form :model="comparisonForm" label-width="120px">
          <el-form-item label="对比维度">
            <el-select v-model="comparisonForm.dimension" placeholder="选择对比维度">
              <el-option label="员工满意度" value="satisfaction" />
              <el-option label="工作环境" value="environment" />
              <el-option label="薪资福利" value="salary" />
              <el-option label="团队协作" value="teamwork" />
              <el-option label="发展机会" value="development" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="选择调研">
            <el-select v-model="comparisonForm.surveyId" placeholder="选择调研数据">
              <el-option
                v-for="survey in surveys"
                :key="survey.id"
                :label="survey.title"
                :value="survey.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="对比企业">
            <el-select
              v-model="comparisonForm.companies"
              multiple
              placeholder="选择要对比的企业"
              style="width: 100%"
            >
              <el-option
                v-for="company in availableCompanies"
                :key="company.id"
                :label="company.name"
                :value="company.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="runComparison" :loading="isAnalyzing">
              开始分析
            </el-button>
            <el-button @click="showComparisonForm = false">取消</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 对比结果展示 -->
      <div v-if="comparisonResults && !showComparisonForm" class="comparison-results">
        <div class="result-header">
          <h4>{{ comparisonForm.dimension }} - 对比分析结果</h4>
          <div class="result-actions">
            <el-button size="small" @click="exportResults">
              <el-icon><Download /></el-icon>
              导出结果
            </el-button>
            <el-button size="small" @click="generateAIAnalysis" :loading="isGeneratingAI">
              <el-icon><Star /></el-icon>
              AI深度分析
            </el-button>
          </div>
        </div>

        <!-- 对比图表 -->
        <div class="charts-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <div ref="comparisonChart" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <div ref="radarChart" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 详细数据表格 -->
        <div class="data-table-section">
          <h4>详细数据对比</h4>
          <el-table :data="comparisonTableData" stripe>
            <el-table-column prop="company" label="企业名称" width="150" />
            <el-table-column prop="score" label="综合得分" width="100">
              <template #default="{ row }">
                <el-tag :type="getScoreType(row.score)">
                  {{ row.score }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="satisfaction" label="满意度" width="100" />
            <el-table-column prop="environment" label="工作环境" width="100" />
            <el-table-column prop="salary" label="薪资福利" width="100" />
            <el-table-column prop="teamwork" label="团队协作" width="100" />
            <el-table-column prop="development" label="发展机会" width="100" />
            <el-table-column prop="participants" label="参与人数" width="100" />
            <el-table-column prop="response_rate" label="响应率" width="100">
              <template #default="{ row }">
                {{ row.response_rate }}%
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- AI分析结果 -->
        <div v-if="aiAnalysis" class="ai-analysis-section">
          <h4>AI深度分析</h4>
          <el-card class="analysis-card">
            <div class="analysis-content" v-html="formatAIAnalysis(aiAnalysis)"></div>
          </el-card>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!comparisonResults && !showComparisonForm" class="empty-state">
        <el-empty description="暂无对比数据">
          <el-button type="primary" @click="startNewComparison">
            开始企业对比分析
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <el-dialog v-model="isAnalyzing" title="分析中..." width="400px" :close-on-click-modal="false">
      <div class="loading-content">
        <el-progress :percentage="analysisProgress" :status="analysisStatus" />
        <p>{{ analysisMessage }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Download, Star } from '@element-plus/icons-vue'
import * as analyticsAPI from '@/api/analytics'
import * as surveyAPI from '@/api/survey'

// 响应式数据
const showComparisonForm = ref(false)
const isAnalyzing = ref(false)
const isGeneratingAI = ref(false)
const analysisProgress = ref(0)
const analysisStatus = ref('')
const analysisMessage = ref('')
const surveys = ref([])
const availableCompanies = ref([])
const comparisonResults = ref(null)
const aiAnalysis = ref('')
const comparisonTableData = ref([])

// 表单数据
const comparisonForm = ref({
  dimension: '',
  surveyId: null,
  companies: []
})

// 图表引用
const comparisonChart = ref(null)
const radarChart = ref(null)

// 方法
const loadSurveys = async () => {
  try {
    let allSurveys = []
    try {
      const myResponse = await surveyAPI.getSurveys()
      if (Array.isArray(myResponse)) allSurveys = allSurveys.concat(myResponse)
    } catch (e) { /* ignore */ }
    try {
      const globalResponse = await surveyAPI.getGlobalSurveys()
      if (Array.isArray(globalResponse)) {
        const existingIds = new Set(allSurveys.map(s => s.id))
        for (const s of globalResponse) {
          if (!existingIds.has(s.id)) allSurveys.push(s)
        }
      }
    } catch (e) { /* ignore */ }
    surveys.value = allSurveys
  } catch (error) {
    console.error('加载调研列表失败:', error)
  }
}

const loadAvailableCompanies = async () => {
  try {
    const response = await analyticsAPI.getOrganizations()
    const orgs = Array.isArray(response) ? response : (response?.data || response?.items || [])
    availableCompanies.value = orgs.map(org => ({
      id: org.id,
      name: org.name
    }))
  } catch (error) {
    console.error('加载企业列表失败:', error)
    availableCompanies.value = []
  }
}

const startNewComparison = () => {
  showComparisonForm.value = true
  comparisonResults.value = null
  aiAnalysis.value = ''
}

const runComparison = async () => {
  if (!comparisonForm.value.dimension || !comparisonForm.value.surveyId || comparisonForm.value.companies.length < 2) {
    ElMessage.warning('请完整填写对比参数，至少选择2个企业')
    return
  }

  isAnalyzing.value = true
  analysisProgress.value = 0
  analysisStatus.value = ''
  analysisMessage.value = '正在收集数据...'

  try {
    const progressInterval = setInterval(() => {
      if (analysisProgress.value < 80) {
        analysisProgress.value += 10
        if (analysisProgress.value === 20) analysisMessage.value = '正在分析数据...'
        if (analysisProgress.value === 40) analysisMessage.value = '正在生成对比图表...'
        if (analysisProgress.value === 60) analysisMessage.value = '正在计算指标...'
        if (comparisonProgress.value === 80) analysisMessage.value = '正在生成报告...'
      }
    }, 300)

    const surveyId = comparisonForm.value.surveyId
    const selectedOrgIds = comparisonForm.value.companies
    const primaryOrgId = selectedOrgIds[0]
    const compareOrgIds = selectedOrgIds.slice(1)

    const response = await analyticsAPI.getEnterpriseComparison(primaryOrgId, surveyId, compareOrgIds)
    const data = response?.data || response || []

    clearInterval(progressInterval)
    analysisProgress.value = 100
    analysisStatus.value = 'success'
    analysisMessage.value = '分析完成！'

    if (data.length > 0) {
      comparisonTableData.value = data.map(item => ({
        company: item.organization_name || item.company || item.name || '未知',
        score: Math.round(item.average_score || item.avg_score || item.total_score || 0),
        satisfaction: Math.round(item.satisfaction || item.average_score || 0),
        environment: Math.round(item.environment || 0),
        salary: Math.round(item.salary || 0),
        teamwork: Math.round(item.teamwork || 0),
        development: Math.round(item.development || 0),
        participants: item.response_count || item.participants || 0,
        response_rate: Math.round(item.response_rate || 0)
      }))

      comparisonResults.value = {
        dimension: comparisonForm.value.dimension,
        companies: comparisonTableData.value.map(d => d.company),
        data: comparisonTableData.value,
        generated_at: new Date().toISOString()
      }
    } else {
      comparisonTableData.value = []
      comparisonResults.value = {
        dimension: comparisonForm.value.dimension,
        companies: [],
        data: [],
        generated_at: new Date().toISOString()
      }
      ElMessage.info('所选企业暂无对比数据')
    }

    setTimeout(() => {
      isAnalyzing.value = false
      showComparisonForm.value = false
      if (comparisonResults.value.data.length > 0) {
        renderCharts()
      }
    }, 1000)

  } catch (error) {
    console.error('对比分析失败:', error)
    ElMessage.error('对比分析失败: ' + (error.message || '请检查参数后重试'))
    isAnalyzing.value = false
  }
}

const renderCharts = () => {
  if (!comparisonResults.value) return

  // 柱状图对比
  if (comparisonChart.value) {
    const chart1 = echarts.init(comparisonChart.value)
    const categories = comparisonResults.value.data.map(item => item.company)
    const scores = comparisonResults.value.data.map(item => item.score)
    
    chart1.setOption({
      title: { text: '综合得分对比', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: categories },
      yAxis: { type: 'value', name: '得分' },
      series: [{
        type: 'bar',
        data: scores,
        itemStyle: { color: '#409EFF' },
        label: { show: true, position: 'top' }
      }]
    })
  }

  // 雷达图对比
  if (radarChart.value) {
    const chart2 = echarts.init(radarChart.value)
    const dimensions = ['满意度', '工作环境', '薪资福利', '团队协作', '发展机会']
    const seriesData = comparisonResults.value.data.map(item => ({
      name: item.company,
      value: [
        item.satisfaction,
        item.environment,
        item.salary,
        item.teamwork,
        item.development
      ]
    }))
    
    chart2.setOption({
      title: { text: '多维度对比', left: 'center' },
      tooltip: {},
      radar: {
        indicator: dimensions.map(dim => ({ name: dim, max: 100 }))
      },
      series: [{
        type: 'radar',
        data: seriesData
      }]
    })
  }
}

const generateAIAnalysis = async () => {
  if (!comparisonResults.value) {
    ElMessage.warning('请先进行对比分析')
    return
  }

  isGeneratingAI.value = true

  try {
    // 构建对比数据
    const comparisonData = {
      dimension: comparisonForm.value.dimension,
      companies: comparisonResults.value.companies,
      comparison_data: comparisonResults.value.data
    }

    // 调用AI分析API
    const response = await analyticsAPI.generateEnterpriseComparisonAI(
      1, // 组织ID
      comparisonForm.value.surveyId,
      comparisonData
    )

    aiAnalysis.value = response.data.comparison_analysis
    ElMessage.success('AI分析生成成功')

  } catch (error) {
    console.error('AI分析生成失败:', error)
    ElMessage.error('AI分析生成失败，请稍后重试')
  } finally {
    isGeneratingAI.value = false
  }
}

const formatAIAnalysis = (analysis) => {
  // 简单的Markdown转HTML转换
  return analysis
    .replace(/### (.*)/g, '<h3>$1</h3>')
    .replace(/## (.*)/g, '<h2>$1</h2>')
    .replace(/# (.*)/g, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*)\*/g, '<em>$1</em>')
    .replace(/- (.*)/g, '<li>$1</li>')
    .replace(/(\d+)\. (.*)/g, '<li>$2</li>')
    .replace(/\n/g, '<br>')
}

const exportResults = () => {
  if (!comparisonResults.value) {
    ElMessage.warning('暂无可导出的数据')
    return
  }

  const csvContent = generateCSV()
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `企业对比分析_${comparisonForm.value.dimension}_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('导出成功')
}

const generateCSV = () => {
  const headers = ['企业名称', '综合得分', '满意度', '工作环境', '薪资福利', '团队协作', '发展机会', '参与人数', '响应率']
  const rows = comparisonTableData.value.map(item => [
    item.company,
    item.score,
    item.satisfaction,
    item.environment,
    item.salary,
    item.teamwork,
    item.development,
    item.participants,
    item.response_rate + '%'
  ])
  
  return [headers, ...rows].map(row => row.join(',')).join('\n')
}

const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 70) return 'warning'
  return 'danger'
}

const refreshData = async () => {
  await loadSurveys()
  await loadAvailableCompanies()
  ElMessage.success('数据刷新成功')
}

// 生命周期
onMounted(() => {
  loadSurveys()
  loadAvailableCompanies()
})
</script>

<style scoped>
.enterprise-comparison {
  padding: 20px;
}

.comparison-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.header-controls {
  display: flex;
  gap: 12px;
}

.comparison-form {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 20px;
}

.comparison-results {
  margin-top: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-header h4 {
  margin: 0;
  color: #303133;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.data-table-section {
  margin-bottom: 30px;
}

.ai-analysis-section {
  margin-bottom: 30px;
}

.analysis-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.analysis-content {
  padding: 20px;
  line-height: 1.6;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.loading-content {
  text-align: center;
  padding: 20px;
}

.loading-content p {
  margin-top: 15px;
  color: #606266;
}

h4 {
  color: #303133;
  margin-bottom: 15px;
}

:deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}
</style>