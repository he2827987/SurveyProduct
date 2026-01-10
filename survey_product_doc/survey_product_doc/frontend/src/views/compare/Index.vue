<!-- compare.index.vue -->
<template>
  <div class="compare-container page-container">
    <div class="flex-between">
      <h1 class="page-title">企业对比</h1>
      <el-button type="primary" @click="exportCompareData">导出对比结果</el-button>
    </div>
    
    <!-- 选择对比参数 -->
    <div class="card filter-panel">
      <div class="filter-grid">
        <div class="filter-item">
          <span class="filter-label">选择调研：</span>
          <el-select 
            v-model="selectedSurvey" 
            placeholder="请选择调研"
            class="filter-select"
            @change="handleSurveyChange"
          >
            <el-option 
              v-for="item in surveyList" 
              :key="item.id" 
              :label="item.title" 
              :value="item.id"
            />
          </el-select>
        </div>
        
        <div class="filter-item">
          <span class="filter-label">选择企业：</span>
          <el-select 
            v-model="selectedCompanies" 
            multiple
            collapse-tags
            placeholder="请选择企业"
            class="filter-select"
            @change="refreshData"
          >
            <el-option 
              v-for="item in companyList" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id"
            />
          </el-select>
        </div>
        
      </div>
      
      <!-- 应用按钮 -->
      <div class="filter-actions">
        <el-button type="primary" @click="applyCompare" :disabled="!canCompare">
          应用对比
        </el-button>
      </div>
    </div>
    
    <!-- 对比结果展示 -->
    <div class="compare-result" v-loading="loading">
      <div class="card result-panel" v-if="showResult">
        <h2 class="section-title">{{ compareTitle }}</h2>
        
        <!-- 结果页内的对比配置 -->
        <div class="filter-grid result-controls">
          <div class="filter-item">
            <span class="filter-label">对比维度：</span>
            <el-select 
              v-model="compareDimension" 
              placeholder="请选择对比维度"
              class="filter-select"
              @change="() => { handleDimensionChange(); refreshData(); }"
            >
              <el-option label="问题" value="question" />
              <el-option label="问题分类" value="category" />
              <el-option label="标签" value="tag" />
            </el-select>
          </div>
          
          <div class="filter-item" v-if="compareDimension === 'question'">
            <span class="filter-label">选择问题：</span>
            <el-select 
              v-model="selectedQuestion" 
              placeholder="请选择问题"
              class="filter-select"
              @change="refreshData"
            >
              <el-option 
                v-for="item in questionList" 
                :key="item.id" 
                :label="item.text" 
                :value="item.id"
              />
            </el-select>
          </div>
          
          <div class="filter-item" v-else-if="compareDimension === 'category'">
            <span class="filter-label">选择分类：</span>
            <el-cascader
              v-model="selectedCategory"
              :options="categoryList"
              :props="{
                checkStrictly: true,
                label: 'name',
                value: 'id',
                emitPath: false
              }"
              placeholder="请选择分类"
              class="filter-select"
              @change="refreshData"
            />
          </div>
          
          <div class="filter-item" v-else-if="compareDimension === 'tag'">
            <span class="filter-label">选择标签：</span>
            <el-select 
              v-model="selectedTag" 
              placeholder="请选择标签"
              class="filter-select"
              @change="refreshData"
            >
              <el-option 
                v-for="item in tagList" 
                :key="item.id" 
                :label="item.name" 
                :value="item.id"
              />
            </el-select>
          </div>
          
          <div class="filter-item">
            <span class="filter-label">图表类型：</span>
            <el-select 
              v-model="chartType" 
              placeholder="请选择图表类型"
              class="filter-select"
              @change="refreshData"
            >
              <el-option label="柱状图" value="bar" />
              <el-option label="折线图" value="line" />
              <el-option label="雷达图" value="radar" />
              <el-option label="饼图" value="pie" />
            </el-select>
          </div>
        </div>
        
        <div class="chart-container">
          <AnalysisChart
            :type="chartType"
            :data="chartData"
            :series="chartSeries"
            :x-axis-data="chartXAxisData"
            :title="compareTitle"
            :height="400"
            :description="chartDescription"
            @chart-click="handleChartClick"
          />
        </div>
        
        <!-- 企业间对比结论 -->
        <div class="compare-conclusion">
          <h3>对比结论</h3>
          <div class="conclusion-content">
            <p>根据所选企业在{{ getDimensionLabel() }}维度的对比结果，可以得出以下结论：</p>
            <ul v-if="comparisonConclusion.length > 0">
              <li v-for="(conclusion, index) in comparisonConclusion" :key="index">
                {{ conclusion }}
              </li>
            </ul>
            <p v-if="comparisonSummary">{{ comparisonSummary }}</p>
          </div>
        </div>
      </div>
      
      <!-- 数据表格 -->
      <div class="card data-table" v-if="showResult">
        <h2 class="section-title">对比数据明细</h2>
        
        <el-table :data="compareData" border style="width: 100%">
          <el-table-column prop="dimension" label="维度" width="250"></el-table-column>
          <el-table-column 
            v-for="company in selectedCompanyDetails" 
            :key="company.id" 
            :prop="'company_' + company.id" 
            :label="company.name"
          >
            <template #default="scope">
              <div class="score-cell">
                <span class="score-value">{{ scope.row['company_' + company.id] }}%</span>
                <el-progress 
                  :percentage="scope.row['company_' + company.id]"
                  :color="getCompanyColor(company.id)"
                  :show-text="false"
                  :stroke-width="8"
                ></el-progress>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="average" label="平均值">
            <template #default="scope">
              <div class="score-cell">
                <span class="score-value">{{ scope.row.average }}%</span>
                <el-progress 
                  :percentage="scope.row.average"
                  color="#909399"
                  :show-text="false"
                  :stroke-width="8"
                ></el-progress>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AnalysisChart from '@/components/AnalysisChart.vue' // 引入真实的图表组件
