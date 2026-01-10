<template>
  <div class="bar-chart-container" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  data: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

const buildOption = () => {
  const categories = props.data.map(item => item.name)
  const totalList = props.data.map(item => item.value || 0)

  // 收集部门/职位维度
  const departments = new Set()
  props.data.forEach(item => {
    if (item.breakdown) {
      item.breakdown.forEach(b => departments.add(b.name))
    }
  })
  const deptList = Array.from(departments)

  const series = []

  // 堆叠柱：每个部门一条 series
  deptList.forEach(dept => {
    series.push({
      name: dept,
      type: 'bar',
      stack: 'total',
      label: {
        show: true,
        position: 'inside',
        formatter: (params) => (params.value > 0 ? params.value : '')
      },
      emphasis: { focus: 'series' },
      data: props.data.map(item => {
        const found = item.breakdown.find(b => b.name === dept)
        return found ? found.value : 0
      })
    })
  })

  // 自定义系列：只绘制总计文本，不影响柱高
  const labelData = totalList.map((v, idx) => [idx, v])
  series.push({
    name: '总计标签',
    type: 'custom',
    renderItem: (params, api) => {
      const categoryIndex = api.value(0)
      const totalValue = api.value(1)
      if (!totalValue) return null
      const point = api.coord([categoryIndex, totalValue])
      return {
        type: 'text',
        position: [point[0], point[1] - 30], // 固定距离 30px 上方
        style: {
          text: totalValue,
          fill: '#333',
          font: '12px sans-serif',
          textAlign: 'center',
          textVerticalAlign: 'bottom'
        }
      }
    },
    data: labelData,
    tooltip: { show: false }
  })

  return {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        let result = `${params[0].name}<br/>`
        params.forEach(param => {
          if (param.seriesName !== '总计标签' && param.value > 0) {
            result += `${param.seriesName}: ${param.value}<br/>`
          }
        })
        return result
      }
    },
    legend: { top: 'bottom' },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value' },
    series
  }
}

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(buildOption())
}

watch(() => props.data, () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})

const handleResize = () => {
  chartInstance && chartInstance.resize()
}
</script>

<style scoped>
.bar-chart-container {
  width: 100%;
  height: 400px;
}
</style>
