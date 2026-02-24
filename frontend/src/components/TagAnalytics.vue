<!-- TagAnalytics.vue - 标签分析组件 -->
<template>
  <div class="tag-analytics">
    <el-card class="analytics-card">
      <template #header>
        <div class="card-header">
          <h3>标签统计分析</h3>
          <div class="header-controls">
            <el-select v-model="selectedOrganization" placeholder="选择组织" @change="loadOrganizationData">
              <el-option
                v-for="org in organizations"
                :key="org.id"
                :label="org.name"
                :value="org.id"
              />
            </el-select>
            <el-select v-model="selectedSurvey" placeholder="选择调研（可选）" @change="loadSurveyData" clearable>
              <el-option
                v-for="survey in surveys"
                :key="survey.id"
                :label="survey.title"
                :value="survey.id"
              />
            </el-select>
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 标签概览统计 -->
      <div class="overview-section">
        <h4>标签概览</h4>
        <el-row :gutter="20">
          <el-col :span="6" v-for="stat in overviewStats" :key="stat.label">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 标签分布图表 -->
      <div class="chart-section">
        <h4>标签分布</h4>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <div ref="tagDistributionChart" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <div ref="tagScoreChart" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 标签详情表格 -->
      <div class="table-section">
        <h4>标签详情</h4>
        <el-table :data="tagData" stripe>
          <el-table-column prop="tag_name" label="标签名称" width="150">
            <template #default="{ row }">
              <el-tag :color="row.tag_color" effect="dark">
                {{ row.tag_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="question_count" label="问题数量" width="100" />
          <el-table-column prop="percentage" label="占比" width="100">
            <template #default="{ row }">
              {{ row.percentage }}%
            </template>
          </el-table-column>
          <el-table-column prop="total_responses" label="回答总数" width="120" />
          <el-table-column prop="average_score" label="平均得分" width="100">
            <template #default="{ row }">
              <span v-if="row.score_stats && row.score_stats.average_score">
                {{ row.score_stats.average_score }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="viewTagDetails(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 标签详情对话框 -->
    <el-dialog v-model="tagDetailVisible" title="标签详细分析" width="80%">
      <div v-if="selectedTagDetail">
        <div class="tag-header">
          <el-tag :color="selectedTagDetail.tag_color" size="large" effect="dark">
            {{ selectedTagDetail.tag_name }}
          </el-tag>
          <div class="tag-stats">
            <span>问题数量: {{ selectedTagDetail.questions?.length || 0 }}</span>
            <span>总回答数: {{ selectedTagDetail.total_responses }}</span>
            <span>平均每题回答: {{ selectedTagDetail.average_responses_per_question }}</span>
          </div>
        </div>

        <!-- 问题列表 -->
        <div class="questions-section">
          <h4>相关问题</h4>
          <el-collapse v-model="activeQuestions">
            <el-collapse-item 
              v-for="(question, index) in selectedTagDetail.questions" 
              :key="question.question_id"
              :title="`${index + 1}. ${question.question_text}`"
              :name="question.question_id"
            >
              <div class="question-details">
                <p><strong>问题类型:</strong> {{ getQuestionTypeLabel(question.question_type) }}</p>
                <p><strong>回答数量:</strong> {{ question.responses }}</p>
                
                <!-- 响应分布图表 -->
                <div v-if="Object.keys(question.response_distribution).length > 0" class="response-chart">
                  <h5>响应分布</h5>
                  <div :ref="`response-chart-${question.question_id}`" class="mini-chart"></div>
                </div>
                
                <!-- 响应详情表格 -->
                <el-table :data="getResponseTableData(question.response_distribution)" size="small">
                  <el-table-column prop="option" label="选项" />
                  <el-table-column prop="count" label="选择人数" />
                  <el-table-column prop="percentage" label="占比" />
                </el-table>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import analyticsAPI from '@/api/analytics'

// 响应式数据
const selectedOrganization = ref(null)
const selectedSurvey = ref(null)
const organizations = ref([])
const surveys = ref([])
const tagData = ref([])
const tagDetailVisible = ref(false)
const selectedTagDetail = ref(null)
const activeQuestions = ref([])
const overviewStats = ref([])

// 图表引用
const tagDistributionChart = ref(null)
const tagScoreChart = ref(null)

// 方法
const loadOrganizations = async () => {
  try {
    const response = await analyticsAPI.getOrganizations()
    organizations.value = response.data
    if (organizations.value.length > 0) {
      selectedOrganization.value = organizations.value[0].id
      await loadOrganizationData()
    }
  } catch (error) {
    ElMessage.error('加载组织列表失败')
  }
}

const loadOrganizationData = async () => {
  if (!selectedOrganization.value) return
  
  try {
    // 加载调研列表
    const surveysResponse = await analyticsAPI.getOrganizationSurveys(selectedOrganization.value)
    surveys.value = surveysResponse.data
    
    // 加载标签统计数据
    const tagResponse = await analyticsAPI.getOrganizationTagAnalytics(selectedOrganization.value)
    tagData.value = tagResponse.data.tag_statistics
    
    // 更新概览统计
    updateOverviewStats(tagResponse.data)
    
    // 渲染图表
    await nextTick()
    renderCharts(tagResponse.data.tag_statistics)
    
  } catch (error) {
    ElMessage.error('加载组织数据失败')
  }
}

const loadSurveyData = async () => {
  if (!selectedOrganization.value || !selectedSurvey.value) {
    await loadOrganizationData()
    return
  }
  
  try {
    const response = await analyticsAPI.getSurveyTagAnalytics(selectedOrganization.value, selectedSurvey.value)
    tagData.value = response.data.tag_analytics
    
    // 更新概览统计
    updateOverviewStats(response.data)
    
    // 渲染图表
    await nextTick()
    renderCharts(response.data.tag_analytics)
    
  } catch (error) {
    ElMessage.error('加载调研数据失败')
  }
}

const loadTagSummary = async () => {
  if (!selectedOrganization.value) return
  
  try {
    const response = await analyticsAPI.getOrganizationTagSummary(selectedOrganization.value)
    // 合并汇总数据到现有标签数据
    const summaryData = response.data.tag_summary
    tagData.value = tagData.value.map(tag => {
      const summary = summaryData.find(s => s.tag_id === tag.tag_id)
      return {
        ...tag,
        score_stats: summary?.score_stats || null
      }
    })
    
    // 重新渲染图表
    await nextTick()
    renderCharts(tagData.value)
    
  } catch (error) {
    console.error('加载标签汇总数据失败:', error)
  }
}

const updateOverviewStats = (data) => {
  overviewStats.value = [
    { label: '总问题数', value: data.total_questions || 0 },
    { label: '总标签数', value: data.total_tags || 0 },
    { label: '总回答数', value: calculateTotalResponses(data) },
    { label: '平均得分', value: calculateAverageScore(data) }
  ]
}

const calculateTotalResponses = (data) => {
  if (data.tag_analytics) {
    return data.tag_analytics.reduce((sum, tag) => sum + (tag.total_responses || 0), 0)
  } else if (data.tag_statistics) {
    return data.tag_statistics.reduce((sum, tag) => sum + (tag.total_responses || 0), 0)
  }
  return 0
}

const calculateAverageScore = (data) => {
  let totalScore = 0
  let count = 0
  
  const tags = data.tag_analytics || data.tag_statistics || []
  for (const tag of tags) {
    if (tag.score_stats && tag.score_stats.average_score) {
      totalScore += tag.score_stats.average_score
      count += 1
    }
  }
  
  return count > 0 ? (totalScore / count).toFixed(1) + '%' : '-'
}

const renderCharts = (tags) => {
  // 标签分布饼图
  if (tagDistributionChart.value) {
    const chart1 = echarts.init(tagDistributionChart.value)
    const data1 = tags.map(tag => ({
      name: tag.tag_name,
      value: tag.question_count,
      itemStyle: { color: tag.tag_color }
    }))
    
    chart1.setOption({
      title: { text: '标签问题分布', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: data1,
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
        }
      }]
    })
  }
  
  // 标签得分柱状图
  if (tagScoreChart.value) {
    const chart2 = echarts.init(tagScoreChart.value)
    const data2 = tags
      .filter(tag => tag.score_stats && tag.score_stats.average_score)
      .map(tag => ({
        name: tag.tag_name,
        value: tag.score_stats.average_score,
        itemStyle: { color: tag.tag_color }
      }))
    
    chart2.setOption({
      title: { text: '标签平均得分', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data2.map(item => item.name) },
      yAxis: { type: 'value', name: '得分 (%)' },
      series: [{
        type: 'bar',
        data: data2.map(item => item.value),
        itemStyle: { color: '#409EFF' }
      }]
    })
  }
}

const viewTagDetails = (tag) => {
  selectedTagDetail.value = tag
  tagDetailVisible.value = true
  
  // 渲染问题响应图表
  nextTick(() => {
    tag.questions?.forEach(question => {
      if (Object.keys(question.response_distribution).length > 0) {
        const chartRef = document.querySelector(`#response-chart-${question.question_id}`)
        if (chartRef) {
          const chart = echarts.init(chartRef)
          const data = Object.entries(question.response_distribution).map(([key, value]) => ({
            name: key,
            value: value
          }))
          
          chart.setOption({
            tooltip: { trigger: 'item' },
            series: [{
              type: 'pie',
              radius: '50%',
              data: data
            }]
          })
        }
      }
    })
  })
}

const getResponseTableData = (distribution) => {
  const total = Object.values(distribution).reduce((sum, count) => sum + count, 0)
  return Object.entries(distribution).map(([option, count]) => ({
    option,
    count,
    percentage: total > 0 ? ((count / total) * 100).toFixed(1) + '%' : '0%'
  }))
}

const getQuestionTypeLabel = (type) => {
  const typeMap = {
    'SINGLE_CHOICE': '单选题',
    'MULTI_CHOICE': '多选题',
    'TEXT_INPUT': '文本输入',
    'NUMBER_INPUT': '数字输入',
    'SORT_ORDER': '排序题',
    'CONDITIONAL': '关联题'
  }
  return typeMap[type] || type
}

const refreshData = async () => {
  if (selectedSurvey.value) {
    await loadSurveyData()
  } else {
    await loadOrganizationData()
    await loadTagSummary()
  }
}

// 生命周期
onMounted(() => {
  loadOrganizations()
})
</script>

<style scoped>
.tag-analytics {
  padding: 20px;
}

.analytics-card {
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
  align-items: center;
}

.overview-section {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.chart-section {
  margin-bottom: 30px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.table-section {
  margin-bottom: 30px;
}

.tag-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.tag-stats {
  display: flex;
  gap: 20px;
  color: #606266;
}

.questions-section {
  margin-top: 20px;
}

.question-details {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.response-chart {
  margin: 15px 0;
}

.mini-chart {
  width: 100%;
  height: 200px;
}

h4, h5 {
  color: #303133;
  margin-bottom: 15px;
}

:deep(.el-collapse-item__header) {
  background: #f8f9fa;
  margin-bottom: 10px;
  border-radius: 4px;
  padding: 10px 15px;
}
</style>