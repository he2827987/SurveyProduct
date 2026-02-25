<!-- TagAnalyticsSimple.vue - 标签分析组件 -->
<template>
  <div class="tag-analytics">
    <el-card class="analytics-card">
      <template #header>
        <div class="card-header">
          <h3>标签统计分析</h3>
          <el-button type="primary" @click="loadTagData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
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
            <div class="chart-container" ref="tagDistributionChart"></div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container" ref="tagScoreChart"></div>
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
          <el-table-column prop="total_score" label="总分数" width="100" />
          <el-table-column prop="avg_score" label="平均分" width="100">
            <template #default="{ row }">
              <span v-if="row.avg_score">{{ row.avg_score.toFixed(1) }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as analyticsApi from '@/api/analytics'

const tagData = ref([])
const overviewStats = ref([
  { label: '总标签数', value: 0 },
  { label: '总问题数', value: 0 },
  { label: '总回答数', value: 0 },
  { label: '平均分数', value: 0 }
])

const tagDistributionChart = ref(null)
const tagScoreChart = ref(null)

const loadTagData = async () => {
  try {
    // 模拟API调用，实际应该调用后端API
    const mockData = [
      {
        tag_id: 1,
        tag_name: '工作环境',
        tag_color: '#409EFF',
        question_count: 15,
        total_score: 680,
        avg_score: 85.5
      },
      {
        tag_id: 2,
        tag_name: '薪资福利',
        tag_color: '#67C23A',
        question_count: 12,
        total_score: 540,
        avg_score: 75.0
      },
      {
        tag_id: 3,
        tag_name: '团队协作',
        tag_color: '#E6A23C',
        question_count: 8,
        total_score: 420,
        avg_score: 70.0
      }
    ]
    
    tagData.value = mockData
    
    // 更新概览统计
    overviewStats.value[0].value = mockData.length
    overviewStats.value[1].value = mockData.reduce((sum, tag) => sum + tag.question_count, 0)
    overviewStats.value[2].value = mockData.reduce((sum, tag) => sum + tag.total_score, 0)
    overviewStats.value[3].value = (mockData.reduce((sum, tag) => sum + tag.avg_score, 0) / mockData.length).toFixed(1)
    
    // 渲染图表
    renderCharts()
    
    ElMessage.success('标签数据加载成功')
  } catch (error) {
    console.error('加载标签数据失败:', error)
    ElMessage.error('加载标签数据失败')
  }
}

const renderCharts = () => {
  // 渲染标签分布饼图
  if (tagDistributionChart.value && tagData.value.length > 0) {
    const chartData = tagData.value.map(tag => ({
      name: tag.tag_name,
      value: tag.question_count
    }))
    
    // 使用简单的DOM操作创建图表（不依赖ECharts）
    const chartHtml = `
      <div style="width: 100%; height: 300px; text-align: center; line-height: 300px; background: #f5f5f5; border-radius: 4px;">
        <div style="font-weight: bold; margin-bottom: 10px;">标签问题分布</div>
        ${chartData.map(item => 
          `<div style="display: inline-block; margin: 0 10px;">
            <div style="font-size: 12px;">${item.name}</div>
            <div style="font-weight: bold; color: #409EFF;">${item.value}</div>
          </div>`
        ).join('')}
      </div>
    `
    
    tagDistributionChart.value.innerHTML = chartHtml
  }
  
  // 渲染标签分数柱状图
  if (tagScoreChart.value && tagData.value.length > 0) {
    const chartData = tagData.value.map(tag => ({
      name: tag.tag_name,
      value: tag.avg_score
    }))
    
    const maxScore = Math.max(...chartData.map(item => item.value))
    
    const chartHtml = `
      <div style="width: 100%; height: 300px; text-align: center; background: #f5f5f5; border-radius: 4px;">
        <div style="font-weight: bold; margin-bottom: 10px;">标签平均分数</div>
        ${chartData.map(item => {
          const widthPercent = (item.value / maxScore) * 80
          return `<div style="display: inline-block; margin: 0 5px; width: ${widthPercent}px; height: 20px; background: #409EFF; color: white; line-height: 20px; font-size: 12px;">
            ${item.name}: ${item.value.toFixed(1)}
          </div>`
        }).join('')}
      </div>
    `
    
    tagScoreChart.value.innerHTML = chartHtml
  }
}

onMounted(() => {
  // 初始化
  loadTagData()
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
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 20px;
}

.table-section {
  margin-bottom: 30px;
}

h4 {
  color: #303133;
  margin-bottom: 15px;
}
</style>