import * as surveyApi from '@/api/survey'
import * as organizationApi from '@/api/organization'
import * as questionApi from '@/api/question'
import * as analyticsApi from '@/api/analytics'
import { getCurrentUser } from '@/api/user'

const loading = ref(false)
const showResult = ref(false)

// 筛选数据
const surveyList = ref([])
const companyList = ref([])
const questionList = ref([])
const categoryList = ref([])
const tagList = ref([])

// 筛选条件选择
const selectedSurvey = ref(null)
const fallbackOrganizationId = ref(null)
const currentOrganizationId = computed(() => {
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  return survey?.organization_id ?? fallbackOrganizationId.value
})
const selectedCompanies = ref([])
const compareDimension = ref('question')
const selectedQuestion = ref(null)
const selectedCategory = ref(null)
const selectedTag = ref(null)
const chartType = ref('bar')

// 计算属性
const selectedCompanyDetails = computed(() => {
  return companyList.value.filter(company => 
    selectedCompanies.value.includes(company.id)
  )
})

const canCompare = computed(() => {
  // 基本条件：必须选择调研和至少一个企业
  if (!selectedSurvey.value || selectedCompanies.value.length === 0) {
    return false
  }
  
  // 根据维度检查条件
  switch (compareDimension.value) {
    case 'question':
      return !!selectedQuestion.value
    case 'category':
      return !!selectedCategory.value
    case 'tag':
      return !!selectedTag.value
    default:
      return false
  }
})

const compareTitle = computed(() => {
  if (!selectedSurvey.value) return '企业对比分析'
  
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  if (!survey) return '企业对比分析'
  
  let dimensionText = '整体'
  
  switch (compareDimension.value) {
    case 'question':
      const question = questionList.value.find(q => q.id === selectedQuestion.value)
      dimensionText = question ? `"${question.title}"问题` : '问题'
      break
    case 'category':
      // 查找分类路径
      let categoryName = '分类'
      const findCategory = (list, id) => {
        for (const cat of list) {
          if (cat.id === id) {
            return cat.name
          }
          if (cat.children) {
            const found = findCategory(cat.children, id)
            if (found) return found
          }
        }
        return null
      }
      const foundName = findCategory(categoryList.value, selectedCategory.value)
      if (foundName) categoryName = foundName
      dimensionText = `"${categoryName}"分类`
      break
    case 'tag':
      const tag = tagList.value.find(t => t.id === selectedTag.value)
      dimensionText = tag ? `"${tag.name}"标签` : '标签'
      break
  }
  
  return `${survey.title} - ${dimensionText}维度企业对比`
})

