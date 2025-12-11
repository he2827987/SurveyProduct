<!-- components/AnalysisChart.vue -->
<template>
  <div class="analysis-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-actions">
        <el-button type="primary" link size="small" @click="downloadChart">
          <el-icon><Download /></el-icon>
          下载图表
        </el-button>
        <el-button type="primary" link size="small" @click="refreshChart">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="chart-container" ref="chartContainer">
      <div v-if="chartError" class="chart-error">
        <el-alert
          title="图表渲染错误"
          :description="chartError"
          type="error"
          show-icon
          :closable="false"
        />
        <el-button type="primary" @click="retryRender" style="margin-top: 10px;">
          重试渲染
        </el-button>
      </div>
      <v-chart 
        v-else
        :key="chartKeyValue" 
        :option="chartOption" 
        :style="{ height: height + 'px' }"
        @click="handleChartClick"
      />
    </div>
    
    <!-- 图表说明 -->
    <div v-if="description" class="chart-description">
      <el-icon><InfoFilled /></el-icon>
      <span>{{ description }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { Download, Refresh, InfoFilled } from '@element-plus/icons-vue'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

// ===== Props =====
const props = defineProps({
  type: {
    type: String,
    default: 'pie',
    validator: (value) => ['pie', 'bar', 'line', 'radar'].includes(value)
  },
  data: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  height: {
    type: Number,
    default: 400
  },
  description: {
    type: String,
    default: ''
  },
  // 新增：支持多系列数据
  series: {
    type: Array,
    default: () => []
  },
  // 新增：X轴数据
  xAxisData: {
    type: Array,
    default: () => []
  }
})

// ===== Emits =====
const emit = defineEmits(['chart-click'])

// ===== 响应式数据 =====
const chartContainer = ref(null)
const chartKey = ref(0) // 用于强制重新渲染图表
const chartError = ref(null) // 图表渲染错误

// ===== 计算属性 =====

/**
 * 生成图表组件的key值
 */
const chartKeyValue = computed(() => {
  return `${props.type}-${chartKey.value}-${JSON.stringify(props.data)}`
})

/**
 * 根据图表类型和数据生成ECharts配置
 */
const chartOption = computed(() => {
  const baseOption = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: props.type === 'pie' ? 'item' : 'axis',
      formatter: (params) => {
        if (props.type === 'pie') {
          return `${params.name}<br/>${params.seriesName}: ${params.value} (${params.percent}%)`
        } else {
          const firstLine = params[0].name
          const lines = params.map(item => {
            const label = item.seriesName === '问卷总分' ? '平均分' : item.seriesName
            return `${label}: ${item.value}`
          })
          return `${firstLine}<br/>${lines.join('<br/>')}`
        }
      }
    },
    legend: {
      orient: 'horizontal',
      bottom: 10
    }
  }

  // 检查是否为多系列数据
  const isMultiSeries = props.series && props.series.length > 0

  switch (props.type) {
    case 'pie':
      return {
        ...baseOption,
        series: [{
          name: '数据',
          type: 'pie',
          radius: '50%',
          center: ['50%', '50%'],
          data: props.data.map(item => ({
            name: item.name,
            value: item.value
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
    
    case 'bar':
      if (isMultiSeries) {
        // 多系列柱状图（企业对比）
        return {
          ...baseOption,
          xAxis: {
            type: 'category',
            data: props.xAxisData,
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            max: 100
          },
          series: props.series.map((series, index) => ({
            name: series.name,
            type: 'bar',
            data: series.value,
            itemStyle: {
              color: getSeriesColor(index)
            }
          }))
        }
      } else {
        // 单系列柱状图
        return {
          ...baseOption,
          xAxis: {
            type: 'category',
            data: props.data.map(item => item.name),
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            name: '数量',
            type: 'bar',
            data: props.data.map(item => item.value),
            itemStyle: {
              color: '#409eff'
            }
          }]
        }
      }
    
    case 'line':
      if (isMultiSeries) {
        // 多系列折线图（企业对比）
        return {
          ...baseOption,
          xAxis: {
            type: 'category',
            data: props.xAxisData
          },
          yAxis: {
            type: 'value',
            max: 100
          },
          series: props.series.map((series, index) => ({
            name: series.name,
            type: 'line',
            data: series.value,
            smooth: true,
            itemStyle: {
              color: getSeriesColor(index)
            }
          }))
        }
      } else {
        // 单系列折线图
        return {
          ...baseOption,
          xAxis: {
            type: 'category',
            data: props.data.map(item => item.name)
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            name: '趋势',
            type: 'line',
            data: props.data.map(item => item.value),
            smooth: true,
            itemStyle: {
              color: '#67c23a'
            }
          }]
        }
      }
    
    case 'radar':
      try {
        // 简化的雷达图配置，确保数据格式正确
        let radarData = []
        let maxValue = 10 // 默认最大值
        
        if (props.data && typeof props.data === 'object' && props.data.indicator) {
          // 对象格式数据
          radarData = props.data.series[0]?.value || []
          maxValue = Math.max(...radarData, 10)
        } else if (Array.isArray(props.data)) {
          // 数组格式数据
          radarData = props.data.map(item => item.value || 0)
          maxValue = Math.max(...radarData, 10)
        }
        
        // 确保有数据
        if (!radarData || radarData.length === 0) {
          console.warn('雷达图数据为空，使用默认数据')
          radarData = [5, 8, 6, 7, 9]
          maxValue = 10
        }
        
        const indicator = radarData.map((_, index) => ({
          name: `指标${index + 1}`,
          max: maxValue * 1.2
        }))
        
        return {
          ...baseOption,
          radar: {
            indicator: indicator,
            radius: '60%'
          },
          series: [{
            name: '数据分析',
            type: 'radar',
            data: [{
              value: radarData,
              name: '分析结果'
            }],
            itemStyle: {
              color: '#409eff'
            },
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.2)'
            }
          }]
        }
      } catch (error) {
        console.error('雷达图配置错误:', error)
        // 返回一个简单的默认配置
        return {
          ...baseOption,
          radar: {
            indicator: [
              { name: '指标1', max: 10 },
              { name: '指标2', max: 10 },
              { name: '指标3', max: 10 }
            ],
            radius: '60%'
          },
          series: [{
            name: '数据分析',
            type: 'radar',
            data: [{
              value: [5, 8, 6],
              name: '分析结果'
            }]
          }]
        }
      }
    
    default:
      return baseOption
  }
})

/**
 * 获取系列颜色
 */
const getSeriesColor = (index) => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
  return colors[index % colors.length]
}

