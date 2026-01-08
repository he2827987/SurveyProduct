<template>
  <el-dialog
    :title="dialogTitle"
    :visible.sync="visibleLocal"
    width="700px"
    @close="handleClose"
  >
    <div class="filters">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="题号">
          <el-input-number
            v-model="filters.questionNumber"
            :min="1"
            :placeholder="'输入题号'"
          />
        </el-form-item>
        <el-form-item label="题目">
          <el-input
            v-model="filters.questionText"
            placeholder="输入部分题目关键词"
          />
        </el-form-item>
        <el-form-item label="部门">
          <el-input
            v-model="filters.department"
            placeholder="输入部门名称"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            筛选
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="answers"
      v-loading="loading"
      element-loading-text="加载中..."
      style="width: 100%;"
      size="small"
    >
      <el-table-column prop="question_number" label="题号" width="80" />
      <el-table-column prop="question_text" label="题目" min-width="200" />
      <el-table-column prop="answer_text" label="答案" min-width="220" />
      <el-table-column prop="department" label="部门" width="130" />
      <el-table-column prop="respondent_name" label="受访人" width="150" />
      <el-table-column prop="submitted_at" label="提交时间" width="180">
        <template #default="scope">
          {{ formatTime(scope.row.submitted_at) }}
        </template>
      </el-table-column>
    </el-table>

    <div class="empty-block" v-if="!loading && answers.length === 0">
      <el-empty description="暂无主观题答案"></el-empty>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import * as surveyApi from '@/api/survey'

const props = defineProps({
  surveyId: {
    type: [String, Number],
    default: null
  },
  title: {
    type: String,
    default: '主观题详细答案'
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const visibleLocal = ref(false)
const answers = ref([])
const loading = ref(false)
const filters = ref({
  questionNumber: null,
  questionText: '',
  department: ''
})

const dialogTitle = computed(() => `${props.title}`)

const loadAnswers = async () => {
  if (!props.surveyId) return
  loading.value = true
  try {
    const params = {}
    if (filters.value.questionNumber) {
      params.question_number = filters.value.questionNumber
    }
    if (filters.value.questionText) {
      params.question_text = filters.value.questionText.trim()
    }
    if (filters.value.department) {
      params.department = filters.value.department.trim()
    }

    answers.value = await surveyApi.getSubjectiveAnswers(props.surveyId, params)
  } catch (error) {
    console.error('加载主观题答案失败:', error)
    ElMessage.error('加载主观题答案失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (props.surveyId) {
    loadAnswers()
  }
}

const handleClose = () => {
  emit('update:modelValue', false)
}

watch(
  () => props.modelValue,
  (visible) => {
    visibleLocal.value = visible
    if (visible && props.surveyId) {
      loadAnswers()
    }
  }
)

watch(
  () => visibleLocal.value,
  (visible) => {
    emit('update:modelValue', visible)
  }
)

watch(
  () => props.surveyId,
  (surveyId) => {
    if (visibleLocal.value && surveyId) {
      loadAnswers()
    }
  }
)

const formatTime = (value) => {
  if (!value) return '未知'
  return new Date(value).toLocaleString('zh-CN')
}
</script>

<style scoped>
.filters {
  margin-bottom: 12px;
}
.empty-block {
  margin-top: 16px;
  text-align: center;
}
.filter-form {
  width: 100%;
}
.filter-form .el-form-item {
  margin-right: 12px;
}
</style>