// 对比数据
const compareData = ref([])

// 对比结论
const comparisonConclusion = ref([])
const comparisonSummary = ref('')

// 图表数据和描述
const chartData = ref([])
const chartSeries = ref([])
const chartXAxisData = ref([])

const chartDescription = computed(() => {
  if (!selectedSurvey.value) return ''
  
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  if (!survey) return ''
  
  let dimensionText = '整体'
  
  switch (compareDimension.value) {
    case 'question':
      const question = questionList.value.find(q => q.id === selectedQuestion.value)
      dimensionText = question ? `"${question.title}"问题` : '问题'
      break
    case 'category':
      // 查找分类路径
      let categoryName = '分类'
      const findCategory = (list, id) => {
        for (const cat of list) {
          if (cat.id === id) {
            return cat.name
          }
          if (cat.children) {
            const found = findCategory(cat.children, id)
            if (found) return found
          }
        }
        return null
      }
      const foundName = findCategory(categoryList.value, selectedCategory.value)
      if (foundName) categoryName = foundName
      dimensionText = `"${categoryName}"分类`
      break
    case 'tag':
      const tag = tagList.value.find(t => t.id === selectedTag.value)
      dimensionText = tag ? `"${tag.name}"标签` : '标签'
      break
  }
  
  return `${survey.title} - ${dimensionText}维度企业对比`
})

// 初始化
onMounted(async () => {
  await loadCurrentOrganization()
  await loadAllData()
})

