<template>
  <div class="survey-detail-container page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button type="primary" @click="goBack">返回</el-button>
        <h1 class="page-title">主观题详细答案</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refresh" :loading="loading">刷新</el-button>
      </div>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="题号">
          <el-select
            v-model="filters.questionNumber"
            placeholder="（未选择）"
            clearable
            filterable
            style="width: 160px"
          >
            <el-option label="（未选择）" :value="''" />
            <el-option
              v-for="num in questionNumberOptions"
              :key="num"
              :label="`第 ${num} 题`"
              :value="num"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="题目">
          <el-input v-model="filters.questionText" placeholder="题目关键词" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="filters.department" placeholder="部门" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="loadData" :loading="loading">
            筛选
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table
        :data="answers"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        size="small"
      >
        <el-table-column prop="question_number" label="题号" width="90" />
        <el-table-column prop="question_text" label="题目" min-width="220" />
        <el-table-column prop="answer_text" label="答案" min-width="240" />
        <el-table-column prop="department" label="部门" width="140" />
        <el-table-column prop="respondent_name" label="答题人" width="160" />
        <el-table-column prop="submitted_at" label="提交时间" width="200">
          <template #default="scope">
            {{ formatDate(scope.row.submitted_at) }}
          </template>
        </el-table-column>
      </el-table>
      <div class="empty-block" v-if="!loading && answers.length === 0">
        <el-empty description="暂无数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as surveyApi from '@/api/survey'

const route = useRoute()
const router = useRouter()
const surveyId = Number(route.params.id)

const answers = ref([])
const loading = ref(false)
const filters = ref({ questionNumber: '', questionText: '', department: '' })
const questionNumberOptions = ref([])

const loadData = async () => {
  if (!surveyId) return
  loading.value = true
  try {
    const params = {}
    if (filters.value.questionNumber !== '' && filters.value.questionNumber !== null) {
      params.question_number = filters.value.questionNumber
    }
    if (filters.value.questionText) {
      params.question_text = filters.value.questionText.trim()
    }
    if (filters.value.department) {
      params.department = filters.value.department.trim()
    }
    answers.value = await surveyApi.getSubjectiveAnswers(surveyId, params)
    // 构建题号下拉选项（去重+排序）
    const nums = Array.from(new Set(answers.value.map((a) => a.question_number).filter(Boolean)))
    questionNumberOptions.value = nums.sort((a, b) => a - b)
  } catch (error) {
    console.error('加载主观题答案失败:', error)
    ElMessage.error('加载主观题答案失败')
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  loadData()
}

const goBack = () => {
  router.push('/survey')
}

const formatDate = (value) => {
  if (!value) return '未知'
  return new Date(value).toLocaleString('zh-CN')
}

if (surveyId) {
  loadData()
}
</script>

<style scoped>
.survey-detail-container {
  padding: 20px;
}
.filter-form {
  width: 100%;
}
.filter-form .el-form-item {
  margin-right: 12px;
}
.empty-block {
  margin-top: 20px;
  text-align: center;
}
</style>

