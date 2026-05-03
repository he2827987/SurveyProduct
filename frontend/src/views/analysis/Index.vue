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
        
        <!-- AI 总结面板 -->
        <div class="card summary-panel" v-if="selectedSurvey && (summaryLoading || summaryData || summaryError)" ref="summaryPanelRef">
          <div class="summary-panel-header">
            <h2 class="section-title" style="margin: 0;">AI 智能分析总结</h2>
            <el-button v-if="summaryData" type="primary" link size="small" @click="generateSummary">
              重新生成
            </el-button>
          </div>
          <div v-loading="summaryLoading" style="min-height: 200px;">
            <div v-if="summaryError" class="summary-error">
              <el-alert :title="summaryError" type="error" show-icon :closable="false" />
            </div>
            <div v-else-if="summaryData" class="summary-content" v-html="renderMarkdown(summaryData)" />
          </div>
          <div class="summary-disclaimer">AI生成报告，请注意分辨</div>
        </div>
        
        <div v-if="!selectedSurvey" class="no-data-tip">
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

    <!-- 导出对话框 -->
    <el-dialog v-model="exportVisible" title="导出数据" width="480px">
      <div class="export-dialog-content">
        <p style="margin: 0 0 16px; color: #606266;">请选择要导出的内容和格式：</p>
        <div class="export-section">
          <div class="export-label">导出内容</div>
          <el-select v-model="exportView" placeholder="选择视图" style="width: 100%;" @change="onExportViewChange">
            <el-option label="筛选分析（图表 + 统计数据）" value="filter" />
            <el-option label="AI 智能总结" value="summary" />
            <el-option label="全部（分析 + 总结）" value="all" />
          </el-select>
        </div>
        <div class="export-section">
          <div class="export-label">导出格式</div>
          <el-radio-group v-model="exportFormat">
            <el-radio-button value="pdf">PDF 文件</el-radio-button>
            <el-radio-button value="png">PNG 图片</el-radio-button>
          </el-radio-group>
        </div>
        <div v-if="exportLoading" style="text-align: center; padding: 20px 0;">
          <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          <span style="margin-left: 8px;">正在生成，请稍候...</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="exportVisible = false">取消</el-button>
        <el-button type="primary" @click="doExport" :loading="exportLoading" :disabled="!selectedSurvey">
          导出
        </el-button>
      </template>
    </el-dialog>

    <!-- 隐藏的导出渲染区域 -->
    <div ref="exportContainerRef" class="export-render-area" style="position: fixed; left: -9999px; top: 0; width: 800px; background: #fff; padding: 30px; z-index: -1;">
      <div id="export-render-content"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
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

