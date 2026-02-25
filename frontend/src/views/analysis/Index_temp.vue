<!-- analysis.index.vue -->
<template>
  <div class="analysis-container page-container">
    <div class="flex-between">
      <h1 class="page-title">数据分析</h1>
      <div class="actions">
        <el-button type="primary" @click="exportData">导出数据</el-button>
        <el-button type="success" @click="generateSummary">生成总结</el-button>
      </div>
    </div>
    
    <!-- 筛选条件 -->
    <div class="card filter-panel">
      <div class="filter-row">
        <div class="filter-item">
          <span class="filter-label">选择调研：</span>
          <el-select v-model="selectedSurvey" placeholder="请选择调研" class="filter-select" @change="handleSurveyChange">
            <el-option 
              v-for="item in surveyList" 
              :key="item.id" 
              :label="item.title" 
              :value="item.id"
            />
          </el-select>
          <div v-if="surveyList.length === 0" class="no-surveys-tip">
            暂无调研数据，请先创建调研
            <br>
            <el-button type="primary" size="small" @click="setAuthToken" style="margin-top: 10px;">
              设置认证Token
            </el-button>
          </div>
        </div>
        
        <div class="filter-item">
          <span class="filter-label">分组方式：</span>
          <el-select v-model="groupBy" placeholder="请选择分组方式" class="filter-select" @change="handleGroupChange">
            <el-option label="按部门" value="department" />
            <el-option label="按职位" value="position" />
            <el-option label="按问题" value="question" />
            <el-option label="按标签" value="tag" />
          </el-select>
        </div>
        
        <div class="filter-item" v-if="groupBy === 'tag'">
          <span class="filter-label">选择标签：</span>
          <el-select v-model="selectedTag" placeholder="请选择标签" class="filter-select" @change="refreshData">
            <el-option 
              v-for="tag in tagList" 
              :key="tag.id" 
              :label="tag.name" 
              :value="tag.id"
            />
          </el-select>
        </div>
      </div>
    </div>
    
    <div class="analysis-content" v-loading="loading">
      <div class="card chart-panel" v-if="selectedSurvey">
        <h2 class="section-title">{{ chartTitle }}</h2>
        
        <div class="chart-type-selector">
          <el-radio-group v-model="chartType" @change="handleChartTypeChange">
            <el-radio-button value="pie">饼图</el-radio-button>
            <el-radio-button value="bar">柱状图</el-radio-button>
            <el-radio-button value="line">折线图</el-radio-button>
          </el-radio-group>
        </div>
        
        <div class="chart-container">
          <AnalysisChart 
            :type="chartType"
            :data="chartData"
            :title="chartTitle"
            :height="400"
            @chart-click="handleChartClick"
          />
        </div>
      </div>
      
      <div v-else class="no-data-tip">
        <el-empty description="请选择调研查看数据分析" />
      </div>
    </div>
  </div>
</template>