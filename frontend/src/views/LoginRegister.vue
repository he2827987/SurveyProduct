<!-- LoginRegister.vue -->
<template>
  <div class="login-container">
    <el-form
      :model="form"
      :rules="formRules"
      ref="formRef"
      class="login-form"
      @keyup.enter.native="isLoginMode ? onLogin() : onRegister()"
    >
      <h2 class="title">企业问卷调查系统</h2>


      <!-- 注册模式下显示用户名字段 -->
      <el-form-item v-if="!isLoginMode" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" clearable />
      </el-form-item>

      <el-form-item prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" clearable />
      </el-form-item>

      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
      </el-form-item>

      <!-- 注册模式下显示确认密码字段 -->
      <el-form-item v-if="!isLoginMode" prop="confirmPassword">
        <el-input v-model="form.confirmPassword" type="password" placeholder="请确认密码" show-password />
      </el-form-item>

      <!-- 登录模式显示登录按钮和切换到注册的选项 -->
      <template v-if="isLoginMode">
        <el-button type="primary" class="wide-btn" @click="onLogin" :loading="loading">登录</el-button>
        <div class="switch-mode">
          没有账号？<el-link type="primary" @click="switchMode">立即注册</el-link>
        </div>
      </template>

      <!-- 注册模式显示注册按钮和切换到登录的选项 -->
      <template v-else>
        <el-button type="success" class="wide-btn" @click="onRegister" :loading="loading">注册</el-button>
        <div class="switch-mode">
          已有账号？<el-link type="primary" @click="switchMode">返回登录</el-link>
        </div>
      </template>

      <!-- 注册模式下不再需要 companyName 字段，因为注册只创建用户 -->
      <!-- <div class="tip" v-if="!isLoginMode">首次注册将自动创建企业主体</div> -->
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
// 修复API导入，使用正确的函数名
import { login, register } from '@/api/user';

const router = useRouter();
const isLoginMode = ref(true);
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
});
const loading = ref(false);
const formRef = ref(null);

// 表单验证规则
const formRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' },
    { max: 50, message: '用户名长度不能超过50位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]+$/, message: '用户名只能包含字母和数字', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    {
      required: true,
      message: '请确认密码',
      trigger: 'blur',
    },
    {
      validator: (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请再次输入密码'));
        } else if (value !== form.password) {
          callback(new Error('两次输入的密码不一致!'));
        } else {
          callback();
        }
      },
      trigger: 'blur',
    },
  ],
});

// 切换登录/注册模式
const switchMode = () => {
  isLoginMode.value = !isLoginMode.value;
  form.email = '';
  form.password = '';
  form.confirmPassword = '';
  formRef.value?.resetFields();
};

// 修复登录函数
const onLogin = async () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 使用正确的API调用方式
        const loginData = {
          username: form.email, // 后端可能使用username字段
          password: form.password
        };
        const response = await login(loginData);
        
        // 根据后端返回格式处理token
        const token = response.access_token || response.token;
        if (token) {
          localStorage.setItem('access_token', token);
          ElMessage.success('登录成功');
          
          // 检查是否有重定向路径
          const redirect = router.currentRoute.value.query.redirect;
          if (redirect) {
            router.push(redirect);
          } else {
            router.push('/');
          }
        } else {
          ElMessage.error('登录失败：未获取到token');
        }
      } catch (e) {
        console.error('登录失败:', e);
        // 错误信息由 request.js 统一处理
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning('请检查表单输入');
    }
  });
};

// 修复注册函数
const onRegister = async () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 使用正确的API调用方式
        const registerData = {
          username: form.username,
          email: form.email,
          password: form.password
        };
        await register(registerData);
        
        ElMessage.success('注册成功！请登录。');
        switchMode(); // 注册成功后切换到登录模式
        
      } catch (e) {
        console.error('注册失败:', e);
        // 错误信息由 request.js 统一处理
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning('请检查表单输入');
    }
  });
};
</script>

<style scoped>
/* ... (样式部分保持不变) ... */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fa;
}
.login-form {
  width: 100%;
  max-width: 340px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px #0001;
  padding: 32px 24px 18px 24px;
  box-sizing: border-box;
}
.title {
  text-align: center;
  margin-bottom: 24px;
  color: #2d3a4b;
  font-size: 22px;
  font-weight: 600;
}
.wide-btn {
  width: 100%;
  margin-bottom: 15px;
}
.switch-mode {
  text-align: center;
  margin-bottom: 15px;
}
.tip {
  color: #888;
  font-size: 13px;
  text-align: center;
  margin-top: 10px;
}
@media (max-width: 600px) {
  .login-form {
    max-width: 98vw;
    padding: 18px 4vw 10px 4vw;
  }
}
</style>
