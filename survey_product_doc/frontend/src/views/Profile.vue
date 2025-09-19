<!-- Profile.vue -->
<template>
  <div class="profile-container page-container">
    <div class="profile-header">
      <h1 class="page-title">个人信息</h1>
      <el-button type="primary" @click="saveProfile" :loading="saving">保存修改</el-button>
    </div>

    <div class="profile-content">
      <!-- 基本信息卡片 -->
      <div class="card profile-card">
        <h2 class="section-title">基本信息</h2>
        <el-form 
          ref="profileFormRef" 
          :model="profileForm" 
          :rules="profileRules"
          label-width="120px"
          class="profile-form"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用户名" prop="username">
                <el-input v-model="profileForm.username" placeholder="请输入用户名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="角色">
                <el-tag :type="getRoleType(profileForm.role)">{{ getRoleLabel(profileForm.role) }}</el-tag>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属组织">
                <el-tag v-if="profileForm.organizationName" type="info">
                  {{ profileForm.organizationName }}
                </el-tag>
                <span v-else class="text-muted">未分配组织</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="注册时间">
                <span class="text-muted">{{ formatDate(profileForm.createdAt) }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="最后更新">
                <span class="text-muted">{{ formatDate(profileForm.updatedAt) }}</span>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <!-- 修改密码卡片 -->
      <div class="card password-card">
        <h2 class="section-title">修改密码</h2>
        <el-form 
          ref="passwordFormRef" 
          :model="passwordForm" 
          :rules="passwordRules"
          label-width="120px"
          class="password-form"
        >
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input 
              v-model="passwordForm.currentPassword" 
              type="password" 
              placeholder="请输入当前密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="新密码" prop="newPassword">
            <el-input 
              v-model="passwordForm.newPassword" 
              type="password" 
              placeholder="请输入新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="changePassword" :loading="changingPassword">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentUser, updateUser, changePassword as changePasswordApi } from '@/api/user'

// 个人信息表单
const profileFormRef = ref(null)
const profileForm = ref({
  id: null,
  username: '',
  email: '',
  role: '',
  organizationId: null,
  organizationName: '',
  createdAt: null,
  updatedAt: null
})

// 密码表单
const passwordFormRef = ref(null)
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 加载状态
const saving = ref(false)
const changingPassword = ref(false)

// 表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await getCurrentUser()
    const userData = response.data || response
    
    profileForm.value = {
      id: userData.id,
      username: userData.username,
      email: userData.email,
      role: userData.role,
      organizationId: userData.organization_id,
      organizationName: userData.organization_name || '',
      createdAt: userData.created_at,
      updatedAt: userData.updated_at
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 保存个人信息
const saveProfile = async () => {
  try {
    await profileFormRef.value.validate()
    saving.value = true
    
    const updateData = {
      username: profileForm.value.username,
      email: profileForm.value.email
    }
    
    await updateUser(updateData)
    ElMessage.success('个人信息更新成功')
    
    // 重新获取用户信息
    await fetchUserInfo()
  } catch (error) {
    console.error('保存个人信息失败:', error)
    ElMessage.error('保存个人信息失败')
  } finally {
    saving.value = false
  }
}

// 修改密码
const changePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    await changePasswordApi({
      old_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })
    
    ElMessage.success('密码修改成功')
    
    // 清空密码表单
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    changingPassword.value = false
  }
}

// 获取角色标签类型
const getRoleType = (role) => {
  const roleTypes = {
    'admin': 'danger',
    'manager': 'warning',
    'employee': 'info'
  }
  return roleTypes[role] || 'info'
}

// 获取角色标签文本
const getRoleLabel = (role) => {
  const roleLabels = {
    'admin': '管理员',
    'manager': '经理',
    'employee': '员工'
  }
  return roleLabels[role] || '未知'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.profile-content {
  display: grid;
  gap: 20px;
}

.profile-card,
.password-card {
  padding: 20px;
}

.section-title {
  margin-bottom: 20px;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.profile-form,
.password-form {
  max-width: 600px;
}

.text-muted {
  color: #909399;
}
</style>