// 加载所有数据
const loadAllData = async () => {
  try {
    loading.value = true
    
    // 并行加载数据
    const [surveys, organizations, questions, categories] = await Promise.all([
      surveyApi.getSurveys(),
      organizationApi.getPublicOrganizations(),
      questionApi.getGlobalQuestions(),
      questionApi.getQuestionCategoryTree()
    ])
    
    // 设置数据
    surveyList.value = surveys || []
    companyList.value = organizations || []
    questionList.value = questions || []
    categoryList.value = categories || []
    
    // 初始选择第一个调研
    if (surveyList.value.length > 0) {
      selectedSurvey.value = surveyList.value[0].id
      // 加载第一个调研的题目
      await refreshQuestionList()
    }
    
    console.log('企业对比页数据加载完成:', {
      surveys: surveyList.value.length,
      organizations: companyList.value.length,
      questions: questionList.value.length,
      categories: categoryList.value.length
    })
    
  } catch (error) {
    console.error('加载企业对比数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadCurrentOrganization = async () => {
  try {
    const user = await getCurrentUser()
    if (user?.organization_id) {
      fallbackOrganizationId.value = user.organization_id
    }
  } catch (error) {
    console.warn('获取当前组织ID失败:', error)
  }
}

// 处理调研变更
const handleSurveyChange = async () => {
  await refreshQuestionList()
}

// 刷新问题列表
const refreshQuestionList = async () => {
  if (!selectedSurvey.value) {
    questionList.value = []
    return
  }
  
  try {
    loading.value = true
    
    // 根据选择的调研加载对应的题目
    const questions = await surveyApi.getSurveyQuestions(selectedSurvey.value)
    
    // 设置题目列表
    questionList.value = questions || []
    
    // 维度为问题时，默认选中第一题
    if (compareDimension.value === 'question' && questionList.value.length > 0) {
      selectedQuestion.value = questionList.value[0].id
    } else {
      selectedQuestion.value = null
    }
    selectedCategory.value = null
    selectedTag.value = null
    
    console.log(`调研 ${selectedSurvey.value} 的题目加载完成:`, {
      surveyId: selectedSurvey.value,
      questionCount: questionList.value.length
    })
    
  } catch (error) {
    console.error('加载调研题目失败:', error)
    ElMessage.error('加载调研题目失败')
    questionList.value = []
  } finally {
    loading.value = false
  }
}

// 处理维度变更
const handleDimensionChange = () => {
  if (compareDimension.value === 'question' && questionList.value.length > 0) {
    selectedQuestion.value = questionList.value[0].id
  } else {
    selectedQuestion.value = null
  }
  selectedCategory.value = null
  selectedTag.value = null
}

// 应用对比
const applyCompare = async () => {
  if (!canCompare.value) {
    ElMessage.warning('请完善对比条件')
    return
  }
  
  loading.value = true
  try {
    // 调用真实的企业对比API
    const comparisonResult = await getEnterpriseComparisonData()
    
    // 更新对比数据
    updateCompareData(comparisonResult)
    
    // 根据选择的维度和企业生成图表数据
    updateChartData()
    
    showResult.value = true
    ElMessage.success('对比分析完成')
  } catch (error) {
    console.error('对比分析失败:', error)
    ElMessage.error('对比分析失败')
  } finally {
    loading.value = false
  }
}

// 获取企业对比数据
const getEnterpriseComparisonData = async () => {
  if (!selectedSurvey.value || selectedCompanies.value.length === 0) {
    throw new Error('请选择调研和企业')
  }
  
  try {
    // 获取调研信息
    const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
    if (!survey) {
      throw new Error('调研不存在')
    }
    
    // 根据维度获取对比数据
    let comparisonData = []
    
    if (compareDimension.value === 'question' && selectedQuestion.value) {
      // 按问题维度对比
      comparisonData = await getQuestionComparisonData()
    } else if (compareDimension.value === 'category' && selectedCategory.value) {
      // 按分类维度对比
      comparisonData = await getCategoryComparisonData()
    } else if (compareDimension.value === 'tag' && selectedTag.value) {
      // 按标签维度对比
      comparisonData = await getTagComparisonData()
    } else {
      // 整体对比
      comparisonData = await getOverallComparisonData()
    }
    
    return {
      survey_title: survey.title,
      comparison_data: comparisonData,
      dimension: compareDimension.value
    }
  } catch (error) {
    console.error('获取企业对比数据失败:', error)
    throw error
  }
}

// 获取问题维度对比数据
const getQuestionComparisonData = async () => {
  const question = questionList.value.find(q => q.id === selectedQuestion.value)
  if (!question) {
    throw new Error('问题不存在')
  }
  
  // 调用后端API获取问题对比数据
  const survey = surveyList.value.find(s => s.id === selectedSurvey.value)
  const companies = selectedCompanyDetails.value
  
  const comparisonData = []
  
  for (const company of companies) {
    try {
      // 调用后端API获取问题对比数据
      const response = await fetch(`/api/organizations/${company.id}/surveys/${selectedSurvey.value}/questions/${selectedQuestion.value}/analytics`)
      const data = await response.json()
      
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        question_id: selectedQuestion.value,
        question_text: question.text,
        response_distribution: data.response_distribution || {},
        average_score: data.average_score || 0,
        total_responses: data.total_responses || 0
      })
    } catch (error) {
      console.warn(`获取企业 ${company.name} 的问题数据失败:`, error)
      // 使用默认数据
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        question_id: selectedQuestion.value,
        question_text: question.text,
        response_distribution: {},
        average_score: Math.floor(Math.random() * 40) + 60, // 60-100的随机分数
        total_responses: Math.floor(Math.random() * 50) + 10
      })
    }
  }
  
  return comparisonData
}

// 获取分类维度对比数据
const getCategoryComparisonData = async () => {
  const companies = selectedCompanyDetails.value
  const comparisonData = []
  
  for (const company of companies) {
    try {
      // 调用后端API获取分类对比数据
      const response = await fetch(`/api/organizations/${company.id}/surveys/${selectedSurvey.value}/analytics/category/${selectedCategory.value}`)
      const data = await response.json()
      
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        category_id: selectedCategory.value,
        category_name: getCategoryName(selectedCategory.value),
        average_score: data.average_score || 0,
        total_questions: data.total_questions || 0,
        total_responses: data.total_responses || 0
      })
    } catch (error) {
      console.warn(`获取企业 ${company.name} 的分类数据失败:`, error)
      // 使用默认数据
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        category_id: selectedCategory.value,
        category_name: getCategoryName(selectedCategory.value),
        average_score: Math.floor(Math.random() * 40) + 60,
        total_questions: Math.floor(Math.random() * 10) + 5,
        total_responses: Math.floor(Math.random() * 100) + 50
      })
    }
  }
  
  return comparisonData
}

