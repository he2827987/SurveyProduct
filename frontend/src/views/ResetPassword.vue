<template>
  <div class="reset-container">
    <div class="reset-card">
      <h2 class="title">重置密码</h2>
      <p class="subtitle">请输入您的新密码</p>

      <div v-if="state === 'loading'" class="state-msg">
        <el-icon class="is-loading" :size="20"><Loading /></el-icon>
        <span>正在验证链接...</span>
      </div>

      <div v-else-if="state === 'expired'" class="state-msg error">
        <el-icon :size="20"><CircleCloseFilled /></el-icon>
        <span>重置链接已过期，请重新发送</span>
        <el-button type="primary" size="small" style="margin-top:12px" @click="$router.push('/login')">返回登录</el-button>
      </div>

      <div v-else-if="state === 'error'" class="state-msg error">
        <el-icon :size="20"><CircleCloseFilled /></el-icon>
        <span>{{ errorMsg }}</span>
        <el-button type="primary" size="small" style="margin-top:12px" @click="$router.push('/login')">返回登录</el-button>
      </div>

      <div v-else-if="state === 'success'" class="state-msg success">
        <el-icon :size="20"><CircleCheckFilled /></el-icon>
        <span>密码重置成功！正在跳转到登录页...</span>
      </div>

      <el-form v-else ref="formRef" :model="form" :rules="rules" @submit.prevent="onSubmit">
        <el-form-item prop="newPassword">
          <el-input v-model="form.newPassword" type="password" placeholder="请输入新密码（至少6位）" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请确认新密码" show-password />
        </el-form-item>
        <el-button type="primary" class="wide-btn" @click="onSubmit" :loading="submitting">重置密码</el-button>
        <div class="switch-mode">
          <el-link type="info" @click="$router.push('/login')">返回登录</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, CircleCloseFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import { resetPassword } from '@/api/user'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const state = ref('loading')
const errorMsg = ref('')
const submitting = ref(false)

const form = reactive({
  newPassword: '',
  confirmPassword: '',
})

const rules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

onMounted(() => {
  const token = route.query.token
  if (!token) {
    state.value = 'error'
    errorMsg.value = '缺少重置令牌'
    return
  }
  window.__resetToken = token
  state.value = 'form'
})

const onSubmit = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const token = window.__resetToken
      await resetPassword({
        token,
        new_password: form.newPassword,
      })
      state.value = 'success'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
  } catch (e) {
      const resp = e?.response?.data || {}
      const detail = resp.detail || e.message || '重置失败'
      if (detail.includes('过期') || detail.includes('expired') || detail.includes('无效')) {
        state.value = 'expired'
      } else {
        state.value = 'error'
        errorMsg.value = detail
      }
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.reset-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fa;
}
.reset-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px #0001;
  padding: 32px 24px 18px 24px;
  box-sizing: border-box;
}
.title {
  text-align: center;
  margin: 0 0 6px;
  color: #2d3a4b;
  font-size: 22px;
  font-weight: 600;
}
.subtitle {
  text-align: center;
  margin: 0 0 24px;
  color: #909399;
  font-size: 14px;
}
.wide-btn {
  width: 100%;
  margin-bottom: 12px;
}
.switch-mode {
  text-align: center;
}
.state-msg {
  text-align: center;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #606266;
}
.state-msg.error {
  color: #f56c6c;
}
.state-msg.success {
  color: #67c23a;
}
@media (max-width: 600px) {
  .reset-card {
    max-width: 98vw;
    padding: 18px 4vw 10px 4vw;
  }
}
</style>
