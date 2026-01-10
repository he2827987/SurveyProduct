<!-- question.index.vue -->
<template>
  <div class="question-container page-container">
    <div class="flex-between">
      <h1 class="page-title">题库管理</h1>
      <el-button type="primary" @click="openQuestionDialog()">新增题目</el-button>
    </div>
    
    <div class="question-content">
      <!-- 左侧分类面板 -->
      <div class="card category-panel">
        <div class="flex-between panel-header">
          <h3>题目分类</h3>
          <el-button type="primary" link @click="openCategoryDialog(null)">
            <el-icon><Plus /></el-icon>添加分类
          </el-button>
        </div>

        <div class="current-category" v-if="selectedCategoryLabel">
          当前分类：{{ selectedCategoryLabel }}
        </div>
        
        <div class="category-search-row">
          <el-input
            v-model="categoryFilter"
            placeholder="搜索分类"
            clearable
            class="filter-input"
          />
          <el-tooltip content="清除选中分类" placement="top">
            <el-button 
              :icon="RefreshLeft" 
              @click="clearCategorySelection" 
              :disabled="!selectedCategoryId"
              circle
            />
          </el-tooltip>
        </div>
        
        <el-tree
          ref="categoryTreeRef"
          :data="categories"
          :props="defaultProps"
          :filter-node-method="filterCategory"
          node-key="id"
          default-expand-all
          highlight-current
          @node-click="handleCategoryClick"
        >
          <template #default="{ node, data }">
            <div class="category-node">
              <span>{{ node.label }}</span>
              <div class="category-count">({{ data.question_count || 0 }})</div>
              <div class="category-actions">
                <el-button type="primary" link @click.stop="openCategoryDialog(data)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-popconfirm
                  title="确定要删除该分类吗？"
                  @confirm="removeCategory(node, data)"
                  confirm-button-text="确定"
                  cancel-button-text="取消"
                >
                  <template #reference>
                    <el-button type="danger" link @click.stop>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </template>
        </el-tree>
        
        <div class="filter-tags">
          <h3>标签筛选</h3>
          <div class="tags-container">
            <el-tag
              v-for="tag in filterTags"
              :key="tag.name"
              :type="tag.active ? 'primary' : 'info'"
              effect="light"
              class="filter-tag"
              @click="toggleTagFilter(tag)"
              :class="{ 'active-tag': tag.active }"
            >
              {{ tag.name }} ({{ tag.count }})
            </el-tag>
          </div>
          <div class="tag-create">
            <el-input
              v-model="newTagName"
              placeholder="输入新标签，回车或点击添加"
              size="small"
              @keyup.enter="createTag"
            />
            <el-button
              type="primary"
              size="small"
              :loading="creatingTag"
              @click="createTag"
              style="margin-left: 8px;"
            >
              添加标签
            </el-button>
            <el-button
              v-if="filterTags.some(t => t.active)"
              type="danger"
              size="small"
              @click="deleteActiveTag"
              style="margin-left: 8px;"
            >
              删除选中标签
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 右侧题目列表 -->
      <div class="question-list-wrapper">
        <!-- 搜索栏 -->
        <div class="card search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索题目（输入时自动搜索）"
            clearable
            class="search-input"
          >
            <template #append>
              <el-button :icon="Search" @click="searchQuestions" title="立即搜索" />
            </template>
          </el-input>
          
          <div class="filters">
            <el-select v-model="questionType" placeholder="题目类型" clearable class="filter-select">
              <el-option label="全部类型" value="" />
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multiple" />
              <el-option label="填空题" value="text" />
            </el-select>
            
            <el-select v-model="sortBy" placeholder="排序方式" class="filter-select">
              <el-option label="创建时间降序" value="created_desc" />
              <el-option label="创建时间升序" value="created_asc" />
              <el-option label="使用次数降序" value="usage_desc" />
              <el-option label="使用次数升序" value="usage_asc" />
            </el-select>
          </div>
        </div>
        
        <!-- 题目列表 -->
        <div class="card question-list">
          <el-empty description="暂无数据" v-if="questionList.length === 0 && !loading"></el-empty>
          
          <div v-loading="loading" element-loading-text="加载中...">
            <!-- 批量操作工具栏 -->
            <div class="batch-actions" v-if="selectedQuestions.length > 0">
              <span class="selected-count">已选择 {{ selectedQuestions.length }} 项</span>
              
              <div class="action-buttons">
                <el-select v-model="batchCategory" placeholder="批量分类" size="small" class="batch-select">
                  <el-option
                    v-for="cat in flattenedCategories"
                    :key="cat.id"
                    :label="cat.name"
                    :value="cat.id"
                  />
                </el-select>
                
                <el-button size="small" type="primary" @click="batchUpdateCategory" :disabled="!batchCategory">
                  移动到该分类
                </el-button>
                
                <el-button size="small" type="danger" @click="batchDeleteQuestions">
                  批量删除
                </el-button>
              </div>
            </div>
            
            <!-- 题目列表内容 -->
            <el-table
              :data="questionList"
              style="width: 100%"
              @selection-change="handleSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              
              <el-table-column prop="text" label="题目标题" min-width="300">
                <template #default="scope">
                  <div class="question-item">
                    <div class="question-type-tag">
                      <el-tag :type="getQuestionTypeTag(scope.row.type).type" size="small">
                        {{ getQuestionTypeTag(scope.row.type).label }}
                      </el-tag>
                    </div>
                    <div class="question-title">{{ scope.row.text }}</div>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column label="标签" width="250">
                <template #default="scope">
                  <div class="tag-list">
                    <el-tag
                      v-for="tag in scope.row.tags"
                      :key="tag"
                      size="small"
                      effect="plain"
                      class="tag-item"
                    >
                      {{ tag }}
                    </el-tag>
                    <el-button
                      v-if="!scope.row.tags || scope.row.tags.length === 0"
                      type="primary"
                      link
                      size="small"
                      @click="openTagDialog(scope.row)"
                    >
                      添加标签
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="category_name" label="分类" width="120">
                <template #default="scope">
                  {{ scope.row.category_name || '未分类' }}
                </template>
              </el-table-column>
              
              <el-table-column prop="created_at" label="创建时间" width="150" />
              
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="scope">
                  <el-button type="primary" link @click="openQuestionDialog(scope.row)">
                    编辑
                  </el-button>
                  <el-button type="info" link @click="openDetailDialog(scope.row)">
                    查看详情
                  </el-button>
                  <el-popconfirm
                    title="确定要删除此题目吗？"
                    @confirm="deleteQuestionHandler(scope.row)"
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
            
            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalQuestions"
                :background="true"
                :hide-on-single-page="false"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 新增/编辑题目对话框 -->
    <el-dialog
      v-model="questionDialog.visible"
      :title="questionDialog.isEdit ? '编辑题目' : '新增题目'"
      width="650px"
      :destroy-on-close="true"
    >
      <el-form
        ref="questionFormRef"
        :model="questionForm"
        :rules="questionRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="text">
          <el-input
            v-model="questionForm.text"
            placeholder="请输入题目标题"
            maxlength="200"
            show-word-limit
            type="textarea"
            :rows="2"
          />
        </el-form-item>
        
        <el-form-item label="题目类型" prop="type">
          <el-select v-model="questionForm.type" placeholder="请选择题目类型" style="width: 100%">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="排序题" value="sort" />
            <el-option label="填空题" value="text" />
            <el-option label="数字题" value="number" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分类" prop="category_id">
          <el-cascader
            v-model="questionForm.category_id"
            :options="categories"
            :props="{
              checkStrictly: true,
              label: 'name',
              value: 'id',
              emitPath: false
            }"
            placeholder="请选择分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="是否必填" prop="is_required">
          <el-switch v-model="questionForm.is_required" />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="questionForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或创建标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        
        <template v-if="questionForm.type === 'single' || questionForm.type === 'multiple' || questionForm.type === 'sort'">
          <el-divider content-position="left">选项设置</el-divider>
          <el-alert
            v-if="questionForm.type === 'sort'"
            title="提示：排序题需要至少2个选项，用户将对这些选项进行排序"
            type="info"
            :closable="false"
            style="margin-bottom: 15px"
          />
          
          <el-form-item label="启用分值">
            <el-switch v-model="questionForm.enable_score" />
          </el-form-item>
          
          <template v-if="questionForm.enable_score">
            <el-form-item label="分值范围">
              <el-col :span="11">
                <el-input-number v-model="questionForm.min_score" placeholder="最小值" style="width: 100%" />
              </el-col>
              <el-col :span="2" class="text-center">
                <span class="text-gray-500">-</span>
              </el-col>
              <el-col :span="11">
                <el-input-number v-model="questionForm.max_score" placeholder="最大值" style="width: 100%" />
              </el-col>
            </el-form-item>
          </template>

          <div class="options-list">
            <div 
              v-for="(option, index) in questionForm.options" 
              :key="index"
              class="option-item"
            >
              <el-row :gutter="10" style="width: 100%" align="middle">
                <!-- 排序题的拖拽手柄 -->
                <el-col :span="2" v-if="questionForm.type === 'sort'" class="flex items-center justify-center">
                  <el-icon style="cursor: move; color: #909399" class="drag-handle">
                    <Rank />
                  </el-icon>
                </el-col>
                <el-col :span="questionForm.enable_score ? (questionForm.type === 'sort' ? 12 : 14) : (questionForm.type === 'sort' ? 18 : 20)">
                  <el-input
                    v-model="questionForm.options[index].text"
                    placeholder="请输入选项内容"
                  >
                    <template #prepend>
                      <div class="option-label">{{ String.fromCharCode(65 + index) }}</div>
                    </template>
                  </el-input>
                </el-col>
                <el-col :span="6" v-if="questionForm.enable_score">
                   <el-input-number 
                      v-model="questionForm.options[index].score" 
                      :min="questionForm.min_score" 
                      :max="questionForm.max_score"
                      placeholder="分值"
                      style="width: 100%"
                   />
                </el-col>
                <el-col :span="2" class="flex items-center justify-center" v-if="questionForm.type !== 'sort'">
                    <el-tooltip content="设为正确答案" placement="top">
                        <el-checkbox v-model="questionForm.options[index].is_correct" />
                    </el-tooltip>
                </el-col>
                <el-col :span="2">
                  <el-button @click="removeOption(index)" :disabled="questionForm.options.length <= 2" style="width: 100%">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-col>
                <!-- 排序题的上移下移按钮 -->
                <el-col :span="4" v-if="questionForm.type === 'sort'" class="flex items-center gap-2">
                  <el-button 
                    size="small" 
                    @click="moveOptionUp(index)" 
                    :disabled="index === 0"
                    text
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </el-button>
                  <el-button 
                    size="small" 
                    @click="moveOptionDown(index)" 
                    :disabled="index === questionForm.options.length - 1"
                    text
                  >
                    <el-icon><ArrowDown /></el-icon>
                  </el-button>
                </el-col>
              </el-row>
            </div>
            
            <div class="add-option">
              <el-button text @click="addOption" :disabled="questionForm.options.length >= 10">
                <el-icon><Plus /></el-icon> 添加选项
              </el-button>
            </div>
          </div>
        </template>
        
        <template v-if="questionForm.type === 'text' || questionForm.type === 'number'">
          <el-divider content-position="left">{{ questionForm.type === 'text' ? '填空设置' : '数字设置' }}</el-divider>
          
          <el-form-item v-if="questionForm.type === 'text'" label="最大字数">
            <el-input-number 
              v-model="questionForm.max_length" 
              :min="10" 
              :max="2000" 
              :step="10"
            />
          </el-form-item>
          
          <el-form-item v-if="questionForm.type === 'number'" label="最小值">
            <el-input-number v-model="questionForm.min_value" :min="-999999" />
          </el-form-item>
          
          <el-form-item v-if="questionForm.type === 'number'" label="最大值">
            <el-input-number v-model="questionForm.max_value" :min="-999999" />
          </el-form-item>
        </template>
        
        <!-- 关联题设置 -->
        <el-divider content-position="left">关联题设置（可选）</el-divider>
        <el-form-item label="父题目">
          <el-select 
            v-model="questionForm.parent_question_id" 
            placeholder="选择父题目（留空表示非关联题）" 
            clearable
            filterable
            style="width: 100%"
            @change="handleParentQuestionChange"
          >
            <el-option
              v-for="q in availableParentQuestions"
              :key="q.id"
              :label="`Q${q.order || q.id}: ${q.text.substring(0, 50)}${q.text.length > 50 ? '...' : ''}`"
              :value="q.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          v-if="questionForm.parent_question_id" 
          label="触发选项"
          :rules="[{ 
            required: true, 
            message: '设置父题目后，必须选择至少一个触发选项',
            validator: (rule, value, callback) => {
              if (questionForm.parent_question_id && (!value || value.length === 0)) {
                callback(new Error('设置父题目后，必须选择至少一个触发选项'))
              } else {
                callback()
              }
            }
          }]"
        >
          <el-select 
            v-model="questionForm.trigger_options" 
            placeholder="选择触发选项（当父题目选择这些选项时，此题目才会显示）" 
            multiple
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="opt in parentQuestionOptions"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
          <el-alert
            title="提示：当父题目选择了上述任一选项时，此题目才会显示给用户"
            type="info"
            :closable="false"
            style="margin-top: 10px"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="questionDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="savingQuestion" :disabled="savingQuestion" @click="saveQuestion">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 分类操作对话框 -->
    <el-dialog
      v-model="categoryDialog.visible"
      :title="categoryDialog.isEdit ? '编辑分类' : '添加分类'"
      width="500px"
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-width="80px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        
        <el-form-item label="分类描述">
          <el-input 
            v-model="categoryForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入分类描述" 
          />
        </el-form-item>
        
        <el-form-item label="分类编码">
          <el-input v-model="categoryForm.code" placeholder="请输入分类编码" />
        </el-form-item>
        
        <el-form-item label="上级分类">
          <el-cascader
            v-model="categoryForm.parent_id"
            :options="categories"
            :props="{
              checkStrictly: true,
              label: 'name',
              value: 'id',
              emitPath: false
            }"
            placeholder="请选择上级分类"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="categoryForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="categoryDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="saveCategory">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 标签管理对话框 -->
    <el-dialog
      v-model="tagDialog.visible"
      title="管理标签"
      width="500px"
    >
      <el-form>
        <el-form-item label="题目标签">
          <el-select
            v-model="tagDialog.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或创建标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="tagDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="saveTags">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 题目详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="题目详情"
      width="700px"
      :destroy-on-close="true"
    >
      <div v-if="detailDialog.question" class="question-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3 class="section-title">基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="题目ID">{{ detailDialog.question.id }}</el-descriptions-item>
            <el-descriptions-item label="创建者ID">{{ detailDialog.question.owner_id || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="创建者">{{ detailDialog.question.owner_name || '未知用户' }}</el-descriptions-item>
            <el-descriptions-item label="题目类型">
              <el-tag :type="getQuestionTypeTag(detailDialog.question.type).type">
                {{ getQuestionTypeTag(detailDialog.question.type).label }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="分类">{{ detailDialog.question.category_name || '未分类' }}</el-descriptions-item>
            <el-descriptions-item label="是否必填">
              <el-tag :type="detailDialog.question.is_required ? 'danger' : 'info'" size="small">
                {{ detailDialog.question.is_required ? '必填' : '选填' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ detailDialog.question.created_at }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ detailDialog.question.updated_at || '未更新' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- 题目内容 -->
        <div class="detail-section">
          <h3 class="section-title">
            题目内容
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="copyQuestionText"
              style="margin-left: 10px;"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制题目
            </el-button>
          </h3>
          <div class="question-content">
            <p class="question-text">{{ detailDialog.question.text }}</p>
          </div>
        </div>
        
        <!-- 选项信息 -->
        <div class="detail-section" v-if="detailDialog.question.options && detailDialog.question.options.length > 0">
          <h3 class="section-title">选项信息</h3>
          <div v-if="detailDialog.question.min_score !== undefined && detailDialog.question.max_score !== undefined" class="mb-2 text-gray-500">
             分值范围: {{ detailDialog.question.min_score }} - {{ detailDialog.question.max_score }}
          </div>
          <div class="options-list">
            <div
              v-for="(option, index) in detailDialog.question.options"
              :key="index"
              class="option-item"
            >
              <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
              <span class="option-text">{{ typeof option === 'string' ? option : option.text }}</span>
              <el-tag v-if="typeof option !== 'string' && option.score !== undefined" type="warning" size="small" class="ml-2">
                {{ option.score }}分
              </el-tag>
              <el-tag v-if="option.is_correct" type="success" size="small" class="ml-2">正确答案</el-tag>
            </div>
          </div>
        </div>
        
        <!-- 标签信息 -->
        <div class="detail-section">
          <h3 class="section-title">标签信息</h3>
          <div class="tags-container">
            <el-tag
              v-for="tag in detailDialog.question.tags"
              :key="tag"
              size="small"
              effect="plain"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <span v-if="!detailDialog.question.tags || detailDialog.question.tags.length === 0" class="no-tags">
              暂无标签
            </span>
          </div>
        </div>
        
        <!-- 使用统计 -->
        <div class="detail-section">
          <h3 class="section-title">使用统计</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="使用次数">{{ detailDialog.question.usage_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="回答次数">{{ detailDialog.question.answer_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="正确率">
               {{ 
                  (detailDialog.question.options && detailDialog.question.options.some(opt => opt.is_correct)) 
                  ? (detailDialog.question.correct_rate || '0%') 
                  : 'N/A' 
               }}
            </el-descriptions-item>
          </el-descriptions>
          <div class="statistics-note">
            <el-alert
              title="统计信息说明"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>• 使用次数：该题目在调研中被使用的次数</p>
                <p>• 回答次数：该题目收到的回答总数</p>
                <p>• 正确率：选择题的正确回答比例（填空题暂无此统计）</p>
              </template>
            </el-alert>
          </div>
        </div>
        
        <!-- 题目属性 -->
        <div class="detail-section">
          <h3 class="section-title">题目属性</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="题目类型">
              <el-tag :type="getQuestionTypeTag(detailDialog.question.type).type">
                {{ getQuestionTypeTag(detailDialog.question.type).label }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="是否必填">
              <el-tag :type="detailDialog.question.is_required ? 'danger' : 'info'" size="small">
                {{ detailDialog.question.is_required ? '必填' : '选填' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="排序位置">{{ detailDialog.question.order || 0 }}</el-descriptions-item>
            <el-descriptions-item label="选项数量">{{ detailDialog.question.options ? detailDialog.question.options.length : 0 }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialog.visible = false">关闭</el-button>
          <el-button type="success" @click="exportQuestionDetail">
            <el-icon><Download /></el-icon>
            导出详情
          </el-button>
          <el-button type="primary" @click="editFromDetail">编辑题目</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Edit, Search, DocumentCopy, Download, Rank, ArrowUp, ArrowDown, RefreshLeft } from '@element-plus/icons-vue'
import { createGlobalQuestion, getGlobalQuestions, updateQuestion, deleteQuestion, getQuestionCategoryTree, createQuestionCategory, updateQuestionCategory, deleteQuestionCategory, getQuestionTags, createQuestionTag, deleteQuestionTag } from '@/api/question'

// 分类树数据
const categories = ref([])
const categoriesLoading = ref(false)
const selectedCategoryId = ref(null)
const selectedCategoryLabel = ref('全部')

// 展平的分类列表，用于下拉选择
const flattenedCategories = computed(() => {
  const result = []
  
  const flatten = (items, parentName = '') => {
    items.forEach(item => {
      const name = parentName ? `${parentName} / ${item.name}` : item.name
      result.push({
        id: item.id,
        name
      })
      
      if (item.children && item.children.length) {
        flatten(item.children, name)
      }
    })
  }
  
  flatten(categories.value)
  return result
})

// 标签过滤数据
const filterTags = ref([
  { name: '员工福利', count: 8, active: false },
  { name: '工作环境', count: 12, active: false },
  { name: '团队协作', count: 5, active: false },
  { name: '领导力', count: 7, active: false },
  { name: '职业发展', count: 10, active: false },
  { name: '公司文化', count: 6, active: false }
])

// 新建标签
const newTagName = ref('')
const creatingTag = ref(false)

// 题目列表数据
const questionList = ref([])
const savingQuestion = ref(false)

// 所有标签
const allTags = computed(() => {
  return Array.from(new Set(filterTags.value.map(tag => tag.name)))
})

// 分类过滤
const categoryFilter = ref('')
const categoryTreeRef = ref(null)
// selectedCategoryId 在文件上方已声明，这里移除重复声明

// 题目搜索
const searchQuery = ref('')
const questionType = ref('')
const sortBy = ref('created_desc')
const currentPage = ref(1)
const pageSize = ref(10)  // 设置默认页面大小为10
const totalQuestions = ref(0)
const loading = ref(false)
const searchTimer = ref(null) // 搜索防抖定时器

// 多选
const selectedQuestions = ref([])
const batchCategory = ref(null)

// 对话框
const questionDialog = ref({
  visible: false,
  isEdit: false
})

const categoryDialog = ref({
  visible: false,
  isEdit: false
})

const tagDialog = ref({
  visible: false,
  currentQuestion: null,
  tags: []
})

const detailDialog = ref({
  visible: false,
  question: null
})

// 表单
const questionFormRef = ref(null)
const questionForm = ref({
  id: '',
  text: '',
  type: 'single_choice',
  category_id: null,
  tags: [],
  options: [{text: '选项A', score: 0, is_correct: false}, {text: '选项B', score: 0, is_correct: false}, {text: '选项C', score: 0, is_correct: false}],
  enable_score: false,
  min_score: 0,
  max_score: 10,
  max_length: 500,
  parent_question_id: null,
  trigger_options: []
})

const categoryFormRef = ref(null)
const categoryForm = ref({
  id: '',
  name: '',
  description: '',
  code: '',
  parent_id: null,
  sort_order: 0,
  is_active: true
})

// 表单验证规则
const questionRules = {
  text : [
    { required: true, message: '请输入题目标题', trigger: 'blur' },
    { min: 3, max: 200, message: '长度在 3 到 200 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择题目类型', trigger: 'change' }
  ]
}

const categoryRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 树属性
const defaultProps = {
  children: 'children',
  label: 'name'
}

// 监听分类过滤输入
watch(categoryFilter, (val) => {
  if (categoryTreeRef.value) {
    categoryTreeRef.value.filter(val)
  }
})

// 获取分类树数据
const fetchCategories = async () => {
  categoriesLoading.value = true
  try {
    const response = await getQuestionCategoryTree()
    categories.value = response || []
    // 如果已选分类，刷新路径展示
    if (selectedCategoryId.value) {
      selectedCategoryLabel.value = getCategoryPathLabel(selectedCategoryId.value)
    }
  } catch (error) {
    console.error('获取分类树失败:', error)
    ElMessage.error('获取分类树失败: ' + (error.message || '未知错误'))
    categories.value = []
  } finally {
    categoriesLoading.value = false
  }
}

// 获取标签数据
const fetchTags = async () => {
  try {
    const response = await getQuestionTags()
    if (response && Array.isArray(response)) {
      // 转换后端数据格式为前端格式
      filterTags.value = response.map(tag => ({
        id: tag.id,
        name: tag.name,
        count: tag.question_count || 0,
        active: false
      }))
    }
  } catch (error) {
    console.error('获取标签失败:', error)
    // 如果获取失败，使用默认标签数据
    filterTags.value = [
      { name: '员工福利', count: 8, active: false },
      { name: '工作环境', count: 12, active: false },
      { name: '团队协作', count: 5, active: false },
      { name: '领导力', count: 7, active: false },
      { name: '职业发展', count: 10, active: false },
      { name: '公司文化', count: 6, active: false }
    ]
  }
}

// 获取问题列表
const fetchQuestions = async () => {
  loading.value = true
  try {
    // 构造查询参数
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    // 添加类型筛选参数
    if (questionType.value) {
      params.type = questionType.value
    }
    // 添加搜索关键词
    if (searchQuery.value && searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    // 添加排序参数
    if (sortBy.value) {
      params.sort_by = sortBy.value
    }
    // 添加分类筛选参数
    if (selectedCategoryId.value) {
      params.category_id = selectedCategoryId.value
    }
    // 添加标签筛选参数
    const activeTags = filterTags.value.filter(tag => tag.active).map(tag => tag.name)
    if (activeTags.length > 0) {
      params.tags = activeTags.join(',')
    }

    const response = await getGlobalQuestions(params)
    
    // 处理新的API响应格式
    if (response && response.items) {
      // 新格式：{ items: [...], total: 100, ... }
      questionList.value = response.items
      totalQuestions.value = response.total
    } else if (Array.isArray(response)) {
      // 兼容旧格式：直接返回数组
      questionList.value = response
      totalQuestions.value = response.length
    } else {
      // 其他情况
      questionList.value = []
      totalQuestions.value = 0
    }
    
  } catch (error) {
    console.error('获取题目列表失败:', error)
    ElMessage.error('获取题目列表失败: ' + (error.message || '未知错误'))
    questionList.value = [] // 失败时清空列表
    totalQuestions.value = 0
  } finally {
    loading.value = false
  }
}

// 加载数据
onMounted(() => {
  fetchQuestions()
  fetchCategories()
  fetchTags()
})

// 过滤分类
const filterCategory = (value, data) => {
  if (!value) return true
  return data.name.includes(value)
}

// 清除分类选择
const clearCategorySelection = () => {
  selectedCategoryId.value = null
  selectedCategoryLabel.value = '全部'
  if (categoryTreeRef.value) {
    categoryTreeRef.value.setCurrentKey(null)
  }
  currentPage.value = 1
  fetchQuestions()
}

// 点击分类
const handleCategoryClick = (data) => {
  selectedCategoryId.value = data.id
  selectedCategoryLabel.value = getCategoryPathLabel(data.id)
  currentPage.value = 1
  fetchQuestions()
}

// 递归查找分类路径（名称链）
const getCategoryPathLabel = (targetId) => {
  const dfs = (nodes, trail = []) => {
    for (const n of nodes || []) {
      const nextTrail = [...trail, n.name]
      if (n.id === targetId) return nextTrail
      if (n.children && n.children.length) {
        const found = dfs(n.children, nextTrail)
        if (found) return found
      }
    }
    return null
  }
  const path = dfs(categories.value, [])
  return path ? path.join(' / ') : '全部'
}

// 切换标签筛选
const toggleTagFilter = (tag) => {
  tag.active = !tag.active
  currentPage.value = 1
  fetchQuestions()
}

// 删除选中标签（仅删除一个当前激活的标签）
const deleteActiveTag = async () => {
  const activeTags = filterTags.value.filter(t => t.active)
  if (activeTags.length === 0) {
    ElMessage.warning('请先选中要删除的标签')
    return
  }
  if (activeTags.length > 1) {
    ElMessage.warning('不能同时删除多个标签')
    return
  }
  const activeTag = activeTags[0]
  if (!activeTag.id) {
    ElMessage.error('无法删除：缺少标签ID（可能是本地默认标签）')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定删除标签「${activeTag.name}」？此操作将从所有题目中移除该标签。`,
      '提示',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await deleteQuestionTag(activeTag.id)
    // 从列表移除
    filterTags.value = filterTags.value.filter(t => t.id !== activeTag.id)
    // 刷新题目和标签
    await fetchQuestions()
    await fetchTags()
    ElMessage.success('标签已删除')
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除标签失败:', err)
      ElMessage.error('删除标签失败')
    }
  }
}

// 创建新标签
const createTag = async () => {
  const name = newTagName.value.trim()
  if (!name) {
    ElMessage.warning('请输入标签名称')
    return
  }

  // 前端去重：若已存在同名标签则直接提示并激活
  const existing = filterTags.value.find(t => t.name === name)
  if (existing) {
    existing.active = true
    newTagName.value = ''
    currentPage.value = 1
    fetchQuestions()
    return
  }

  try {
    creatingTag.value = true
    const resp = await createQuestionTag({ name })
    // 确保返回对象包含 name
    const created = resp && resp.name ? resp : { id: undefined, name, count: 0, active: false }
    filterTags.value.push({
      id: created.id,
      name: created.name,
      count: created.question_count || 0,
      active: true
    })
    newTagName.value = ''
    currentPage.value = 1
    fetchQuestions()
    ElMessage.success('标签创建成功')
  } catch (error) {
    console.error('创建标签失败:', error)
    ElMessage.error('创建标签失败')
  } finally {
    creatingTag.value = false
  }
}

// 搜索题目
const searchQuestions = () => {
  currentPage.value = 1
  fetchQuestions()
}

// 分页变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1  // 重置到第一页
  fetchQuestions()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchQuestions()
}

watch(questionType, () => {
  currentPage.value = 1
  fetchQuestions()
})

// 监听排序方式变化
watch(sortBy, () => {
  currentPage.value = 1
  fetchQuestions()
})

// 监听搜索关键词变化，实现实时搜索
watch(searchQuery, (newValue, oldValue) => {
  // 防抖处理，避免频繁请求
  if (searchTimer.value) {
    clearTimeout(searchTimer.value)
  }
  
  searchTimer.value = setTimeout(() => {
    currentPage.value = 1
    fetchQuestions()
  }, 500) // 500ms 防抖延迟
})

// 表格多选
const handleSelectionChange = (selection) => {
  selectedQuestions.value = selection
}

// 批量更新分类
const batchUpdateCategory = () => {
  if (!batchCategory.value || selectedQuestions.value.length === 0) return
  
  const ids = selectedQuestions.value.map(item => item.id)
  ElMessage.success(`已将 ${ids.length} 个题目移动到新分类`)
  
  // 实际项目中应调用接口进行更新
  batchCategory.value = null
}

// 批量删除
const batchDeleteQuestions = async () => {
  if (selectedQuestions.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedQuestions.value.length} 个题目吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 批量删除选中的题目
    const deletePromises = selectedQuestions.value.map(question => 
      deleteQuestion(question.id).catch(error => {
        console.error(`删除题目 ${question.id} 失败:`, error)
        return { success: false, id: question.id, error }
      })
    )
    
    const results = await Promise.allSettled(deletePromises)
    
    // 统计删除结果
    const successCount = results.filter(result => 
      result.status === 'fulfilled' && !result.value.error
    ).length
    const failCount = selectedQuestions.value.length - successCount
    
    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount} 个题目`)
    }
    if (failCount > 0) {
      ElMessage.warning(`${failCount} 个题目删除失败`)
    }
    
    // 清空选择
    selectedQuestions.value = []
    
    // 计算删除后的分页情况
    const totalAfterDelete = totalQuestions.value - successCount
    const maxPage = Math.ceil(totalAfterDelete / pageSize.value)
    
    // 如果删除后当前页没有题目了，跳转到上一页
    if (currentPage.value > maxPage && maxPage > 0) {
      currentPage.value = maxPage
    }
    
    // 刷新题目列表
    await fetchQuestions()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + (error.message || '未知错误'))
    }
  }
}

// 获取题目类型Tag
const getQuestionTypeTag = (type) => {
  const types = {
    'single': { label: '单选题', type: 'primary' },
    'multiple': { label: '多选题', type: 'success' },
    'sort': { label: '排序题', type: 'warning' },
    'text': { label: '填空题', type: 'warning' },
    'number': { label: '数字题', type: 'info' },
    'single_choice': { label: '单选题', type: 'primary' },
    'multi_choice': { label: '多选题', type: 'success' },
    'sort_order': { label: '排序题', type: 'warning' },
    'text_input': { label: '填空题', type: 'warning' },
    'number_input': { label: '数字题', type: 'info' }
  }
  return types[type] || { label: '未知', type: 'info' }
}

// 打开新增/编辑题目对话框
const openQuestionDialog = (question = null) => {
  questionDialog.value.isEdit = !!question
  
  if (question) {
    // 编辑模式，填充表单
    const questionData = JSON.parse(JSON.stringify(question))
    
    // 转换题目类型为前端格式
    questionData.type = mapQuestionTypeForUI(questionData.type)
    
// 处理选项数据
if (questionData.options && typeof questionData.options === 'string') {
  try {
    const parsedOptions = JSON.parse(questionData.options)
    // 统一转换为对象格式
    questionData.options = parsedOptions.map(opt => {
        if (typeof opt === 'string') return { text: opt, score: 0, is_correct: false }
        if (opt.is_correct === undefined) opt.is_correct = false
        return opt
    })
  } catch (e) {
    questionData.options = []
  }
} else if (Array.isArray(questionData.options)) {
    // 已经是数组，确保元素统一
    questionData.options = questionData.options.map(opt => {
        if (typeof opt === 'string') return { text: opt, score: 0, is_correct: false }
        if (opt.is_correct === undefined) opt.is_correct = false
        return opt
    })
}
    
    // 设置默认值
    if (!questionData.options) {
      questionData.options = [{text: '选项A', score: 0, is_correct: false}, {text: '选项B', score: 0, is_correct: false}, {text: '选项C', score: 0, is_correct: false}]
    } else {
        // 确保 options 是对象数组
        questionData.options = questionData.options.map(opt => {
            if (typeof opt === 'string') {
                return { text: opt, score: 0, is_correct: false }
            }
            if (opt.is_correct === undefined) opt.is_correct = false // 确保有 is_correct 字段
            return opt
        })
    }
    
    // 初始化分值相关字段
    if (questionData.min_score === undefined) questionData.min_score = 0
    if (questionData.max_score === undefined) questionData.max_score = 10
    
    // 如果已有分值且不全为0，则默认开启分值
    const hasScore = questionData.options.some(opt => opt.score !== 0 && opt.score !== undefined)
    questionData.enable_score = hasScore

    if (!questionData.max_length) {
      questionData.max_length = 500
    }
    if (!questionData.tags) {
      questionData.tags = []
    }
    
    // 处理关联题字段
    if (questionData.parent_question_id) {
      questionData.parent_question_id = questionData.parent_question_id
    } else {
      questionData.parent_question_id = null
    }
    
    // 处理trigger_options（从后端JSON字符串解析）
    if (questionData.trigger_options) {
      if (typeof questionData.trigger_options === 'string') {
        try {
          const parsed = JSON.parse(questionData.trigger_options)
          questionData.trigger_options = parsed.map(t => t.option_text || t)
        } catch (e) {
          questionData.trigger_options = []
        }
      } else if (Array.isArray(questionData.trigger_options)) {
        questionData.trigger_options = questionData.trigger_options.map(t => t.option_text || t)
      }
    } else {
      questionData.trigger_options = []
    }
    
    questionForm.value = questionData
  } else {
    // 新增模式，重置表单
    questionForm.value = {
      id: '',
      text: '',
      type: 'single',
      category_id: null,
      tags: [],
      is_required: false,
      options: [{text: '选项A', score: 0, is_correct: false}, {text: '选项B', score: 0, is_correct: false}, {text: '选项C', score: 0, is_correct: false}],
      enable_score: false,
      min_score: 0,
      max_score: 10,
      max_length: 500,
      min_value: 0,
      max_value: 999999,
      parent_question_id: null,
      trigger_options: []
    }
  }
  
  questionDialog.value.visible = true
}

// 添加选项
const addOption = () => {
  if (questionForm.value.options.length < 10) {
    questionForm.value.options.push({ text: '', score: 0, is_correct: false })
  }
}

// 移除选项
const removeOption = (index) => {
  if (questionForm.value.options.length > 2) {
    questionForm.value.options.splice(index, 1)
  }
}

// 排序题：上移选项
const moveOptionUp = (index) => {
  if (index > 0) {
    const options = questionForm.value.options
    const temp = options[index]
    options[index] = options[index - 1]
    options[index - 1] = temp
  }
}

// 排序题：下移选项
const moveOptionDown = (index) => {
  const options = questionForm.value.options
  if (index < options.length - 1) {
    const temp = options[index]
    options[index] = options[index + 1]
    options[index + 1] = temp
  }
}

// 可用的父题目列表（排除当前题目和已经是关联题的题目）
const availableParentQuestions = computed(() => {
  return questionList.value.filter(q => {
    // 排除当前编辑的题目
    if (questionForm.value.id && q.id === questionForm.value.id) {
      return false
    }
    // 只显示选择题类型的题目作为父题目（因为需要选项来触发）
    const qType = mapQuestionTypeForUI(q.type)
    return qType === 'single' || qType === 'multiple'
  })
})

// 父题目的选项列表
const parentQuestionOptions = computed(() => {
  if (!questionForm.value.parent_question_id) {
    return []
  }
  const parentQuestion = questionList.value.find(q => q.id === questionForm.value.parent_question_id)
  if (!parentQuestion) {
    return []
  }
  
  // 解析父题目的选项
  let options = []
  if (parentQuestion.options) {
    if (typeof parentQuestion.options === 'string') {
      try {
        options = JSON.parse(parentQuestion.options)
      } catch (e) {
        return []
      }
    } else if (Array.isArray(parentQuestion.options)) {
      options = parentQuestion.options
    }
  }
  
  // 提取选项文本
  return options.map(opt => {
    if (typeof opt === 'string') {
      return opt
    } else if (opt && opt.text) {
      return opt.text
    }
    return String(opt)
  })
})

// 处理父题目变化
const handleParentQuestionChange = () => {
  // 当父题目改变时，清空触发选项
  questionForm.value.trigger_options = []
}

// 保存题目
const saveQuestion = () => {
  if (savingQuestion.value) return
  questionFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请检查表单输入是否正确。')
      return
    }
    savingQuestion.value = true
    try {
        // 1. 深拷贝表单数据，避免修改原始表单
        const payload = JSON.parse(JSON.stringify(questionForm.value))
        
        // 2. 转换 type 字段
        payload.type = mapQuestionTypeForApi(payload.type)
        
        // 3. 处理选项字段 - 填空题和数字题不应该有选项
        if (payload.type === 'text_input' || payload.type === 'number_input') {
          payload.options = null
        }
        
        // 4. 处理关联题字段
        // 将trigger_options转换为后端需要的格式：[{"option_text": "选项A"}]
        if (payload.trigger_options && Array.isArray(payload.trigger_options) && payload.trigger_options.length > 0) {
          payload.trigger_options = payload.trigger_options.map(opt => ({
            option_text: opt
          }))
        } else {
          // 如果没有触发选项或为空数组，清空关联题相关字段
          payload.trigger_options = null
        }
        
        // 如果没有父题目ID，也清空它
        if (!payload.parent_question_id) {
          payload.parent_question_id = null
        }
        
        // 5. 确保 survey_id 为 null 表示存入全局题库
        payload.survey_id = null

        let response
        if (questionDialog.value.isEdit) {
          // 编辑现有题目
          response = await updateQuestion(payload.id, payload) // 使用 payload
          ElMessage.success('题目更新成功')
          // 刷新题目列表以获取最新数据
          await fetchQuestions()
          await fetchCategories() // 更新分类计数
        } else {
          response = await createGlobalQuestion(payload)
          ElMessage.success('题目添加成功')
          await fetchQuestions()
          await fetchCategories()
        }
        questionDialog.value.visible = false
      } catch (error) {
        console.error('=== 捕获到错误 ===');
        console.error('保存题目失败:', error);
        console.error('错误对象详情:', error); // 打印完整错误对象
        console.error('错误堆栈:', error.stack); // 打印堆栈信息
        let errorMsg = '未知错误'
        // 尝试从 error 对象中提取更具体的后端错误信息
        if (error.response) {
            console.error('错误响应对象 (error.response):', error.response);
            if (error.response.data) {
                console.error('错误响应数据 (error.response.data):', error.response.data);
                if (error.response.data.detail) {
                    errorMsg = JSON.stringify(error.response.data.detail);
                } else {
                    // 如果 detail 不存在，尝试直接 stringify data
                    errorMsg = JSON.stringify(error.response.data);
                }
            } else {
                errorMsg = `HTTP Error: ${error.response.status} ${error.response.statusText}`;
            }
        } else if (error.request) {
            console.error('错误请求对象 (error.request):', error.request);
            errorMsg = '网络请求失败，请检查网络连接或后端服务。';
        } else {
            errorMsg = error.message || '未知错误';
        }
        ElMessage.error('保存题目失败: ' + errorMsg);
      } finally {
        savingQuestion.value = false
    }
  })
}

// 删除题目
const deleteQuestionHandler = async (question) => { // 更改函数名以避免与导入的 deleteQuestion 冲突
  try {
    await deleteQuestion(question.id)
    ElMessage.success('题目删除成功')
    
    // 计算删除后的分页情况
    const totalAfterDelete = totalQuestions.value - 1
    const maxPage = Math.ceil(totalAfterDelete / pageSize.value)
    
    // 如果删除后当前页没有题目了，跳转到上一页
    if (currentPage.value > maxPage && maxPage > 0) {
      currentPage.value = maxPage
    }
    
    // 刷新题目列表以获取最新数据
    await fetchQuestions()
  } catch (error) {
    console.error('删除题目失败:', error)
    ElMessage.error('删除题目失败: ' + (error.message || '未知错误'))
  }
}

// 打开分类对话框
const openCategoryDialog = (category = null) => {
  categoryDialog.value.isEdit = !!category
  
  if (category) {
    // 编辑模式
    categoryForm.value = {
      id: category.id,
      name: category.name,
      parent_id: category.parent_id || null
    }
  } else {
    // 新增模式
    categoryForm.value = {
      id: '',
      name: '',
      parent_id: null
    }
  }
  
  categoryDialog.value.visible = true
}

// 保存分类
const saveCategory = async () => {
  categoryFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (categoryDialog.value.isEdit) {
          // 编辑现有分类
          await updateQuestionCategory(categoryForm.value.id, {
            name: categoryForm.value.name,
            description: categoryForm.value.description,
            code: categoryForm.value.code,
            parent_id: categoryForm.value.parent_id,
            sort_order: categoryForm.value.sort_order,
            is_active: categoryForm.value.is_active
          })
          ElMessage.success('分类更新成功')
        } else {
          // 添加新分类
          await createQuestionCategory({
            name: categoryForm.value.name,
            description: categoryForm.value.description,
            code: categoryForm.value.code,
            parent_id: categoryForm.value.parent_id,
            sort_order: categoryForm.value.sort_order,
            is_active: categoryForm.value.is_active
          })
          ElMessage.success('分类添加成功')
        }
        
        // 重新获取分类数据
        await fetchCategories()
        categoryDialog.value.visible = false
      } catch (error) {
        console.error('保存分类失败:', error)
        ElMessage.error('保存分类失败: ' + (error.message || '未知错误'))
      }
    }
  })
}

// 移除分类
const removeCategory = async (node, data) => {
  try {
    await deleteQuestionCategory(data.id)
    ElMessage.success('分类删除成功')
    // 重新获取分类数据
    await fetchCategories()
  } catch (error) {
    console.error('删除分类失败:', error)
    ElMessage.error('删除分类失败: ' + (error.message || '未知错误'))
  }
}

// 打开标签对话框
const openTagDialog = (question) => {
  tagDialog.value.currentQuestion = question
  tagDialog.value.tags = [...question.tags]
  tagDialog.value.visible = true
}

// 保存标签
const saveTags = () => {
  if (tagDialog.value.currentQuestion) {
    tagDialog.value.currentQuestion.tags = [...tagDialog.value.tags]
    ElMessage.success('标签更新成功')
  }
  
  tagDialog.value.visible = false
}

// 打开题目详情对话框
const openDetailDialog = (question) => {
  detailDialog.value.question = question
  detailDialog.value.visible = true
}

// 从详情对话框编辑题目
const editFromDetail = () => {
  openQuestionDialog(detailDialog.value.question)
}

// 复制题目文本
const copyQuestionText = () => {
  if (detailDialog.value.question) {
    ElMessage.success('题目文本已复制到剪贴板！')
    navigator.clipboard.writeText(detailDialog.value.question.text)
  }
}

// 导出题目详情
const exportQuestionDetail = () => {
  if (detailDialog.value.question) {
    const data = JSON.stringify(detailDialog.value.question, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${detailDialog.value.question.text.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    ElMessage.success('题目详情已导出！');
  } else {
    ElMessage.warning('请先选择一个题目。');
  }
};

// 将后端 API 的枚举值映射为前端 UI 的类型值
const mapQuestionTypeForUI = (apiType) => {
  const mapping = {
    'single_choice': 'single',
    'multi_choice': 'multiple',
    'sort_order': 'sort',
    'text_input': 'text',
    'number_input': 'number',
    'conditional': 'conditional' // 关联题可以是任何类型，这里保留
  }
  return mapping[apiType] || apiType
}

// 将前端 UI 的类型值映射为后端 API 的枚举值
const mapQuestionTypeForApi = (uiType) => {
  const mapping = {
    'single': 'single_choice',
    'multiple': 'multi_choice',
    'sort': 'sort_order',
    'text': 'text_input',
    'number': 'number_input'
  }
  return mapping[uiType] || uiType
}
</script>

<style scoped>
.question-content {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.category-panel {
  width: 280px;
  flex-shrink: 0;
}

.question-list-wrapper {
  flex: 1;
}

.panel-header {
  margin-bottom: 15px;
}

.filter-input {
  flex: 1;
}

.category-search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.category-node {
  display: flex;
  align-items: center;
  width: 100%;
}

.category-count {
  margin-left: 5px;
  color: #909399;
}

.category-actions {
  display: none;
  margin-left: auto;
}

.category-node:hover .category-actions {
  display: flex;
}

.filter-tags {
  margin-top: 20px;
}

.tags-container {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  cursor: pointer;
}

.active-tag {
  font-weight: bold;
}

.tag-create {
  margin-top: 10px;
  display: flex;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
  padding: 15px;
}

.search-input {
  margin-bottom: 15px;
}

.filters {
  display: flex;
  gap: 10px;
}

.filter-select {
  width: 150px;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f0f9ff;
  padding: 8px 16px;
  margin-bottom: 15px;
  border-radius: 4px;
}

.selected-count {
  font-weight: bold;
  color: #409EFF;
}

.action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.batch-select {
  width: 180px;
}

.question-item {
  display: flex;
  align-items: flex-start;
}

.question-type-tag {
  margin-right: 8px;
  flex-shrink: 0;
}

.question-title {
  word-break: break-word;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-item {
  margin-right: 4px;
}

.options-list {
  margin-bottom: 20px;
}

.option-item {
  margin-bottom: 10px;
}

.option-label {
  width: 30px;
  text-align: center;
}

.add-option {
  margin-top: 10px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.pagination-container .el-pagination {
  --el-pagination-bg-color: #ffffff;
  --el-pagination-text-color: #606266;
  --el-pagination-border-radius: 4px;
  --el-pagination-button-color: #606266;
  --el-pagination-button-bg-color: #ffffff;
  --el-pagination-button-disabled-color: #c0c4cc;
  --el-pagination-button-disabled-bg-color: #ffffff;
  --el-pagination-hover-color: #409eff;
}

.question-detail {
  padding: 20px;
}

.detail-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
  color: #303133;
}

.question-content .question-text {
  font-size: 16px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-all;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.option-item .option-label {
  font-weight: bold;
  color: #409eff;
  margin-right: 10px;
  min-width: 30px;
}

.option-item .option-text {
  flex: 1;
  font-size: 15px;
  color: #333;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  margin: 0;
}

.no-tags {
  color: #909399;
  font-style: italic;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px dashed #dcdfe6;
}

.statistics-note {
  margin-top: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.statistics-note p {
  margin-bottom: 5px;
  font-size: 14px;
  color: #606266;
}

@media (max-width: 768px) {
  .question-content {
    flex-direction: column;
  }
  
  .category-panel {
    width: 100%;
  }
  
  .category-actions {
    display: flex;
  }
}
</style> 