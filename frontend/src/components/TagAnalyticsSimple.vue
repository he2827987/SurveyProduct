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
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as analyticsApi from '@/api/analytics'
import * as echarts from 'echarts'

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
    
    overviewStats.value[0].value = mockData.length
    overviewStats.value[1].value = mockData.reduce((sum, tag) => sum + tag.question_count, 0)
    overviewStats.value[2].value = mockData.reduce((sum, tag) => sum + tag.total_score, 0)
    overviewStats.value[3].value = (mockData.reduce((sum, tag) => sum + tag.avg_score, 0) / mockData.length).toFixed(1)
    
    await nextTick()
    renderCharts()
    
    console.log('标签数据加载成功')
  } catch (error) {
    console.error('加载标签数据失败:', error)
    ElMessage.error('加载标签数据失败')
  }
}

const renderCharts = () => {
  if (tagDistributionChart.value && tagData.value.length > 0) {
    const el = tagDistributionChart.value
    if (el.clientWidth === 0 || el.clientHeight === 0) return
    const chartData = tagData.value.map(tag => ({
      name: tag.tag_name,
      value: tag.question_count
    }))
    
    import('echarts').then(echarts => {
      if (el.clientWidth === 0) return
      const chart = echarts.init(el)
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '问题分布',
            type: 'pie',
            radius: '50%',
            data: chartData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      chart.setOption(option)
      
      window.addEventListener('resize', () => {
        chart.resize()
      })
    })
  }
  
  if (tagScoreChart.value && tagData.value.length > 0) {
    const el = tagScoreChart.value
    if (el.clientWidth === 0 || el.clientHeight === 0) return
    const chartData = tagData.value.map(tag => ({
      name: tag.tag_name,
      value: tag.avg_score
    }))
    
    import('echarts').then(echarts => {
      if (el.clientWidth === 0) return
      const chart = echarts.init(el)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: chartData.map(item => item.name)
        },
        series: [
          {
            name: '平均分',
            type: 'bar',
            data: chartData.map(item => item.value),
            itemStyle: {
              color: '#409EFF'
            }
          }
        ]
      }
      chart.setOption(option)
      
      window.addEventListener('resize', () => {
        chart.resize()
      })
    })
  }
}

let chartsRendered = false

onMounted(() => {
  loadTagData()
  // Retry rendering when tab becomes visible
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && !chartsRendered && tagData.value.length > 0) {
      chartsRendered = true
      nextTick(() => renderCharts())
      observer.disconnect()
    }
  })
  nextTick(() => {
    const el = document.querySelector('.tag-analytics')
    if (el) observer.observe(el)
  })
})

const tryRenderCharts = () => {
  if (chartsRendered) return
  if (tagData.value.length > 0 && tagDistributionChart.value && tagDistributionChart.value.clientWidth > 0) {
    chartsRendered = true
    renderCharts()
  }
}
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
  padding: 10px;
}

.table-section {
  margin-bottom: 30px;
}

h4 {
  color: #303133;
  margin-bottom: 15px;
}
</style>