// ===== 监听器 =====

/**
 * 监听图表类型变化，强制重新渲染
 */
watch(() => props.type, () => {
  chartKey.value++
  nextTick(() => {
    // 确保DOM更新后再重置图表
    console.log(`图表类型已切换到: ${props.type}`)
    console.log('当前数据:', props.data)
  })
})

/**
 * 监听数据变化，重置图表
 */
watch(() => props.data, () => {
  chartKey.value++
}, { deep: true })

// ===== 方法 =====

/**
 * 处理图表点击事件
 */
const handleChartClick = (params) => {
  emit('chart-click', params)
}

/**
 * 下载图表
 */
const downloadChart = async () => {
  try {
    const chart = chartContainer.value?.querySelector('canvas')
    if (chart) {
      const link = document.createElement('a')
      link.download = `${props.title || 'chart'}.png`
      link.href = chart.toDataURL()
      link.click()
      ElMessage.success('图表下载成功')
    }
  } catch (error) {
    console.error('下载图表失败:', error)
    ElMessage.error('下载图表失败')
  }
}

/**
 * 刷新图表
 */
const refreshChart = () => {
  chartKey.value++
  chartError.value = null
  nextTick(() => {
    ElMessage.success('图表已刷新')
  })
}

/**
 * 重试渲染
 */
const retryRender = () => {
  chartError.value = null
  chartKey.value++
  nextTick(() => {
    ElMessage.success('图表重新渲染')
  })
}
</script>

<style scoped>
.analysis-chart {
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.chart-container {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.chart-description {
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chart-description .el-icon {
  color: #409eff;
}

.chart-error {
  padding: 20px;
  text-align: center;
}
</style>