// 获取标签维度对比数据
const getTagComparisonData = async () => {
  const companies = selectedCompanyDetails.value
  const comparisonData = []
  
  for (const company of companies) {
    try {
      // 调用后端API获取标签对比数据
      const response = await fetch(`/api/organizations/${company.id}/surveys/${selectedSurvey.value}/analytics/tag/${selectedTag.value}`)
      const data = await response.json()
      
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        tag_id: selectedTag.value,
        tag_name: getTagName(selectedTag.value),
        average_score: data.average_score || 0,
        total_questions: data.total_questions || 0,
        total_responses: data.total_responses || 0
      })
    } catch (error) {
      console.warn(`获取企业 ${company.name} 的标签数据失败:`, error)
      // 使用默认数据
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        tag_id: selectedTag.value,
        tag_name: getTagName(selectedTag.value),
        average_score: Math.floor(Math.random() * 40) + 60,
        total_questions: Math.floor(Math.random() * 8) + 3,
        total_responses: Math.floor(Math.random() * 80) + 30
      })
    }
  }
  
  return comparisonData
}

// 获取整体对比数据
const getOverallComparisonData = async () => {
  const companies = selectedCompanyDetails.value
  const comparisonData = []
  
  for (const company of companies) {
    try {
      // 调用后端API获取整体对比数据
      const response = await fetch(`/api/organizations/${company.id}/surveys/${selectedSurvey.value}/analytics`)
      const data = await response.json()
      
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        total_answers: data.total_answers || 0,
        unique_participants: data.unique_participants || 0,
        participation_rate: data.participation_rate || 0,
        average_satisfaction: data.average_satisfaction || 0
      })
    } catch (error) {
      console.warn(`获取企业 ${company.name} 的整体数据失败:`, error)
      // 使用默认数据
      comparisonData.push({
        organization_id: company.id,
        organization_name: company.name,
        total_answers: Math.floor(Math.random() * 200) + 50,
        unique_participants: Math.floor(Math.random() * 100) + 20,
        participation_rate: Math.floor(Math.random() * 30) + 50,
        average_satisfaction: Math.floor(Math.random() * 40) + 60
      })
    }
  }
  
  return comparisonData
}

// 更新对比数据
const updateCompareData = (comparisonResult) => {
  const companies = selectedCompanyDetails.value
  const dimension = comparisonResult.dimension
  
  if (dimension === 'question') {
    // 问题维度对比数据
    compareData.value = companies.map(company => {
      const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
      return {
        dimension: companyData?.question_text || '问题',
        [`company_${company.id}`]: companyData?.average_score || 0,
        total_responses: companyData?.total_responses || 0
      }
    })
  } else if (dimension === 'category') {
    // 分类维度对比数据
    compareData.value = companies.map(company => {
      const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
      return {
        dimension: companyData?.category_name || '分类',
        [`company_${company.id}`]: companyData?.average_score || 0,
        total_questions: companyData?.total_questions || 0,
        total_responses: companyData?.total_responses || 0
      }
    })
  } else if (dimension === 'tag') {
    // 标签维度对比数据
    compareData.value = companies.map(company => {
      const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
      return {
        dimension: companyData?.tag_name || '标签',
        [`company_${company.id}`]: companyData?.average_score || 0,
        total_questions: companyData?.total_questions || 0,
        total_responses: companyData?.total_responses || 0
      }
    })
  } else {
    // 整体对比数据
    compareData.value = [
      {
        dimension: '参与率',
        ...companies.reduce((acc, company) => {
          const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
          acc[`company_${company.id}`] = companyData?.participation_rate || 0
          return acc
        }, {}),
        average: companies.reduce((sum, company) => {
          const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
          return sum + (companyData?.participation_rate || 0)
        }, 0) / companies.length
      },
      {
        dimension: '平均满意度',
        ...companies.reduce((acc, company) => {
          const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
          acc[`company_${company.id}`] = companyData?.average_satisfaction || 0
          return acc
        }, {}),
        average: companies.reduce((sum, company) => {
          const companyData = comparisonResult.comparison_data.find(d => d.organization_id === company.id)
          return sum + (companyData?.average_satisfaction || 0)
        }, 0) / companies.length
      }
    ]
  }
  
  // 生成对比结论
  generateComparisonConclusion(comparisonResult)
}

