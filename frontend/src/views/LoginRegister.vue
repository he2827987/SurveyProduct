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
          <el-link type="info" @click="openForgotPassword" :underline="false">忘记密码？点击此处找回</el-link>
        </div>
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
    </el-form>

    <!-- 忘记密码对话框 -->
    <el-dialog v-model="forgotVisible" title="找回密码" width="400px" :close-on-click-modal="false" center>
      <!-- Step 1: 输入邮箱 -->
      <div v-if="forgotStep === 1">
        <el-form :model="forgotForm" :rules="forgotRules" ref="forgotFormRef" label-width="0">
          <el-form-item prop="email">
            <el-input v-model="forgotForm.email" placeholder="请输入注册时使用的邮箱" clearable />
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="forgotVisible = false">取消</el-button>
          <el-button type="primary" @click="onSendCode" :loading="forgotLoading">发送验证码</el-button>
        </div>
      </div>

      <!-- Step 2: 输入验证码 -->
      <div v-if="forgotStep === 2">
        <el-form :model="forgotForm" ref="codeFormRef" label-width="0">
          <el-form-item>
            <el-input v-model="forgotForm.code" placeholder="请输入6位验证码" maxlength="6" clearable />
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="forgotStep = 1">上一步</el-button>
          <el-button type="primary" @click="onVerifyCode" :loading="forgotLoading">验证</el-button>
        </div>
      </div>

      <!-- Step 3: 设置新密码 -->
      <div v-if="forgotStep === 3">
        <el-form :model="forgotForm" ref="resetFormRef" label-width="0">
          <el-form-item>
            <el-input v-model="forgotForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" show-password />
          </el-form-item>
          <el-form-item>
            <el-input v-model="forgotForm.confirmNewPassword" type="password" placeholder="请确认新密码" show-password />
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="forgotStep = 2">上一步</el-button>
          <el-button type="primary" @click="onResetPassword" :loading="forgotLoading">重置密码</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { login, register, forgotPassword, verifyResetCode, resetPassword } from '@/api/user';

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

onMounted(() => {
  const token = localStorage.getItem('access_token');
  const tokenFromStorage = localStorage.getItem('user_info');
  
  if (token && tokenFromStorage) {
    console.log('检测到已登录状态，显示提示信息');
    ElMessage.info('您已登录，正在跳转到首页...');
    setTimeout(() => {
      router.push('/');
    }, 1000);
  }
});

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

const switchMode = () => {
  isLoginMode.value = !isLoginMode.value;
  form.email = '';
  form.password = '';
  form.confirmPassword = '';
  formRef.value?.resetFields();
};

const onLogin = async () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const loginData = {
          username: form.email,
          password: form.password
        };
        const response = await login(loginData);
        
        const token = response.access_token || response.token;
        if (token) {
          localStorage.setItem('access_token', token);
          
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const userInfo = {
              id: payload.sub,
              username: payload.sub,
            };
            localStorage.setItem('user_info', JSON.stringify(userInfo));
            console.log('用户信息已保存:', userInfo);
          } catch (error) {
            console.error('解码token失败:', error);
            const userInfo = {
              id: form.email,
              username: form.email
            };
            localStorage.setItem('user_info', JSON.stringify(userInfo));
          }
          
          ElMessage.success('登录成功');
          
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
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning('请检查表单输入');
    }
  });
};

const onRegister = async () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const registerData = {
          username: form.username,
          email: form.email,
          password: form.password
        };
        await register(registerData);
        
        ElMessage.success('注册成功！请登录。');
        switchMode();
        
      } catch (e) {
        console.error('注册失败:', e);
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning('请检查表单输入');
    }
  });
};

// ===== 忘记密码相关 =====
const forgotVisible = ref(false);
const forgotStep = ref(1);
const forgotLoading = ref(false);
const forgotFormRef = ref(null);
const forgotForm = reactive({
  email: '',
  code: '',
  newPassword: '',
  confirmNewPassword: '',
});
const forgotRules = reactive({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
});

const openForgotPassword = () => {
  forgotForm.email = '';
  forgotForm.code = '';
  forgotForm.newPassword = '';
  forgotForm.confirmNewPassword = '';
  forgotStep.value = 1;
  forgotVisible.value = true;
};

const onSendCode = async () => {
  forgotFormRef.value?.validate(async (valid) => {
    if (!valid) return;
    forgotLoading.value = true;
    try {
      await forgotPassword({ email: forgotForm.email });
      ElMessage.success('验证码已发送');
      forgotStep.value = 2;
    } catch (e) {
      console.error('发送验证码失败:', e);
    } finally {
      forgotLoading.value = false;
    }
  });
};

const onVerifyCode = async () => {
  if (!forgotForm.code || forgotForm.code.length !== 6) {
    ElMessage.warning('请输入6位验证码');
    return;
  }
  forgotLoading.value = true;
  try {
    await verifyResetCode({ email: forgotForm.email, code: forgotForm.code });
    ElMessage.success('验证码验证成功');
    forgotStep.value = 3;
  } catch (e) {
    console.error('验证码验证失败:', e);
  } finally {
    forgotLoading.value = false;
  }
};

const onResetPassword = async () => {
  if (!forgotForm.newPassword || forgotForm.newPassword.length < 6) {
    ElMessage.warning('密码长度不能少于6位');
    return;
  }
  if (forgotForm.newPassword !== forgotForm.confirmNewPassword) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }
  forgotLoading.value = true;
  try {
    await resetPassword({
      email: forgotForm.email,
      code: forgotForm.code,
      new_password: forgotForm.newPassword,
    });
    ElMessage.success('密码重置成功，请使用新密码登录');
    forgotVisible.value = false;
    form.email = forgotForm.email;
    form.password = '';
  } catch (e) {
    console.error('重置密码失败:', e);
  } finally {
    forgotLoading.value = false;
  }
};
</script>

<style scoped>
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
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}
@media (max-width: 600px) {
  .login-form {
    max-width: 98vw;
    padding: 18px 4vw 10px 4vw;
  }
}
</style>