const summaryLoading = ref(false)
const summaryVisible = ref(false)
const summaryData = ref('')
const summaryError = ref('')
const summaryPanelRef = ref(null)

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
      title: survey.title,
      organization_id: survey.organization_id
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
    const all = (response || []).map((q, i) => ({
      id: q.id,
      text: q.text,
      type: q.type,
      order: i + 1
    }))
    surveyQuestions.value = statsMode.value === 'option_count'
      ? all.filter(q => q.type === 'single_choice' || q.type === 'multi_choice')
      : all
    if (surveyQuestions.value.length > 0) {
      if (!selectedQuestionId.value || !surveyQuestions.value.find(q => q.id === selectedQuestionId.value)) {
        selectedQuestionId.value = surveyQuestions.value[0].id
      }
    } else {
      selectedQuestionId.value = null
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
  await loadSurveyQuestions()
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

const exportVisible = ref(false)
const exportView = ref('filter')
const exportFormat = ref('pdf')
const exportLoading = ref(false)
const exportContainerRef = ref(null)

const exportData = () => {
  if (!selectedSurvey.value) {
    ElMessage.warning('请先选择调研')
    return
  }
  exportView.value = 'filter'
  exportFormat.value = 'pdf'
  exportVisible.value = true
}

const onExportViewChange = () => {}

const doExport = async () => {
  if (!selectedSurvey.value) return
  exportLoading.value = true
  try {
    const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
    const title = survey ? survey.title : `调研#${selectedSurvey.value}`

    const renderEl = document.getElementById('export-render-content')
    if (!renderEl) { exportLoading.value = false; return }

    let html = ''

    if (exportView.value === 'filter' || exportView.value === 'all') {
      html += buildAnalysisHTML(title)
    }

    if (exportView.value === 'summary' || exportView.value === 'all') {
      if (exportView.value === 'all' && html) html += '<hr style="margin: 30px 0; border: none; border-top: 2px solid #e4e7ed;" />'
      html += await buildSummaryHTML(survey)
    }

    renderEl.innerHTML = html

    await nextTick()
    await new Promise(r => setTimeout(r, 500))

    const canvas = await html2canvas(renderEl, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false
    })

    if (exportFormat.value === 'pdf') {
      const imgWidth = 210
      const pageHeight = 297
      const margin = 15
      const contentWidth = imgWidth - margin * 2
      const contentHeight = (canvas.height * contentWidth) / canvas.width
      let heightLeft = contentHeight
      let position = margin
      let page = 0

      const pdf = new jsPDF('p', 'mm', 'a4')
      while (heightLeft > 0) {
        if (page > 0) {
          pdf.addPage()
          position = margin - (pageHeight - margin * 2) * page
        }
        pdf.addImage(canvas.toDataURL('image/jpeg', 0.92), 'JPEG', margin, position, contentWidth, contentHeight)
        heightLeft -= (pageHeight - margin * 2)
        page++
      }
      pdf.save(`${title}-数据分析报告.pdf`)
    } else {
      const link = document.createElement('a')
      link.download = `${title}-数据分析.png`
      link.href = canvas.toDataURL('image/png')
      link.click()
    }

    renderEl.innerHTML = ''
    exportVisible.value = false
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

const buildAnalysisHTML = (title) => {
  const chartImg = document.querySelector('.chart-container canvas')
  let chartSection = ''
  if (chartImg) {
    chartSection = `<img src="${chartImg.toDataURL('image/png')}" style="width: 100%; max-height: 400px; object-fit: contain; margin: 16px 0;" />`
  }

  let dataRows = ''
  if (chartData.value.length > 0) {
    const hasRealData = chartData.value.some(d => d.name !== '暂无数据')
    if (hasRealData) {
      dataRows = chartData.value
        .filter(d => d.name !== '暂无数据')
        .map(d => `<tr><td style="padding:8px 12px;border:1px solid #ebeef5;">${d.name}</td><td style="padding:8px 12px;border:1px solid #ebeef5;text-align:right;">${d.value}</td></tr>`)
        .join('')
    }
  }

  const statsModeText = statsMode.value === 'score' ? '平均分' : '选项次数'
  const groupByText = groupBy.value === 'department' ? '部门' : groupBy.value === 'position' ? '职位' : '组织'

  return `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #303133;">
      <h1 style="font-size: 20px; margin: 0 0 6px; color: #303133;">${title}</h1>
      <p style="font-size: 13px; color: #909399; margin: 0 0 20px;">统计方式：${statsModeText} | 分组：${groupByText} | 导出时间：${new Date().toLocaleString('zh-CN')}</p>
      ${chartSection}
      ${dataRows ? `
        <h3 style="font-size: 16px; margin: 20px 0 10px;">数据明细</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <thead>
            <tr style="background: #f5f7fa;">
              <th style="padding:8px 12px;border:1px solid #ebeef5;text-align:left;">${groupByText}</th>
              <th style="padding:8px 12px;border:1px solid #ebeef5;text-align:right;">${statsModeText}</th>
            </tr>
          </thead>
          <tbody>${dataRows}</tbody>
        </table>
      ` : ''}
    </div>
  `
}

const buildSummaryHTML = async (survey) => {
  let summaryText = ''
  if (summaryData.value) {
    summaryText = summaryData.value
  } else if (survey && survey.organization_id) {
    try {
      const result = await analyticsApi.getSurveyAISummary(survey.organization_id, selectedSurvey.value)
      if (result && result.summary) {
        summaryData.value = result.summary
        summaryText = result.summary
      }
    } catch (e) {
      summaryText = '暂无总结数据。请先点击"生成总结"按钮生成 AI 分析。'
    }
  } else {
    summaryText = '暂无总结数据。'
  }

  const renderedSummary = renderMarkdown(summaryText)

  return `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #303133;">
      <h2 style="font-size: 18px; margin: 0 0 10px;">AI 智能分析总结</h2>
      <p style="font-size: 13px; color: #909399; margin: 0 0 20px;">生成时间：${new Date().toLocaleString('zh-CN')}</p>
      <div style="line-height: 1.8; font-size: 14px;">
        ${renderedSummary}
      </div>
    </div>
  `
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}

const generateSummary = async () => {
  if (!selectedSurvey.value) {
    ElMessage.warning('请先选择调研')
    return
  }
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  if (!survey || !survey.organization_id) {
    ElMessage.warning('该调研未关联组织，无法生成总结')
    return
  }

  summaryLoading.value = true
  summaryError.value = ''
  summaryData.value = ''

  try {
    const result = await analyticsApi.getSurveyAISummary(survey.organization_id, selectedSurvey.value)
    if (result && result.summary) {
      summaryData.value = result.summary
    } else {
      summaryError.value = '未能生成总结，请稍后重试'
    }
  } catch (error) {
    console.error('生成总结失败:', error)
    summaryError.value = error.response?.data?.detail || error.message || '生成总结失败，请稍后重试'
  } finally {
    summaryLoading.value = false
  }
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

.summary-content {
  line-height: 1.8;
  font-size: 14px;
  color: #303133;
}

.summary-content h1 {
  font-size: 20px;
  margin: 20px 0 10px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.summary-content h2 {
  font-size: 18px;
  margin: 16px 0 8px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 6px;
}

.summary-content h3 {
  font-size: 16px;
  margin: 14px 0 6px;
}

.summary-content li {
  margin: 4px 0;
}

.summary-error {
  padding: 20px 0;
}

.summary-panel {
  padding: 20px;
}

.summary-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-disclaimer {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  padding: 16px 0 4px;
  border-top: 1px solid #f0f0f0;
  margin-top: 20px;
}

.export-dialog-content {
  padding: 0 10px;
}

.export-section {
  margin-bottom: 18px;
}

.export-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.export-render-area {
  pointer-events: none;
}
</style>