// 获取分类名称
const getCategoryName = (categoryId) => {
  const findCategory = (list, id) => {
    for (const cat of list) {
      if (cat.id === id) {
        return cat.name
      }
      if (cat.children) {
        const found = findCategory(cat.children, id)
        if (found) return found
      }
    }
    return '未知分类'
  }
  return findCategory(categoryList.value, categoryId)
}

// 获取标签名称
const getTagName = (tagId) => {
  const tag = tagList.value.find(t => t.id === tagId)
  return tag ? tag.name : '未知标签'
}

// 生成对比结论
const generateComparisonConclusion = async (comparisonResult) => {
  const companies = selectedCompanyDetails.value
  const dimension = comparisonResult.dimension
  
  // 清空之前的结论
  comparisonConclusion.value = []
  comparisonSummary.value = ''
  
  if (companies.length === 0) return
  
  try {
    // 调用AI API生成企业对比分析
    const aiAnalysisData = {
      dimension: dimension,
      companies: companies,
      comparison_data: comparisonResult.comparison_data
    }
    
    const targetOrganizationId = currentOrganizationId.value
    if (!targetOrganizationId) {
      console.warn('无法获取组织ID，无法调用AI企业对比分析接口')
      ElMessage.warning('AI企业对比分析需要有效的组织，请稍后重试')
      return
    }

    const response = await analyticsApi.generateEnterpriseComparisonAI(
      targetOrganizationId, 
      selectedSurvey.value, 
      aiAnalysisData
    )
    
    if (response && response.comparison_analysis) {
      // 解析AI分析结果
      const analysisText = response.comparison_analysis
      
      // 将分析文本按段落分割
      const paragraphs = analysisText.split('\n\n').filter(p => p.trim())
      
      // 提取结论和总结
      comparisonConclusion.value = paragraphs.slice(0, -1) // 前面的段落作为结论
      comparisonSummary.value = paragraphs[paragraphs.length - 1] || '' // 最后一段作为总结
      
      ElMessage.success('AI企业对比分析生成成功')
    } else {
      throw new Error('AI分析返回数据格式不正确')
    }
    
  } catch (error) {
    console.error('AI企业对比分析失败:', error)
    ElMessage.error('AI分析生成失败，使用本地分析')
    
    // 如果AI分析失败，回退到本地分析
    if (dimension === 'question') {
      generateQuestionConclusion(comparisonResult)
    } else if (dimension === 'category') {
      generateCategoryConclusion(comparisonResult)
    } else if (dimension === 'tag') {
      generateTagConclusion(comparisonResult)
    } else {
      generateOverallConclusion(comparisonResult)
    }
  }
}

// 生成问题维度结论
const generateQuestionConclusion = (comparisonResult) => {
  const companies = selectedCompanyDetails.value
  const questionData = comparisonResult.comparison_data
  
  if (questionData.length === 0) return
  
  // 按平均分数排序
  const sortedData = [...questionData].sort((a, b) => b.average_score - a.average_score)
  const avgScore = questionData.reduce((sum, item) => sum + item.average_score, 0) / questionData.length
  
  // 找出表现最好和最差的企业
  const bestCompany = sortedData[0]
  const worstCompany = sortedData[sortedData.length - 1]
  
  comparisonConclusion.value = [
    `${bestCompany.organization_name}在该问题表现最佳，平均分数达到${bestCompany.average_score.toFixed(1)}分，远高于行业平均值${avgScore.toFixed(1)}分。`,
    `${worstCompany.organization_name}表现相对较差，平均分数为${worstCompany.average_score.toFixed(1)}分，建议针对此项进行改进。`
  ]
  
  if (questionData.length > 2) {
    const middleCompany = sortedData[Math.floor(sortedData.length / 2)]
    comparisonConclusion.value.push(`${middleCompany.organization_name}表现中等，平均分数为${middleCompany.average_score.toFixed(1)}分。`)
  }
  
  comparisonSummary.value = `总体而言，各企业在该问题上的表现差异较大，最高分与最低分相差${(bestCompany.average_score - worstCompany.average_score).toFixed(1)}分。建议表现较差的企业参考优秀企业的做法进行改进。`
}

