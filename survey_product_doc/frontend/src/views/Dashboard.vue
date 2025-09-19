<!--
  @fileoverview 仪表板页面组件
  @description 系统主页面，显示概览信息
  @author Survey System Team
  @version 1.0.0
  @since 2024-01-01
-->

<template>
  <div class="dashboard-container page-container">
    <h1 class="page-title">系统概览</h1>
    
    <!-- 数据统计卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="data-card">
          <div class="data-card-inner">
            <div class="data-icon bg-blue">
              <el-icon><User /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">总部门数</div>
              <div class="data-value">{{ stats.departmentCount || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="data-card">
          <div class="data-card-inner">
            <div class="data-icon bg-green">
              <el-icon><Document /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">题库数量</div>
              <div class="data-value">{{ stats.questionCount || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="data-card">
          <div class="data-card-inner">
            <div class="data-icon bg-orange">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">调研次数</div>
              <div class="data-value">{{ stats.surveyCount || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="data-card">
          <div class="data-card-inner">
            <div class="data-icon bg-purple">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="data-info">
              <div class="data-title">答题人次</div>
              <div class="data-value">{{ stats.respondentCount || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速入口 -->
    <div class="card quick-entry">
      <h2 class="section-title">快速入口</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="entry in quickEntries" :key="entry.path">
          <el-card shadow="hover" class="entry-card" @click="goTo(entry.path)">
            <div class="entry-icon">
              <el-icon><component :is="entry.icon" /></el-icon>
            </div>
            <div class="entry-title">{{ entry.title }}</div>
            <div class="entry-desc">{{ entry.description }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 最近调研 -->
    <div class="card recent-surveys">
      <div class="flex-between">
        <h2 class="section-title">最近调研</h2>
        <el-button type="primary" plain size="small" @click="goTo('/survey')">
          查看全部
        </el-button>
      </div>
      
      <el-table :data="recentSurveys" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="调研标题" min-width="200"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '进行中' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        <el-table-column prop="count" label="答题人数" width="100" align="center"></el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="viewSurvey(scope.row.id)">
              查看详情
            </el-button>
            <el-button type="primary" link size="small" @click="viewAnalysis(scope.row.id)">
              数据分析
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="empty-block" v-if="recentSurveys.length === 0 && !loading">
        <el-empty description="暂无调研数据"></el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, 
  Document, 
  Edit, 
  UserFilled, 
  OfficeBuilding, 
  PieChart, 
  DataAnalysis,
  Setting,
  Histogram
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

// 统计数据
const stats = ref({
  departmentCount: 5,
  questionCount: 36,
  surveyCount: 12,
  respondentCount: 240
})

// 快速入口
const quickEntries = [
  {
    title: '组织架构管理',
    description: '管理公司部门结构',
    icon: 'OfficeBuilding',
    path: '/organization'
  },
  {
    title: '题库管理',
    description: '创建和编辑调研题目',
    icon: 'Document',
    path: '/question'
  },
  {
    title: '发起调研',
    description: '创建新的调研任务',
    icon: 'Edit',
    path: '/survey'
  },
  {
    title: '数据分析',
    description: '查看调研结果分析',
    icon: 'Histogram',
    path: '/analysis'
  },
  {
    title: '企业对比',
    description: '多企业调研数据对比',
    icon: 'PieChart',
    path: '/compare'
  }
]

// 最近调研
const recentSurveys = ref([
  {
    id: 1,
    title: '2023年员工满意度调查',
    status: '已完成',
    created_at: '2023-12-15 14:30',
    count: 85
  },
  {
    id: 2,
    title: '新产品市场反馈收集',
    status: '进行中',
    created_at: '2024-01-10 09:15',
    count: 42
  },
  {
    id: 3,
    title: '研发部工作环境评估',
    status: '进行中',
    created_at: '2024-02-05 16:20',
    count: 18
  }
])

// 页面加载时获取数据
onMounted(() => {
  getDashboardData()
})

// 获取仪表盘数据
const getDashboardData = async () => {
  loading.value = true
  try {
    // 实际项目中这里应该调用接口获取数据
    // const res = await api.getDashboardData()
    // stats.value = res.stats
    // recentSurveys.value = res.recentSurveys
    
    // 模拟延迟
    setTimeout(() => {
      loading.value = false
    }, 500)
  } catch (error) {
    console.error(error)
    loading.value = false
  }
}

// 页面跳转
const goTo = (path) => {
  router.push(path)
}

// 查看调研详情
const viewSurvey = (id) => {
  router.push(`/survey?id=${id}`)
}

// 查看数据分析
const viewAnalysis = (id) => {
  router.push(`/analysis?id=${id}`)
}
</script>

<style scoped>
.dashboard-container {
  padding-bottom: 40px;
}

/* 数据卡片样式 */
.data-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.data-card-inner {
  display: flex;
  align-items: center;
}

.data-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  font-size: 24px;
  color: #fff;
}

.bg-blue {
  background-color: #409EFF;
}

.bg-green {
  background-color: #67C23A;
}

.bg-orange {
  background-color: #E6A23C;
}

.bg-purple {
  background-color: #909399;
}

.data-info {
  flex: 1;
}

.data-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.data-value {
  font-size: 22px;
  font-weight: bold;
  color: #303133;
}

/* 快速入口样式 */
.section-title {
  font-size: 18px;
  margin-bottom: 20px;
  font-weight: 600;
  color: #303133;
}

.quick-entry {
  margin-top: 20px;
}

.entry-card {
  margin-bottom: 20px;
  cursor: pointer;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.3s;
}

.entry-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.entry-icon {
  font-size: 28px;
  margin-bottom: 10px;
  color: #409EFF;
}

.entry-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.entry-desc {
  font-size: 12px;
  color: #909399;
}

/* 最近调研样式 */
.recent-surveys {
  margin-top: 20px;
}

.empty-block {
  margin: 30px 0;
}
</style> 