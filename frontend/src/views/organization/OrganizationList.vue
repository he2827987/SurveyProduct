<!-- organization.list.vue -->
<template>
  <div class="org-list-container page-container">
    <div class="flex-between">
      <h1 class="page-title">组织管理</h1>
      <el-button type="primary" @click="openCreateOrgDialog()">创建组织</el-button>
    </div>
    
    <!-- 组织列表 -->
    <div class="card org-list">
      <el-table :data="organizations" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="组织名称" min-width="200">
          <template #default="scope">
            <div class="org-name">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="member_count" label="成员数" width="100" align="center">
          <template #default="scope">
            <el-tag type="info">{{ scope.row.member_count || 0 }}人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="survey_count" label="调研数" width="100" align="center">
          <template #default="scope">
            <el-tag type="success">{{ scope.row.survey_count || 0 }}个</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="editOrganization(scope.row)">编辑</el-button>
            <el-button type="primary" link @click="viewOrganization(scope.row)">查看</el-button>
            <el-popconfirm title="确定要删除该组织吗？" @confirm="deleteOrganization(scope.row)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 创建/编辑组织对话框 -->
    <el-dialog v-model="orgDialog.visible" :title="orgDialog.isEdit ? '编辑组织' : '创建组织'" width="600px">
      <el-form ref="orgFormRef" :model="orgForm" :rules="orgRules" label-width="100px">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="orgForm.name" placeholder="请输入组织名称，如：腾讯科技、阿里巴巴、字节跳动等" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item label="组织描述" prop="description">
          <el-input v-model="orgForm.description" type="textarea" :rows="4" placeholder="请描述组织的基本信息，如：行业、规模、主要业务等" maxlength="1000" show-word-limit />
        </el-form-item>
        <el-form-item label="组织状态">
          <el-switch v-model="orgForm.is_active" active-text="活跃" inactive-text="停用" />
        </el-form-item>
        <el-form-item label="公开组织">
          <el-switch v-model="orgForm.is_public" active-text="公开" inactive-text="私有" />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>公开组织可以被其他用户查看和参与调研</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="orgDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="saveOrganization" :loading="orgDialog.loading">
            {{ orgDialog.isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, InfoFilled } from '@element-plus/icons-vue'
import * as organizationAPI from '@/api/organization'

const loading = ref(false)
const organizations = ref([])

const orgDialog = ref({
  visible: false,
  isEdit: false,
  loading: false
})

const orgFormRef = ref(null)
const orgForm = ref({
  name: '',
  description: '',
  is_active: true,
  is_public: false
})

const orgRules = {
  name: [
    { required: true, message: '请输入组织名称', trigger: 'blur' },
    { min: 2, max: 255, message: '组织名称长度在 2 到 255 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 1000, message: '组织描述不能超过 1000 个字符', trigger: 'blur' }
  ]
}

onMounted(() => {
  loadOrganizations()
})

const loadOrganizations = async () => {
  try {
    loading.value = true
    const response = await organizationAPI.getOrganizations()
    organizations.value = response || []
  } catch (error) {
    console.error('加载组织列表失败:', error)
    ElMessage.error('加载组织列表失败')
  } finally {
    loading.value = false
  }
}

const openCreateOrgDialog = () => {
  orgDialog.value.isEdit = false
  orgDialog.value.visible = true
  orgForm.value = {
    name: '',
    description: '',
    is_active: true,
    is_public: false
  }
}

const editOrganization = (org) => {
  orgDialog.value.isEdit = true
  orgDialog.value.visible = true
  orgForm.value = {
    id: org.id,
    name: org.name,
    description: org.description || '',
    is_active: org.is_active,
    is_public: org.is_public
  }
}

const saveOrganization = async () => {
  try {
    const valid = await orgFormRef.value.validate()
    if (!valid) return
    
    orgDialog.value.loading = true
    
    if (orgDialog.value.isEdit) {
      await organizationAPI.updateOrganization(orgForm.value.id, orgForm.value)
      ElMessage.success('组织更新成功')
    } else {
      await organizationAPI.createOrganization(orgForm.value)
      ElMessage.success('组织创建成功')
    }
    
    orgDialog.value.visible = false
    loadOrganizations()
  } catch (error) {
    console.error('保存组织失败:', error)
    ElMessage.error('保存组织失败')
  } finally {
    orgDialog.value.loading = false
  }
}

const deleteOrganization = async (org) => {
  try {
    await organizationAPI.deleteOrganization(org.id)
    ElMessage.success('组织删除成功')
    loadOrganizations()
  } catch (error) {
    console.error('删除组织失败:', error)
    ElMessage.error('删除组织失败')
  }
}

const viewOrganization = (org) => {
  // 查看组织详情
  console.log('查看组织:', org)
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.org-list-container {
  padding: 20px;
}

.org-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.org-name .el-icon {
  color: #409eff;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
</style>