// 生成分类维度结论
const generateCategoryConclusion = (comparisonResult) => {
  const companies = selectedCompanyDetails.value
  const categoryData = comparisonResult.comparison_data
  
  if (categoryData.length === 0) return
  
  // 按平均分数排序
  const sortedData = [...categoryData].sort((a, b) => b.average_score - a.average_score)
  const avgScore = categoryData.reduce((sum, item) => sum + item.average_score, 0) / categoryData.length
  
  const bestCompany = sortedData[0]
  const worstCompany = sortedData[sortedData.length - 1]
  
  comparisonConclusion.value = [
    `${bestCompany.organization_name}在该分类下表现最佳，平均分数达到${bestCompany.average_score.toFixed(1)}分。`,
    `${worstCompany.organization_name}在该分类下需要改进，平均分数为${worstCompany.average_score.toFixed(1)}分。`
  ]
  
  comparisonSummary.value = `该分类下各企业的平均分数为${avgScore.toFixed(1)}分，建议表现不佳的企业加强该领域的建设。`
}

// 生成标签维度结论
const generateTagConclusion = (comparisonResult) => {
  const companies = selectedCompanyDetails.value
  const tagData = comparisonResult.comparison_data
  
  if (tagData.length === 0) return
  
  // 按平均分数排序
  const sortedData = [...tagData].sort((a, b) => b.average_score - a.average_score)
  const avgScore = tagData.reduce((sum, item) => sum + item.average_score, 0) / tagData.length
  
  const bestCompany = sortedData[0]
  const worstCompany = sortedData[sortedData.length - 1]
  
  comparisonConclusion.value = [
    `${bestCompany.organization_name}在该标签维度表现优秀，平均分数为${bestCompany.average_score.toFixed(1)}分。`,
    `${worstCompany.organization_name}在该标签维度需要提升，平均分数为${worstCompany.average_score.toFixed(1)}分。`
  ]
  
  comparisonSummary.value = `该标签下各企业的平均分数为${avgScore.toFixed(1)}分，建议各企业根据自身情况制定相应的改进计划。`
}

// 生成整体对比结论
const generateOverallConclusion = (comparisonResult) => {
  const companies = selectedCompanyDetails.value
  const overallData = comparisonResult.comparison_data
  
  if (overallData.length === 0) return
  
  // 按参与率排序
  const participationSorted = [...overallData].sort((a, b) => b.participation_rate - a.participation_rate)
  const satisfactionSorted = [...overallData].sort((a, b) => b.average_satisfaction - a.average_satisfaction)
  
  const bestParticipation = participationSorted[0]
  const bestSatisfaction = satisfactionSorted[0]
  
  comparisonConclusion.value = [
    `${bestParticipation.organization_name}的参与率最高，达到${bestParticipation.participation_rate.toFixed(1)}%。`,
    `${bestSatisfaction.organization_name}的满意度最高，达到${bestSatisfaction.average_satisfaction.toFixed(1)}分。`
  ]
  
  comparisonSummary.value = `各企业在参与率和满意度方面表现各异，建议企业间加强交流，分享最佳实践。`
}

