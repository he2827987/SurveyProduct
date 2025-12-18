<!-- 
  调研管理页面 (Survey Management Page)
  功能：展示调研列表、创建新调研、管理调研状态、生成二维码、查看数据分析
-->
<template>
  <div class="survey-container page-container">
    <!-- 页面头部：标题和操作按钮 -->
    <div class="flex-between">
      <h1 class="page-title">调研管理</h1>
      <div class="header-actions">
        <el-radio-group v-model="viewMode" @change="handleViewModeChange">
          <el-radio-button label="my">我的调研</el-radio-button>
          <el-radio-button label="global">全局调研库</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="openCreateSurveyDialog()">创建调研</el-button>
      </div>
    </div>
    
    <div class="survey-content">
      <!-- 搜索和筛选区域 -->
      <div class="card search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索调研标题"
          clearable
          class="search-input"
        >
          <template #append>
            <el-button :icon="Search" @click="searchSurveys" />
          </template>
        </el-input>
        
        <div class="filters">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable class="filter-select">
            <el-option label="全部状态" value="" />
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="completed" />
            <el-option label="未开始" value="pending" />
          </el-select>
          
          <el-select v-model="sortBy" placeholder="排序方式" class="filter-select">
            <el-option label="创建时间降序" value="created_desc" />
            <el-option label="创建时间升序" value="created_asc" />
            <el-option label="回复数量降序" value="responses_desc" />
          </el-select>
        </div>
      </div>
      
      <!-- 调研列表展示区域 -->
      <div class="card survey-list">
        <!-- 空状态：当没有数据且不在加载时显示 -->
        <el-empty description="暂无数据" v-if="surveyList.length === 0 && !loading"></el-empty>
        
        <!-- 数据加载状态和表格内容 -->
        <div v-loading="loading" element-loading-text="加载中...">
          <!-- 调研列表表格 -->
          <el-table :data="surveyList" style="width: 100%">
            <el-table-column prop="title" label="调研标题" min-width="250"></el-table-column>
            
            <!-- 调研状态列：显示调研的当前状态（进行中/已结束/未开始） -->
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getSurveyStatusType(scope.row.status)">
                  {{ getSurveyStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            
        <el-table-column prop="question_count" label="题目数量" width="100" align="center"></el-table-column>
        <el-table-column prop="response_count" label="回复数量" width="100" align="center"></el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="160"></el-table-column>
            
            <!-- 操作列：提供查看、生成二维码、数据分析、删除等操作 -->
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="scope">
                <!-- 查看调研详情 -->
                <el-button type="primary" link @click="viewSurvey(scope.row)">
                  查看
                </el-button>
                
                <!-- 生成二维码：仅对未完成的调研显示，且只有创建者可以操作 -->
                <el-button 
                  v-if="scope.row.status !== 'completed' && scope.row.isCreator" 
                  type="success" 
                  link 
                  @click="generateQrCode(scope.row)"
                >
                  生成二维码
                </el-button>
                
                <!-- 查看数据分析 -->
                <el-button type="warning" link @click="viewAnalysis(scope.row)">
                  数据分析
                </el-button>
                
                <!-- 主观答案 -->
                <el-button type="primary" link @click="openSubjectiveAnswers(scope.row)">
                  详细答案
                </el-button>
                
                <!-- 编辑调研：点击时验证权限 -->
                <el-button
                  type="info"
                  link
                  @click="editSurvey(scope.row)"
                >
                  编辑
                </el-button>
                
                <!-- 删除调研：仅对未完成的调研显示，点击时验证权限 -->
                <el-popconfirm
                  v-if="scope.row.status !== 'completed'"
                  title="确定要删除此调研吗？"
                  @confirm="deleteSurvey(scope.row)"
                  confirm-button-text="确定"
                  cancel-button-text="取消"
                >
                  <template #reference>
                    <el-button type="danger" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页组件：支持页码跳转和每页数量调整 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="totalSurveys"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建调研对话框：用于创建新的调研项目 -->
    <el-dialog
      v-model="createDialog.visible"
      :title="createDialog.title"
      width="650px"
      @close="handleDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="调研标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入调研标题" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入调研描述"
          />
        </el-form-item>
        
        <!-- 题目选择区域：从题库中选择调研题目 -->
        <el-divider content-position="left">题目选择</el-divider>
        
        <el-tabs v-model="activeTab" class="demo-tabs">
          <!-- 题库选择标签页：从现有题库中选择题目 -->
          <el-tab-pane label="题库选择" name="library">
            <div class="question-selection">
              <!-- 题目分类侧边栏：按分类筛选题目 -->
              <div class="question-categories">
                <div class="category-list">
                  <div
                    v-for="category in categories"
                    :key="category.id || 'all'"
                    class="category-item"
                    :class="{ active: currentCategoryId === category.id }"
                    @click="selectCategory(category.id)"
                  >
                    {{ category.name }}
                  </div>
                </div>
              </div>
              
              <!-- 题目列表区域：显示可选择的题目 -->
              <div class="question-list">
                <!-- 全选/取消全选复选框 -->
                <el-checkbox
                  v-model="selectAll"
                  @change="handleSelectAllChange"
                >
                  全选/取消全选
                </el-checkbox>
                
                <!-- 调试按钮 -->
                <el-button @click="debugSelection" size="small" style="margin-left: 10px;">
                  调试
                </el-button>
                
                <el-divider />
                
                <!-- 题目选择复选框组 -->
                <div class="question-checkbox-group">
                  <!-- 遍历显示每个题目选项 -->
                  <div
                    v-for="question in libraryQuestions"
                    :key="question.id"
                    class="question-checkbox-item"
                  >
                    <label class="question-checkbox-label">
                      <input 
                        type="checkbox" 
                        :value="question.id"
                        v-model="selectedQuestions"
                        @change="onQuestionChange(question.id)"
                      >
                      <div class="question-item">
                        <!-- 题目类型标签：显示题目类型（单选/多选/填空） -->
                        <div class="question-type-tag">
                          <el-tag :type="getQuestionTypeTag(question.type).type" size="small">
                            {{ getQuestionTypeTag(question.type).label }}
                          </el-tag>
                        </div>
                        <!-- 题目标题 -->
                        <div class="question-title">{{ question.text }}</div>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="createSurvey" :disabled="selectedQuestions.length === 0">
            {{ createDialog.isEdit ? '完成编辑' : '创建调研' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 二维码对话框：显示调研的二维码，用于分享和填写 -->
    <el-dialog
      v-model="qrDialog.visible"
      :title="qrDialog.title"
      width="500px"
      align-center
    >
      <QRCodeGenerator
        :survey-id="qrDialog.surveyId"
        :survey-title="qrDialog.title"
        :survey-description="qrDialog.description"
        :response-count="qrDialog.responseCount"
      />
    </el-dialog>
    
    <SubjectiveAnswersDialog
      v-model:visible="subjectiveDialog.visible"
      :survey-id="subjectiveDialog.surveyId"
      :title="subjectiveDialog.title"
    />
  </div>
</template>

<script setup>
// ===== 导入依赖 =====
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import * as surveyApi from '@/api/survey'
import * as questionApi from '@/api/question'
import QRCodeGenerator from '@/components/QRCodeGenerator.vue'
import SubjectiveAnswersDialog from '@/components/SubjectiveAnswersDialog.vue'

// ===== 路由和基础状态 =====
const router = useRouter()
const route = useRoute()

// ===== 列表相关状态 =====
const loading = ref(false) // 加载状态
const searchQuery = ref('') // 搜索关键词
const statusFilter = ref('') // 状态筛选
const sortBy = ref('created_desc') // 排序方式
const currentPage = ref(1) // 当前页码
const pageSize = ref(10) // 每页数量
const totalSurveys = ref(0) // 总调研数量
const viewMode = ref('my') // 视图模式：'my' 我的调研，'global' 全局调研库

// 调研列表数据
const surveyList = ref([])
const subjectiveDialog = ref({
  visible: false,
  surveyId: null,
  title: ''
})

// ===== 创建调研对话框相关状态 =====
const createDialog = ref({
  visible: false,
  title: '创建调研',
  isEdit: false,
  editId: null
})

// 创建表单
const createFormRef = ref(null)
const createForm = ref({
  title: '',
  description: ''
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入调研标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// ===== 题目选择相关状态 =====
const activeTab = ref('library') // 当前激活的标签页
const currentCategoryId = ref(null) // 当前选中的分类ID，null表示全部
const selectAll = ref(false) // 是否全选
const selectedQuestions = ref([]) // 已选择的题目ID列表

// 监听选择变化
watch(selectedQuestions, (newVal) => {
  console.log('选择变化:', newVal)
}, { deep: true })

// 题库分类数据
const categories = ref([
  { id: null, name: '全部' },
  { id: 1, name: '满意度调查' },
  { id: 2, name: '产品反馈' },
  { id: 3, name: '工作环境' },
  { id: 4, name: '薪资福利' }
])

// 题库问题列表
const libraryQuestions = ref([]) // 从后端获取的题目列表
const questionLoading = ref(false) // 题目加载状态

// ===== API 调用函数 =====

/**
 * 获取全局题库题目
 * @param {number|null} categoryId - 分类ID，用于筛选特定分类的题目
 * @param {string|null} questionType - 题目类型，用于筛选特定类型的题目
 */
const fetchGlobalQuestions = async (categoryId = null, questionType = null) => {
  questionLoading.value = true
  try {
    console.log('获取题库题目...')
    
    // 构造查询参数
    const params = {
      skip: 0,
      limit: 100 // 获取更多题目供选择
    }
    
    // 添加分类筛选参数
    if (categoryId !== null && categoryId !== undefined) {
      params.category_id = categoryId
    }
    
    // 添加类型筛选参数
    if (questionType) {
      params.type = questionType
    }
    
    const response = await questionApi.getGlobalQuestions(params)
    
    // 处理响应数据
    if (response && response.items) {
      libraryQuestions.value = response.items.map(question => ({
        id: question.id,
        text: question.text,
        type: question.type, // 保持原始类型
        category_id: question.category_id,
        tags: question.tags || []
      }))
    } else if (Array.isArray(response)) {
      libraryQuestions.value = response.map(question => ({
        id: question.id,
        text: question.text,
        type: question.type, // 保持原始类型
        category_id: question.category_id,
        tags: question.tags || []
      }))
    } else {
      libraryQuestions.value = []
    }
    
    console.log('题库题目:', libraryQuestions.value)
    console.log('题目数量:', libraryQuestions.value.length)
    if (libraryQuestions.value.length > 0) {
      console.log('第一个题目:', libraryQuestions.value[0])
    }
  } catch (error) {
    console.error('获取题库题目失败:', error)
    ElMessage.error('获取题库题目失败: ' + (error.message || '未知错误'))
    libraryQuestions.value = []
  } finally {
    questionLoading.value = false
  }
}

// ===== 二维码对话框状态 =====
const qrDialog = ref({
  visible: false, // 对话框显示状态
  title: '', // 调研标题
  surveyId: null, // 调研ID
  description: '', // 调研描述
  responseCount: 0 // 答题人数
})

// ===== 生命周期钩子 =====

/**
 * 页面加载时初始化数据
 */
// 监听路由查询参数变化
watch(() => route.query.edit, (newEditId) => {
  if (newEditId) {
    openEditSurveyDialog(newEditId)
  }
})

onMounted(() => {
  fetchSurveys() // 获取调研列表
  fetchGlobalQuestions() // 获取题库题目

  // 检查是否处于编辑模式
  const editId = route.query.edit
  if (editId) {
    openEditSurveyDialog(editId)
  }
})

/**
 * 获取调研列表
 * 支持分页、搜索、筛选等功能
 */
const fetchSurveys = async () => {
  loading.value = true
  try {
    console.log('获取调研列表...', viewMode.value)
    
    // 构造查询参数
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    // 添加搜索参数
    if (searchQuery.value && searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    
    // 添加状态筛选参数
    if (statusFilter.value) {
      params.status_filter = statusFilter.value
    }
    
    // 添加排序参数
    if (sortBy.value) {
      params.sort_by = sortBy.value
    }
    
    // 根据视图模式选择API
    let response
    if (viewMode.value === 'global') {
      response = await surveyApi.getGlobalSurveys(params)
    } else {
      response = await surveyApi.getSurveys(params)
    }
    
    // 处理响应数据
    if (Array.isArray(response)) {
      // 获取当前用户ID（从localStorage或token中获取）
      const currentUserId = getCurrentUserId()
      
      surveyList.value = response.map(survey => ({
        id: survey.id,
        title: survey.title,
        description: survey.description || '',
        status: survey.status || 'pending',
        question_count: survey.question_count ?? (survey.questions?.length || 0),
        response_count: survey.response_count ?? (survey.answers?.length || 0),
        createdAt: survey.created_at,
        created_by_user_id: survey.created_by_user_id,
        organization_id: survey.organization_id,
        // 判断当前用户是否是创建者
        isCreator: survey.created_by_user_id === currentUserId
      }))
      totalSurveys.value = surveyList.value.length
    } else {
      surveyList.value = []
      totalSurveys.value = 0
    }
    
    console.log('处理后的调研列表:', surveyList.value)
    console.log('总数:', totalSurveys.value)
  } catch (error) {
    console.error('获取调研列表失败:', error)
    ElMessage.error('获取调研列表失败: ' + (error.message || '未知错误'))
    surveyList.value = []
    totalSurveys.value = 0
  } finally {
    loading.value = false
  }
}

// ===== 工具函数 =====

/**
 * 获取当前用户ID
 * @returns {number|null} 当前用户ID
 */
const getCurrentUserId = () => {
  try {
    // 从localStorage获取用户信息
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      return user.id
    }
    return null
  } catch (error) {
    console.error('获取用户ID失败:', error)
    return null
  }
}

// ===== 列表操作函数 =====

/**
 * 处理视图模式切换
 * @param {string} mode - 新的视图模式
 */
const handleViewModeChange = (mode) => {
  viewMode.value = mode
  currentPage.value = 1
  fetchSurveys()
}

/**
 * 搜索调研
 * 重置到第一页并重新获取数据
 */
const searchSurveys = () => {
  currentPage.value = 1
  fetchSurveys()
}

/**
 * 处理每页数量变化
 * @param {number} size - 新的每页数量
 */
const handleSizeChange = (size) => {
  pageSize.value = size
  fetchSurveys()
}

/**
 * 处理当前页码变化
 * @param {number} page - 新的页码
 */
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchSurveys()
}

/**
 * 处理题目选择变化
 * @param {Array} selection - 选中的题目列表
 */
const handleQuestionSelectionChange = (selection) => {
  selectedQuestions.value = selection.map(q => q.id)
  console.log('选中的题目:', selectedQuestions.value)
}

/**
 * 切换题目选择状态
 * @param {Object} question - 题目对象
 */
const toggleQuestionSelection = (question) => {
  const index = selectedQuestions.value.indexOf(question.id)
  if (index > -1) {
    selectedQuestions.value.splice(index, 1)
  } else {
    selectedQuestions.value.push(question.id)
  }
  console.log('选中的题目:', selectedQuestions.value)
}

/**
 * 调试函数：检查选择状态
 */
const debugSelection = () => {
  console.log('=== 调试信息 ===')
  console.log('题目列表:', libraryQuestions.value)
  console.log('已选择题目:', selectedQuestions.value)
  console.log('题目数量:', libraryQuestions.value.length)
  console.log('选择数量:', selectedQuestions.value.length)
}

/**
 * 题目选择变化处理
 * @param {number} questionId - 题目ID
 */
const onQuestionChange = (questionId) => {
  console.log('题目选择变化:', questionId)
  console.log('当前选择:', selectedQuestions.value)
}

// ===== 工具函数 =====

/**
 * 将后端题目类型映射为前端显示类型
 * @param {string} backendType - 后端题目类型
 * @returns {string} 前端显示类型
 */
const mapQuestionTypeForUI = (backendType) => {
  const typeMap = {
    'single_choice': 'single',
    'multi_choice': 'multiple',
    'text_input': 'text',
    'number_input': 'number'
  }
  return typeMap[backendType] || backendType
}

/**
 * 获取调研状态的中文标签
 * @param {string} status - 状态值
 * @returns {string} 中文状态标签
 */
const getSurveyStatusLabel = (status) => {
  const statusMap = {
    'active': '进行中',
    'completed': '已结束',
    'pending': '未开始'
  }
  return statusMap[status] || '未知'
}

/**
 * 获取调研状态对应的Element Plus标签类型
 * @param {string} status - 状态值
 * @returns {string} 标签类型（success/info/warning）
 */
const getSurveyStatusType = (status) => {
  const statusTypeMap = {
    'active': 'success',
    'completed': 'info',
    'pending': 'warning'
  }
  return statusTypeMap[status] || 'info'
}

// ===== 调研操作函数 =====

/**
 * 查看调研详情
 * @param {Object} survey - 调研对象
 */
const viewSurvey = (survey) => {
  router.push(`/surveys/${survey.id}`)
}

/**
 * 生成调研二维码
 * @param {Object} survey - 调研对象
 */
const generateQrCode = (survey) => {
  qrDialog.value.title = survey.title
  qrDialog.value.surveyId = survey.id
  qrDialog.value.description = survey.description || ''
  qrDialog.value.responseCount = survey.response_count || 0
  qrDialog.value.visible = true
}

/**
 * 下载二维码
 */
const downloadQrCode = () => {
  // 这个方法现在由QRCodeGenerator组件处理
  qrDialog.value.visible = false
}

/**
 * 查看数据分析
 * @param {Object} survey - 调研对象
 */
const viewAnalysis = (survey) => {
  router.push(`/analysis?id=${survey.id}`)
}

const openSubjectiveAnswers = (survey) => {
  subjectiveDialog.value = {
    visible: true,
    surveyId: survey.id,
    title: survey.title
  }
}

/**
 * 编辑调研
 * @param {Object} survey - 调研对象
 */
const editSurvey = (survey) => {
  // 检查权限
  /*
  if (!survey.isCreator) {
    ElMessage.error('只有创建者可以编辑调研')
    return
  }
  */
  // 跳转到编辑模式（复用创建对话框）
  router.push(`/survey?edit=${survey.id}`)
}

/**
 * 删除调研
 * @param {Object} surveyToDelete - 要删除的调研对象
 */
const deleteSurvey = async (surveyToDelete) => {
  try {
    /*
    // 检查权限
    if (!surveyToDelete.isCreator) {
      ElMessage.error('只有创建者可以删除调研')
      return
    }
    */
    // 调用API删除调研
    await surveyApi.deleteSurvey(surveyToDelete.id)
    ElMessage.success(`调研"${surveyToDelete.title}"已删除`)
    
    // 从本地列表中移除
    const index = surveyList.value.findIndex(s => s.id === surveyToDelete.id)
    if (index !== -1) {
      surveyList.value.splice(index, 1)
      // 如果当前页变空且不是第一页，回到上一页
      if (surveyList.value.length === 0 && currentPage.value > 1) {
        currentPage.value = currentPage.value - 1
      }
    }
  } catch (error) {
    console.error('删除调研失败:', error)
    // 根据错误状态码显示不同的错误信息
    if (error.response && error.response.status === 403) {
      ElMessage.error('删除失败：无权限')
    } else if (error.response && error.response.status === 404) {
      ElMessage.error('删除失败：调研不存在')
      // 从列表中移除不存在的调研
      const index = surveyList.value.findIndex(s => s.id === surveyToDelete.id)
      if (index !== -1) surveyList.value.splice(index, 1)
    } else {
      ElMessage.error('删除调研失败')
    }
  }
}

// ===== 创建调研相关函数 =====

/**
 * 打开创建调研对话框
 * 重置表单和选择状态
 */
const openCreateSurveyDialog = () => {
  createDialog.value.visible = true
  createDialog.value.title = '创建调研'
  createDialog.value.isEdit = false
  createDialog.value.editId = null
  // 重置表单数据
  createForm.value = {
    title: '',
    description: ''
  }
  // 重置选择状态
  selectedQuestions.value = []
  selectAll.value = false
}

/**
 * 打开编辑调研对话框
 * 加载要编辑的调研数据
 * @param {string|number} surveyId - 要编辑的调研ID
 */
const openEditSurveyDialog = async (surveyId) => {
  try {
    loading.value = true

    // 获取调研基本信息
    const surveyData = await surveyApi.getSurveyById(surveyId)
    console.log('编辑调研数据:', surveyData)

    // 获取调研的题目列表
    const questionsData = await surveyApi.getSurveyQuestions(surveyId)
    console.log('调研题目数据:', questionsData)

    // 填充表单数据
    createForm.value = {
      title: surveyData.title || '',
      description: surveyData.description || ''
    }

    // 设置已选择的题目
    selectedQuestions.value = questionsData ? questionsData.map(q => q.id) : []
    selectAll.value = false

    // 设置对话框为编辑模式
    createDialog.value.title = '编辑调研'
    createDialog.value.isEdit = true
    createDialog.value.editId = surveyId
    createDialog.value.visible = true

    ElMessage.success('已加载调研数据，可进行编辑')
  } catch (error) {
    console.error('加载编辑数据失败:', error)
    ElMessage.error('加载调研数据失败，无法编辑')
  } finally {
    loading.value = false
  }
}

/**
 * 选择题目分类
 * @param {number|null} categoryId - 分类ID，null表示全部
 */
const selectCategory = (categoryId) => {
  currentCategoryId.value = categoryId
  // 根据分类筛选题目列表
  fetchGlobalQuestions(categoryId)
}

/**
 * 处理全选/取消全选
 * @param {boolean} val - 是否全选
 */
const handleSelectAllChange = (val) => {
  if (val) {
    // 全选：将所有题目的ID添加到选择列表
    selectedQuestions.value = libraryQuestions.value.map(q => q.id)
  } else {
    // 取消全选：清空选择列表
    selectedQuestions.value = []
  }
}

/**
 * 处理对话框关闭
 * 清理URL参数
 */
const handleDialogClose = () => {
  // 如果是编辑模式，清理URL中的edit参数
  if (createDialog.value.isEdit) {
    router.replace('/survey')
  }
}

/**
 * 创建或更新调研
 * 验证表单数据，调用API创建或更新调研，并更新UI
 */
const createSurvey = async () => {
  // 验证表单数据
  const valid = await createFormRef.value.validate()
  if (valid && selectedQuestions.value.length > 0) {
    try {
      const isEdit = createDialog.value.isEdit
      console.log(isEdit ? '更新调研...' : '创建调研...')

      // 构造调研数据
      const surveyData = {
        title: createForm.value.title,
        description: createForm.value.description,
        question_ids: selectedQuestions.value
      }

      let response
      if (isEdit) {
        // 编辑模式：调用更新API
        response = await surveyApi.updateSurvey(createDialog.value.editId, surveyData)
        console.log('更新调研成功:', response)
        ElMessage.success('调研更新成功')
      } else {
        // 创建模式：调用创建API
        response = await surveyApi.createSurvey(surveyData)
        console.log('创建调研成功:', response)
        ElMessage.success('调研创建成功')
      }

      // 重新获取调研列表
      await fetchSurveys()

      // 重置表单和选择
      createForm.value = {
        title: '',
        description: ''
      }
      selectedQuestions.value = []

      // 关闭对话框
      createDialog.value.visible = false

      // 清除URL中的edit参数
      if (isEdit) {
        router.replace('/survey')
      }
    } catch (error) {
      console.error(isEdit ? '更新调研失败:' : '创建调研失败:', error)
      ElMessage.error((isEdit ? '更新' : '创建') + '调研失败: ' + (error.message || '未知错误'))
    }
  } else if (selectedQuestions.value.length === 0) {
    ElMessage.warning('请至少选择一个题目')
  }
}

/**
 * 获取题目类型对应的标签配置
 * @param {string} type - 题目类型
 * @returns {Object} 包含label和type的对象
 */
const getQuestionTypeTag = (type) => {
  const types = {
    'single': { label: '单选题', type: 'primary' },
    'multiple': { label: '多选题', type: 'success' },
    'text': { label: '填空题', type: 'warning' },
    'number': { label: '数字题', type: 'info' },
    'single_choice': { label: '单选题', type: 'primary' },
    'multi_choice': { label: '多选题', type: 'success' },
    'text_input': { label: '填空题', type: 'warning' },
    'number_input': { label: '数字题', type: 'info' }
  }
  return types[type] || { label: '未知', type: 'info' }
}
</script>

<style scoped>
/* ===== 页面布局样式 ===== */

/* 调研内容区域 */
.survey-content {
  margin-top: 20px;
}

/* 头部操作区域 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 视图模式切换按钮组 */
.header-actions .el-radio-group {
  margin-right: 16px;
}

/* ===== 搜索和筛选区域样式 ===== */

/* 搜索栏容器 */
.search-bar {
  margin-bottom: 20px;
  padding: 15px;
}

/* 搜索输入框 */
.search-input {
  margin-bottom: 15px;
}

/* 筛选器容器 */
.filters {
  display: flex;
  gap: 10px;
}

/* 筛选下拉框 */
.filter-select {
  width: 150px;
}

/* ===== 题目相关样式 ===== */

/* 题目项容器 */
.question-item {
  display: flex;
  align-items: flex-start;
}

/* 题目类型标签 */
.question-type-tag {
  margin-right: 8px;
  flex-shrink: 0;
}

/* 题目标题 */
.question-title {
  word-break: break-word;
}

/* ===== 分页样式 ===== */

/* 分页容器 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* ===== 题目选择区域样式 ===== */

/* 题目选择容器 */
.question-selection {
  display: flex;
  height: 350px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

/* 题目分类侧边栏 */
.question-categories {
  width: 180px;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
}

/* 分类列表 */
.category-list {
  padding: 10px 0;
}

/* 分类项 */
.category-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.3s;
}

/* 分类项悬停效果 */
.category-item:hover {
  background-color: #f5f7fa;
}

/* 激活状态的分类项 */
.category-item.active {
  background-color: #ecf5ff;
  color: #409EFF;
  font-weight: bold;
}

/* 题目列表区域 */
.question-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

/* 题目复选框项 */
.question-checkbox-item {
  margin-bottom: 10px;
}

/* 题目选择复选框组 */
.question-checkbox-group {
  margin-top: 10px;
}

/* 题目选择标签 */
.question-checkbox-label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.question-checkbox-label:hover {
  background-color: #f5f7fa;
}

.question-checkbox-label input[type="checkbox"] {
  margin-right: 10px;
  margin-top: 2px;
}

/* ===== 二维码对话框样式 ===== */

/* 二维码容器 */
.qrcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* 二维码图片区域 */
.qrcode {
  margin-bottom: 20px;
}

/* 二维码图片 */
.qr-image {
  width: 200px;
  height: 200px;
  border: 1px solid #ebeef5;
}

/* 二维码信息区域 */
.qrcode-info {
  margin-bottom: 20px;
}

/* 二维码信息文本 */
.qrcode-info p {
  margin: 5px 0;
}
</style> 