<!-- organization.index.vue -->
<template>
  <div class="org-container page-container">
    <div class="flex-between">
      <h1 class="page-title">组织架构管理</h1>
      <el-button type="primary" @click="openAddDeptDialog()">新增部门</el-button>
    </div>
    
    <div class="org-content">
      <div class="card org-tree-container">
        <div class="tree-header">
          <el-input
            v-model="filterText"
            placeholder="输入关键字过滤部门"
            clearable
            class="filter-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <div class="tree-actions">
            <el-button type="primary" link @click="expandAll">全部展开</el-button>
            <el-button type="primary" link @click="collapseAll">全部收起</el-button>
          </div>
        </div>
        
        <el-tree
          ref="treeRef"
          :key="treeKey"
          :data="departments"
          :props="defaultProps"
          :expand-on-click-node="false"
          node-key="id"
          :default-expanded-keys="expandedKeys"
          :filter-node-method="filterNode"
          class="org-tree"
          @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-label">
                <el-icon v-if="data.children && data.children.length">
                  <FolderOpened />
                </el-icon>
                <el-icon v-else>
                  <OfficeBuilding />
                </el-icon>
                <span class="node-text">{{ node.label }}</span>
                <el-tag size="small" type="info" v-if="data.employeeCount">
                  {{ data.employeeCount }}人
                </el-tag>
              </div>
              <div class="node-actions">
                <el-button type="primary" link @click="openAddDeptDialog(data)">
                  添加子部门
                </el-button>
                <el-button type="primary" link @click="editDepartment(data)">
                  编辑
                </el-button>
                <el-button type="danger" link @click.stop="removeDepartment(node, data)">
                  删除
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
      
      <div class="card dept-details" v-if="currentDept.id">
        <div class="dept-header">
          <h2 class="section-title">部门详情</h2>
          <button class="close-btn" @click="closeDeptDetails">
            <span class="close-icon">×</span>
          </button>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="部门名称">
            {{ currentDept.name }}
          </el-descriptions-item>
          <el-descriptions-item label="部门编码">
            {{ currentDept.code || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="上级部门">
            {{ currentDept.parentName || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="人员数量">
            {{ currentDept.employeeCount || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ currentDept.createdAt || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="部门层级">
            {{ currentDept.level || 1 }}级
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ currentDept.remark || '无' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="action-buttons">
          <el-button type="primary" @click="editDepartment(currentDept)">编辑部门</el-button>
          <el-button @click="manageDeptUsers(currentDept)">管理人员</el-button>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑部门对话框 -->
    <el-dialog 
      v-model="deptDialog.visible" 
      :title="deptDialog.isEdit ? '编辑部门' : '新增部门'"
      width="500px"
    >
      <el-form 
        ref="deptFormRef" 
        :model="deptForm" 
        :rules="deptRules"
        label-width="100px"
      >
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="deptForm.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="deptForm.code" placeholder="请输入部门编码" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select
            v-model="deptForm.parentId"
            :data="departmentOptions"
            :props="defaultProps"
            placeholder="请选择上级部门"
            check-strictly
            :render-after-expand="false"
            clearable
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="deptForm.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deptDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="saveDepartment" :loading="deptDialog.loading">
            {{ deptDialog.isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 部门人员管理对话框 -->
    <el-dialog 
      v-model="userDialog.visible" 
      :title="`${userDialog.deptName} - 人员管理`"
      width="800px"
    >
      <div class="user-management">
        <div class="user-actions">
          <el-button type="primary" @click="openAddUserDialog">添加人员</el-button>
          <el-button @click="importUsers">批量导入</el-button>
          <el-button @click="exportUsers">导出人员</el-button>
        </div>
        
        <el-table :data="userDialog.users" border style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="employeeId" label="工号" width="120" />
          <el-table-column prop="position" label="职位" width="150" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="phone" label="电话" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                {{ scope.row.status === 'active' ? '在职' : '离职' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button type="primary" link @click="editUser(scope.row)">编辑</el-button>
              <el-popconfirm
                title="确定要移除该人员吗？"
                @confirm="removeUser(scope.row)"
              >
                <template #reference>
                  <el-button type="danger" link>移除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
    
    <!-- 添加/编辑人员对话框 -->
    <el-dialog 
      v-model="userFormDialog.visible" 
      :title="userFormDialog.isEdit ? '编辑人员' : '添加人员'"
      width="500px"
    >
      <el-form 
        ref="userFormRef" 
        :model="userForm" 
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="工号" prop="employeeId">
          <el-input v-model="userForm.employeeId" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="userForm.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="userForm.status" placeholder="请选择状态">
            <el-option label="在职" value="active" />
            <el-option label="离职" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="userFormDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="saveUser" :loading="userFormDialog.loading">
            {{ userFormDialog.isEdit ? '更新' : '添加' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { FolderOpened, OfficeBuilding, Search, User, Phone, Message } from '@element-plus/icons-vue'

// 部门树的搜索过滤
const filterText = ref('')
const treeRef = ref(null)
const expandedKeys = ref([1]) // 默认展开根节点
const treeKey = ref(0) // 用于强制重新渲染树组件

// 当前选中的部门
const currentDept = ref({})

// 部门树数据
const departments = ref([
  {
    id: 1,
    name: '总公司',
    code: 'HQ',
    employeeCount: 120,
    createdAt: '2023-01-01',
    children: [
      {
        id: 2,
        name: '研发部',
        code: 'RD',
        employeeCount: 45,
        createdAt: '2023-01-02',
        children: [
          {
            id: 5,
            name: '前端组',
            code: 'FE',
            employeeCount: 12,
            createdAt: '2023-01-05'
          },
          {
            id: 6,
            name: '后端组',
            code: 'BE',
            employeeCount: 15,
            createdAt: '2023-01-05'
          },
          {
            id: 7,
            name: '测试组',
            code: 'QA',
            employeeCount: 8,
            createdAt: '2023-01-05'
          },
          {
            id: 8,
            name: '运维组',
            code: 'OPS',
            employeeCount: 10,
            createdAt: '2023-01-05'
          }
        ]
      },
      {
        id: 3,
        name: '市场部',
        code: 'MKT',
        employeeCount: 30,
        createdAt: '2023-01-03',
        children: [
          {
            id: 9,
            name: '国内市场组',
            code: 'MKT-CN',
            employeeCount: 18,
            createdAt: '2023-01-10'
          },
          {
            id: 10,
            name: '国际市场组',
            code: 'MKT-INT',
            employeeCount: 12,
            createdAt: '2023-01-10'
          }
        ]
      },
      {
        id: 4,
        name: '财务部',
        code: 'FIN',
        employeeCount: 15,
        createdAt: '2023-01-04',
        children: []
      }
    ]
  }
])

// 树节点配置
const defaultProps = {
  children: 'children',
  label: 'name'
}

// 部门选项（用于上级部门选择）
const departmentOptions = computed(() => {
  const options = []
  
  const addOption = (dept, level = 0) => {
    options.push({
      id: dept.id,
      name: '　'.repeat(level) + dept.name,
      children: dept.children || []
    })
    
    if (dept.children && dept.children.length > 0) {
      dept.children.forEach(child => addOption(child, level + 1))
    }
  }
  
  departments.value.forEach(dept => addOption(dept))
  return options
})

// 部门对话框
const deptDialog = ref({
  visible: false,
  isEdit: false,
  loading: false
})

// 部门表单
const deptFormRef = ref(null)
const deptForm = ref({
  name: '',
  code: '',
  parentId: null,
  remark: ''
})

// 部门表单验证规则
const deptRules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '部门名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入部门编码', trigger: 'blur' },
    { pattern: /^[A-Z0-9_-]+$/, message: '部门编码只能包含大写字母、数字、下划线和横线', trigger: 'blur' }
  ]
}

// 人员管理对话框
const userDialog = ref({
  visible: false,
  deptName: '',
  users: []
})

// 人员表单对话框
const userFormDialog = ref({
  visible: false,
  isEdit: false,
  loading: false
})

// 人员表单
const userFormRef = ref(null)
const userForm = ref({
  name: '',
  employeeId: '',
  position: '',
  email: '',
  phone: '',
  status: 'active'
})

// 人员表单验证规则
const userRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  employeeId: [
    { required: true, message: '请输入工号', trigger: 'blur' }
  ],
  position: [
    { required: true, message: '请输入职位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 获取所有节点ID的辅助函数
const getAllIds = (nodes) => {
  let ids = []
  nodes.forEach(node => {
    ids.push(node.id)
    if (node.children && node.children.length > 0) {
      ids = ids.concat(getAllIds(node.children))
    }
  })
  return ids
}

// 展开/收起所有节点
const expandAll = () => {
  console.log('expandAll 函数被调用')
  
  const allIds = getAllIds(departments.value)
  console.log('所有节点ID:', allIds)
  
  // 设置展开的键并强制重新渲染
  expandedKeys.value = allIds
  treeKey.value++ // 强制重新创建树组件
  
  console.log('展开所有节点，expandedKeys:', expandedKeys.value)
}

const collapseAll = () => {
  console.log('collapseAll 函数被调用')
  
  // 清空展开的键并强制重新渲染
  expandedKeys.value = []
  treeKey.value++ // 强制重新创建树组件
  
  console.log('收起所有节点，expandedKeys:', expandedKeys.value)
}

// 过滤节点
const filterNode = (value, data) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase()) ||
         data.code.toLowerCase().includes(value.toLowerCase())
}

// 监听过滤文本变化
watch(filterText, (val) => {
  treeRef.value?.filter(val)
})

// 处理节点点击
const handleNodeClick = (data) => {
  currentDept.value = { ...data }
}

// 打开添加部门对话框
const openAddDeptDialog = (parentDept = null) => {
  deptDialog.value.isEdit = false
  deptDialog.value.visible = true
  deptForm.value = {
    name: '',
    code: '',
    parentId: parentDept ? parentDept.id : null,
    remark: ''
  }
}

// 编辑部门
const editDepartment = (dept) => {
  deptDialog.value.isEdit = true
  deptDialog.value.visible = true
  deptForm.value = {
    id: dept.id,
    name: dept.name,
    code: dept.code,
    parentId: dept.parentId,
    remark: dept.remark || ''
  }
}

// 保存部门
const saveDepartment = async () => {
  try {
    deptDialog.value.loading = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (deptDialog.value.isEdit) {
      // 更新部门
      updateDepartmentInTree(deptForm.value)
      ElMessage.success('部门更新成功')
    } else {
      // 创建部门
      const newDept = {
        id: Date.now(),
        name: deptForm.value.name,
        code: deptForm.value.code,
        employeeCount: 0,
        createdAt: new Date().toISOString().split('T')[0],
        remark: deptForm.value.remark,
        children: []
      }
      
      addDepartmentToTree(newDept, deptForm.value.parentId)
      ElMessage.success('部门创建成功')
    }
    
    deptDialog.value.visible = false
  } catch (error) {
    console.error('保存部门失败:', error)
    ElMessage.error('保存部门失败')
  } finally {
    deptDialog.value.loading = false
  }
}

// 删除部门
const removeDepartment = async (node, data) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该部门吗？删除后将无法恢复，且会同时删除所有子部门。',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    removeDepartmentFromTree(data.id)
    ElMessage.success('部门删除成功')
    
    // 如果删除的是当前选中的部门，清空选中状态
    if (currentDept.value.id === data.id) {
      currentDept.value = {}
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除部门失败:', error)
      ElMessage.error('删除部门失败')
    }
  }
}

// 管理部门人员
const manageDeptUsers = (dept) => {
  userDialog.value.deptName = dept.name
  userDialog.value.users = getMockUsers(dept.id)
  userDialog.value.visible = true
}

// 打开添加人员对话框
const openAddUserDialog = () => {
  userFormDialog.value.isEdit = false
  userFormDialog.value.visible = true
  userForm.value = {
    name: '',
    employeeId: '',
    position: '',
    email: '',
    phone: '',
    status: 'active'
  }
}

// 编辑人员
const editUser = (user) => {
  userFormDialog.value.isEdit = true
  userFormDialog.value.visible = true
  userForm.value = { ...user }
}

// 保存人员
const saveUser = async () => {
  try {
    userFormDialog.value.loading = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (userFormDialog.value.isEdit) {
      // 更新人员
      const index = userDialog.value.users.findIndex(u => u.id === userForm.value.id)
      if (index !== -1) {
        userDialog.value.users[index] = { ...userForm.value }
      }
      ElMessage.success('人员信息更新成功')
    } else {
      // 添加人员
      const newUser = {
        id: Date.now(),
        ...userForm.value
      }
      userDialog.value.users.push(newUser)
      ElMessage.success('人员添加成功')
    }
    
    userFormDialog.value.visible = false
  } catch (error) {
    console.error('保存人员失败:', error)
    ElMessage.error('保存人员失败')
  } finally {
    userFormDialog.value.loading = false
  }
}

// 移除人员
const removeUser = async (user) => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const index = userDialog.value.users.findIndex(u => u.id === user.id)
    if (index !== -1) {
      userDialog.value.users.splice(index, 1)
    }
    ElMessage.success('人员移除成功')
  } catch (error) {
    console.error('移除人员失败:', error)
    ElMessage.error('移除人员失败')
  }
}

// 批量导入人员
const importUsers = () => {
  ElMessage.info('批量导入功能开发中...')
}

// 导出人员
const exportUsers = () => {
  try {
    const headers = ['姓名', '工号', '职位', '邮箱', '电话', '状态']
    const csvContent = [
      headers.join(','),
      ...userDialog.value.users.map(user => [
        user.name,
        user.employeeId,
        user.position,
        user.email,
        user.phone,
        user.status === 'active' ? '在职' : '离职'
      ].join(','))
    ].join('\n')
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${userDialog.value.deptName}_人员列表_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    
    ElMessage.success('人员列表导出成功')
  } catch (error) {
    console.error('导出人员列表失败:', error)
    ElMessage.error('导出人员列表失败')
  }
}

// 关闭部门详情
const closeDeptDetails = () => {
  currentDept.value = {}
}
// 工具方法：更新部门树中的部门
const updateDepartmentInTree = (deptData) => {
  const updateDept = (nodes) => {
    for (let node of nodes) {
      if (node.id === deptData.id) {
        Object.assign(node, deptData)
        return true
      }
      if (node.children && node.children.length > 0) {
        if (updateDept(node.children)) return true
      }
    }
    return false
  }
  updateDept(departments.value)
}

// 工具方法：向部门树添加部门
const addDepartmentToTree = (newDept, parentId) => {
  if (!parentId) {
    departments.value.push(newDept)
    return
  }
  
  const addToParent = (nodes) => {
    for (let node of nodes) {
      if (node.id === parentId) {
        if (!node.children) node.children = []
        node.children.push(newDept)
        return true
      }
      if (node.children && node.children.length > 0) {
        if (addToParent(node.children)) return true
      }
    }
    return false
  }
  addToParent(departments.value)
}

// 工具方法：从部门树删除部门
const removeDepartmentFromTree = (deptId) => {
  const removeDept = (nodes) => {
    for (let i = 0; i < nodes.length; i++) {
      if (nodes[i].id === deptId) {
        nodes.splice(i, 1)
        return true
      }
      if (nodes[i].children && nodes[i].children.length > 0) {
        if (removeDept(nodes[i].children)) return true
      }
    }
    return false
  }
  removeDept(departments.value)
}

// 工具方法：获取模拟用户数据
const getMockUsers = (deptId) => {
  const mockUsers = {
    1: [
      { id: 1, name: '张三', employeeId: 'HQ001', position: '总经理', email: 'zhangsan@company.com', phone: '13800000001', status: 'active' },
      { id: 2, name: '李四', employeeId: 'HQ002', position: '副总经理', email: 'lisi@company.com', phone: '13800000002', status: 'active' }
    ],
    2: [
      { id: 3, name: '王五', employeeId: 'RD001', position: '研发总监', email: 'wangwu@company.com', phone: '13800000003', status: 'active' },
      { id: 4, name: '赵六', employeeId: 'RD002', position: '技术经理', email: 'zhaoliu@company.com', phone: '13800000004', status: 'active' }
    ],
    5: [
      { id: 5, name: '钱七', employeeId: 'FE001', position: '前端工程师', email: 'qianqi@company.com', phone: '13800000005', status: 'active' },
      { id: 6, name: '孙八', employeeId: 'FE002', position: '前端工程师', email: 'sunba@company.com', phone: '13800000006', status: 'active' }
    ]
  }
  return mockUsers[deptId] || []
}
</script>

<style scoped>
.org-content {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.org-tree-container {
  flex: 1;
  min-width: 400px;
}

.dept-details {
  flex: 1;
  min-width: 300px;
  position: relative;
}

.dept-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #f56c6c;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background-color: #e74c3c;
}

.close-icon {
  color: white;
  font-size: 16px;
  font-weight: bold;
  line-height: 1;
}

.filter-input {
  margin-bottom: 20px;
}

.org-tree {
  margin-top: 8px;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tree-actions {
  display: flex;
  gap: 10px;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 5px 0;
}

.node-label {
  display: flex;
  align-items: center;
}

.node-text {
  margin-left: 6px;
}

.node-actions {
  display: none;
}

.tree-node:hover .node-actions {
  display: block;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
  gap: 10px;
}

.user-management {
  padding: 20px;
}

.user-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
  gap: 10px;
}

.user-search {
  width: 250px;
}

.add-user-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

@media (max-width: 768px) {
  .org-content {
    flex-direction: column;
  }
  
  .tree-node {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .node-actions {
    display: block;
    margin-top: 5px;
  }
}
</style> 