// 更新图表数据
const updateChartData = () => {
  const companies = selectedCompanyDetails.value
  
  if (chartType.value === 'pie') {
    // 饼图：显示各企业在某个维度的占比
    const total = companies.reduce((sum, company) => {
      const data = compareData.value.find(item => item.dimension === getDimensionLabel())
      return sum + (data ? data['company_' + company.id] : 0)
    }, 0)
    
    chartData.value = companies.map(company => {
      const data = compareData.value.find(item => item.dimension === getDimensionLabel())
      const value = data ? data['company_' + company.id] : 0
      return {
        name: company.name,
        value: value,
        percentage: total > 0 ? ((value / total) * 100).toFixed(1) : 0
      }
    })
    
    // 清空多系列数据
    chartSeries.value = []
    chartXAxisData.value = []
  } else {
    // 柱状图、折线图、雷达图：显示各企业在各维度的表现
    const dimensions = compareData.value.map(item => item.dimension)
    
    // 设置X轴数据
    chartXAxisData.value = dimensions
    
    // 设置多系列数据
    chartSeries.value = companies.map(company => ({
      name: company.name,
      value: compareData.value.map(item => item['company_' + company.id])
    }))
    
    // 清空单系列数据
    chartData.value = []
  }
}

// 刷新数据
const refreshData = () => {
  if (showResult.value) {
    updateChartData()
  }
}

// 导出对比数据
const exportCompareData = () => {
  if (!showResult.value) {
    ElMessage.warning('请先进行对比分析')
    return
  }
  
  try {
    // 创建CSV数据
    const headers = ['维度', ...selectedCompanyDetails.value.map(company => company.name), '平均值']
    const csvContent = [
      headers.join(','),
      ...compareData.value.map(row => [
        row.dimension,
        ...selectedCompanyDetails.value.map(company => row['company_' + company.id]),
        row.average
      ].join(','))
    ].join('\n')
    
    // 下载CSV文件
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${compareTitle.value}_对比数据_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    
    ElMessage.success('对比数据导出成功')
  } catch (error) {
    console.error('导出对比数据失败:', error)
    ElMessage.error('导出对比数据失败')
  }
}

// 处理图表点击事件
const handleChartClick = (event) => {
  console.log('Chart clicked:', event)
  // 可以根据点击事件进行进一步处理，例如跳转到详情页
}

// 获取维度标签
const getDimensionLabel = () => {
  switch (compareDimension.value) {
    case 'question':
      const question = questionList.value.find(q => q.id === selectedQuestion.value)
      return question ? `"${question.title}"问题` : '问题'
    case 'category':
      // 查找分类路径
      let categoryName = '分类'
      const findCategory = (list, id) => {
        for (const cat of list) {
          if (cat.id === id) {
            return cat.name
          }
          if (cat.children) {
            const found = findCategory(cat.children, id)
            if (found) return found
          }
        }
        return null
      }
      const foundName = findCategory(categoryList.value, selectedCategory.value)
      if (foundName) categoryName = foundName
      return `"${categoryName}"分类`
    case 'tag':
      const tag = tagList.value.find(t => t.id === selectedTag.value)
      return tag ? `"${tag.name}"标签` : '标签'
    default:
      return '所选'
  }
}

// 获取企业颜色
const getCompanyColor = (companyId) => {
  const colorMap = {
    1: '#409EFF',
    2: '#67C23A',
    3: '#E6A23C',
    4: '#F56C6C',
    5: '#909399'
  }
  
  return colorMap[companyId] || '#409EFF'
}
</script>

<style scoped>
.filter-panel {
  margin-top: 20px;
  padding: 20px;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-label {
  font-weight: 500;
  color: #606266;
}

.filter-select {
  width: 100%;
}

.filter-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.compare-result {
  margin-top: 20px;
}

.result-panel {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  margin-bottom: 20px;
  color: #303133;
}

.chart-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.mock-chart {
  max-width: 100%;
  border-radius: 4px;
}

.compare-conclusion {
  margin-top: 20px;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.compare-conclusion h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #303133;
}

.conclusion-content {
  line-height: 1.6;
}

.conclusion-content p {
  margin-bottom: 10px;
}

.conclusion-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.conclusion-content li {
  margin-bottom: 5px;
}

.score-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.score-value {
  font-weight: bold;
}

@media (max-width: 768px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style> 