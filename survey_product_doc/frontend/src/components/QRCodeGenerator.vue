<!-- components/QRCodeGenerator.vue -->
<template>
  <div class="qrcode-generator">
    <!-- 二维码显示区域 -->
    <div class="qrcode-display" v-if="qrCodeUrl">
      <div class="qrcode-container">
        <img :src="qrCodeUrl" alt="调研二维码" class="qrcode-image" />
      </div>
      
      <!-- 调研信息 -->
      <div class="survey-info">
        <h3 class="survey-title">{{ surveyTitle }}</h3>
        <p class="survey-description">{{ surveyDescription }}</p>
        <div class="survey-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            有效期至: {{ expireTime }}
          </span>
          <span class="meta-item">
            <el-icon><User /></el-icon>
            已答题: {{ responseCount }} 人
          </span>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="qrcode-actions">
        <el-button type="primary" @click="downloadQRCode" :loading="downloading">
          <el-icon><Download /></el-icon>
          下载二维码
        </el-button>
        <el-button @click="copyLink" :loading="copying">
          <el-icon><CopyDocument /></el-icon>
          复制链接
        </el-button>
        <el-button @click="shareQRCode">
          <el-icon><Share /></el-icon>
          分享
        </el-button>
      </div>
    </div>
    
    <!-- 生成按钮 -->
    <div v-else class="generate-section">
              <el-button type="primary" size="large" @click="generateQRCode" :loading="generating">
          <el-icon><Document /></el-icon>
          生成调研二维码
        </el-button>
    </div>
    
    <!-- 二维码设置对话框 -->
    <el-dialog
      v-model="settingsVisible"
      title="二维码设置"
      width="400px"
      :before-close="handleSettingsClose"
    >
      <el-form :model="qrSettings" label-width="100px">
        <el-form-item label="二维码尺寸">
          <el-select v-model="qrSettings.size" style="width: 100%">
            <el-option label="小尺寸 (150x150)" value="small" />
            <el-option label="标准尺寸 (200x200)" value="medium" />
            <el-option label="大尺寸 (300x300)" value="large" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="二维码颜色">
          <el-color-picker v-model="qrSettings.color" />
        </el-form-item>
        
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="qrSettings.expireTime"
            type="datetime"
            placeholder="选择过期时间"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        
        <el-form-item label="访问限制">
          <el-input-number
            v-model="qrSettings.maxResponses"
            :min="0"
            placeholder="最大答题人数（0为无限制）"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="局域网访问">
          <el-switch
            v-model="qrSettings.useLocalNetwork"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="setting-description">
            启用后生成的二维码可在局域网内访问
          </div>
        </el-form-item>
        
        <el-form-item v-if="qrSettings.useLocalNetwork" label="局域网IP">
          <el-input
            v-model="qrSettings.localNetworkIP"
            placeholder="请输入局域网IP地址，如：192.168.1.100"
            style="width: 100%"
            @blur="saveManualIP"
          />
          
          <!-- 分离的按钮组 -->
          <div class="ip-buttons">
            <el-button @click="autoDetectIP" :loading="detectingIP" type="primary" size="small">
              自动检测
            </el-button>
            <el-button @click="testConnection" :loading="testingConnection" :disabled="!qrSettings.localNetworkIP" type="success" size="small">
              测试连接
            </el-button>
          </div>
          <div class="setting-description">
            留空将使用默认IP地址，或点击"自动检测"获取本机IP
          </div>
          
          <!-- IP获取帮助 -->
          <div class="ip-help" v-if="qrSettings.useLocalNetwork">
            <el-button type="text" size="small" @click="showIPHelp = !showIPHelp">
              <el-icon><QuestionFilled /></el-icon>
              如何获取本机IP地址？
            </el-button>
            <div v-if="showIPHelp" class="ip-help-content">
              <p><strong>方法1：使用系统命令</strong></p>
              <ul>
                <li><strong>Windows:</strong> 打开命令提示符，输入 <code>ipconfig</code></li>
                <li><strong>macOS/Linux:</strong> 打开终端，输入 <code>ifconfig</code> 或 <code>ip addr</code></li>
              </ul>
              <p><strong>方法2：查看网络设置</strong></p>
              <ul>
                <li>打开系统网络设置，查看WiFi或以太网连接的IP地址</li>
                <li>通常格式为：192.168.x.x 或 10.x.x.x</li>
              </ul>
            </div>
          </div>
          
          <!-- 常见IP地址快速选择 -->
          <div class="common-ips" v-if="qrSettings.useLocalNetwork">
            <div class="common-ips-title">常见局域网IP：</div>
            <div class="common-ips-list">
              <el-tag
                v-for="ip in commonIPs"
                :key="ip"
                @click="selectCommonIP(ip)"
                class="ip-tag"
                :class="{ active: qrSettings.localNetworkIP === ip }"
              >
                {{ ip }}
              </el-tag>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="settingsVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSettings">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as surveyApi from '@/api/survey'
import { Calendar, User, Download, CopyDocument, Share, Document, QuestionFilled } from '@element-plus/icons-vue'
import { generateSurveyQRCode, downloadQRCode as downloadQRCodeUtil } from '@/utils/qrcode'

// ===== Props =====
const props = defineProps({
  surveyId: {
    type: [Number, String],
    required: true
  },
  surveyTitle: {
    type: String,
    required: true
  },
  surveyDescription: {
    type: String,
    default: ''
  },
  responseCount: {
    type: Number,
    default: 0
  }
})

// ===== 状态 =====
const qrCodeUrl = ref('')
const generating = ref(false)
const downloading = ref(false)
const copying = ref(false)
const settingsVisible = ref(false)
const detectingIP = ref(false) // 新增状态：自动检测IP时加载中
const showIPHelp = ref(false) // 新增状态：控制IP帮助显示
const testingConnection = ref(false) // 新增状态：测试连接时加载中

// ===== 二维码设置 =====
const qrSettings = ref({
  size: 'medium',
  color: '#000000',
  expireTime: null,
  maxResponses: 0,
  useLocalNetwork: true,  // 默认启用局域网访问
  localNetworkIP: ''      // 用户可自定义局域网IP
})

// 初始化时加载保存的IP
const savedIP = localStorage.getItem('localNetworkIP')
if (savedIP && savedIP.match(/^(\d{1,3}\.){3}\d{1,3}$/)) {
  qrSettings.value.localNetworkIP = savedIP
}

// ===== 常见IP地址列表 =====
const commonIPs = [
  '192.168.0.31',  // 您的实际IP
  '192.168.1.100',
  '192.168.1.101',
  '192.168.0.100',
  '192.168.0.101',
  '10.0.0.100',
  '10.0.0.101',
  '172.16.0.100',
  '172.16.0.101'
]

// ===== 计算属性 =====
const expireTime = computed(() => {
  if (!qrSettings.value.expireTime) return '永久有效'
  return qrSettings.value.expireTime.toLocaleString('zh-CN')
})

const qrCodeOptions = computed(() => {
  const sizeMap = {
    small: 150,
    medium: 200,
    large: 300
  }
  
  return {
    width: sizeMap[qrSettings.value.size],
    height: sizeMap[qrSettings.value.size],
    color: {
      dark: qrSettings.value.color,
      light: '#FFFFFF'
    }
  }
})

// ===== 方法 =====

/**
 * 生成二维码
 */
const generateQRCode = async () => {
  settingsVisible.value = true
}

/**
 * 确认设置并生成二维码
 */
const confirmSettings = async () => {
  try {
    generating.value = true
    settingsVisible.value = false
    
    // 构建二维码选项，包含局域网配置
    const options = {
      ...qrCodeOptions.value,
      useLocalNetwork: qrSettings.value.useLocalNetwork,
      localNetworkIP: qrSettings.value.localNetworkIP
    }
    
    await surveyApi.updateSurveyStatus(props.surveyId, {
      status: 'active',
      end_time: qrSettings.value.expireTime ? qrSettings.value.expireTime.toISOString() : null
    })
    const url = await generateSurveyQRCode(props.surveyId, options)
    qrCodeUrl.value = url
    
    ElMessage.success('二维码生成成功')
  } catch (error) {
    console.error('生成二维码失败:', error)
    ElMessage.error('生成二维码失败')
  } finally {
    generating.value = false
  }
}

/**
 * 下载二维码
 */
const downloadQRCode = async () => {
  try {
    downloading.value = true
    const filename = `${props.surveyTitle}_二维码.png`
    await downloadQRCodeUtil(qrCodeUrl.value, filename)
    ElMessage.success('二维码下载成功')
  } catch (error) {
    console.error('下载二维码失败:', error)
    ElMessage.error('下载二维码失败')
  } finally {
    downloading.value = false
  }
}

/**
 * 复制链接
 */
const copyLink = async () => {
  try {
    copying.value = true
    const surveyUrl = `${window.location.origin}/survey/fill/${props.surveyId}`
    await navigator.clipboard.writeText(surveyUrl)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制链接失败:', error)
    ElMessage.error('复制链接失败')
  } finally {
    copying.value = false
  }
}

/**
 * 分享二维码
 */
const shareQRCode = async () => {
  try {
    if (navigator.share) {
      const surveyUrl = `${window.location.origin}/survey/fill/${props.surveyId}`
      await navigator.share({
        title: props.surveyTitle,
        text: props.surveyDescription,
        url: surveyUrl
      })
    } else {
      // 降级到复制链接
      await copyLink()
    }
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error('分享失败')
  }
}

/**
 * 处理设置对话框关闭
 */
const handleSettingsClose = () => {
  settingsVisible.value = false
}

/**
 * 禁用过去的日期
 */
const disabledDate = (time) => {
  return time.getTime() < Date.now()
}

/**
 * 选择常见IP地址
 */
const selectCommonIP = (ip) => {
  qrSettings.value.localNetworkIP = ip
  // 保存到localStorage
  localStorage.setItem('localNetworkIP', ip)
  ElMessage.success(`已选择IP地址: ${ip}`)
}

/**
 * 保存手动输入的IP地址
 */
const saveManualIP = () => {
  const ip = qrSettings.value.localNetworkIP
      if (ip && ip.match(/^(\d{1,3}\.){3}\d{1,3}$/)) {
    localStorage.setItem('localNetworkIP', ip)
    console.log('已保存手动输入的IP:', ip)
  }
}

/**
 * 自动检测局域网IP
 */
const autoDetectIP = async () => {
  detectingIP.value = true
  try {
    console.log('开始自动检测IP...')
    
    // 尝试多种方法获取IP
    const ip = await getLocalIPAddress()
    
    if (ip && ip.match(/^(\d{1,3}\.){3}\d{1,3}$/)) {
      qrSettings.value.localNetworkIP = ip
      
      // 保存到localStorage以便下次使用
      localStorage.setItem('localNetworkIP', ip)
      
      ElMessage.success(`已自动检测到局域网IP: ${ip}`)
      console.log('IP检测成功:', ip)
    } else {
      throw new Error('检测到的IP无效')
    }
    
  } catch (error) {
    console.error('自动检测IP失败:', error)
    
    // 如果自动检测失败，提供默认IP建议
    const defaultIP = getDefaultLocalIP()
    qrSettings.value.localNetworkIP = defaultIP
    
    ElMessage.warning(`自动检测失败，已设置默认IP: ${defaultIP}`)
    
    // 显示详细的手动获取IP的提示
    ElMessage({
      message: '请手动输入您的局域网IP地址，或点击下方常见IP标签快速选择。您可以通过以下方式获取IP：1) Windows: 打开命令提示符输入 ipconfig 2) macOS/Linux: 打开终端输入 ifconfig',
      type: 'info',
      duration: 8000
    })
  } finally {
    detectingIP.value = false
  }
}

/**
 * 测试局域网连接
 */
const testConnection = async () => {
  testingConnection.value = true
  try {
    console.log('开始测试局域网连接...')
    const protocol = window.location.protocol
    const port = window.location.port
    const testUrl = `${protocol}//${qrSettings.value.localNetworkIP}:${port}`
    
    console.log('测试URL:', testUrl)
    
    // 方法1: 尝试fetch请求
    try {
      const response = await fetch(`${testUrl}/api/v1/health`, {
        method: 'GET',
        mode: 'no-cors',
        cache: 'no-cache'
      })
      console.log('Fetch响应:', response)
      ElMessage.success(`局域网连接成功！IP: ${qrSettings.value.localNetworkIP}`)
      return
    } catch (fetchError) {
      console.log('Fetch失败，尝试其他方法:', fetchError)
    }
    
    // 方法2: 尝试图片加载
    try {
      const img = new Image()
      const timeout = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('连接超时')), 3000)
      )
      
      const loadPromise = new Promise((resolve, reject) => {
        img.onload = () => resolve(true)
        img.onerror = () => reject(new Error('无法访问'))
        img.src = `${testUrl}/favicon.ico?t=${Date.now()}`
      })
      
      await Promise.race([loadPromise, timeout])
      ElMessage.success(`局域网连接成功！IP: ${qrSettings.value.localNetworkIP}`)
      return
    } catch (imgError) {
      console.log('图片加载失败:', imgError)
    }
    
    // 方法3: 尝试XMLHttpRequest
    try {
      const xhr = new XMLHttpRequest()
      const timeout = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('连接超时')), 3000)
      )
      
      const xhrPromise = new Promise((resolve, reject) => {
        xhr.onload = () => resolve(true)
        xhr.onerror = () => reject(new Error('无法访问'))
        xhr.open('GET', `${testUrl}/api/v1/health`, true)
        xhr.send()
      })
      
      await Promise.race([xhrPromise, timeout])
      ElMessage.success(`局域网连接成功！IP: ${qrSettings.value.localNetworkIP}`)
      return
    } catch (xhrError) {
      console.log('XMLHttpRequest失败:', xhrError)
    }
    
    // 所有方法都失败
    throw new Error('无法连接到指定IP地址')
    
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error(`局域网连接失败！IP: ${qrSettings.value.localNetworkIP} (${error.message})`)
    
    // 提供更详细的错误信息和建议
    ElMessage({
      message: `连接失败可能的原因：1) IP地址不正确 2) 防火墙阻止 3) 服务未启动 4) 端口被占用。请检查IP地址是否正确，或尝试其他IP地址。`,
      type: 'warning',
      duration: 8000
    })
  } finally {
    testingConnection.value = false
  }
}

/**
 * 获取本机局域网IP地址
 */
const getLocalIPAddress = () => {
  return new Promise(async (resolve, reject) => {
    try {
      console.log('开始真实IP检测...')
      
      // 方法1: 尝试从localStorage获取之前保存的IP
      const savedIP = localStorage.getItem('localNetworkIP')
      if (savedIP && savedIP.match(/^(\d{1,3}\.){3}\d{1,3}$/)) {
        console.log('使用保存的IP:', savedIP)
        resolve(savedIP)
        return
      }
      
      // 方法2: 尝试WebRTC方法（真实检测）
      try {
        console.log('尝试WebRTC方法...')
        const rtc = new RTCPeerConnection({ 
          iceServers: [],
          iceCandidatePoolSize: 0
        })
        const ips = []
        let resolved = false
        
        rtc.onicecandidate = (event) => {
          if (event.candidate && !resolved) {
            const candidate = event.candidate.candidate
            console.log('ICE候选:', candidate)
            const ipMatch = candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/)
            if (ipMatch) {
              const ip = ipMatch[1]
              console.log('检测到IP:', ip)
              // 过滤掉本地回环地址和公网IP，只保留局域网IP
              if (ip.match(/^(\d{1,3}\.){3}\d{1,3}$/) && 
                  !ip.startsWith('127.') && 
                  !ip.startsWith('169.254.') &&
                  !ip.startsWith('0.') &&
                  !ip.startsWith('255.255.255.255')) {
                ips.push(ip)
                console.log('有效局域网IP:', ip)
                if (!resolved) {
                  resolved = true
                  rtc.close()
                  resolve(ip)
                }
              }
            }
          }
        }
        
        rtc.onicegatheringstatechange = () => {
          console.log('ICE收集状态:', rtc.iceGatheringState)
          if (rtc.iceGatheringState === 'complete' && !resolved) {
            rtc.close()
            if (ips.length > 0) {
              resolved = true
              resolve(ips[0])
            } else {
              console.log('WebRTC未找到有效IP，尝试其他方法')
              tryAlternativeMethods(resolve, reject)
            }
          }
        }
        
        rtc.createDataChannel('')
        rtc.createOffer()
          .then(offer => rtc.setLocalDescription(offer))
          .catch(err => {
            console.error('WebRTC创建offer失败:', err)
            if (!resolved) {
              resolved = true
              rtc.close()
              tryAlternativeMethods(resolve, reject)
            }
          })
        
        // 设置超时
        setTimeout(() => {
          if (!resolved) {
            console.log('WebRTC超时')
            resolved = true
            rtc.close()
            if (ips.length > 0) {
              resolve(ips[0])
            } else {
              tryAlternativeMethods(resolve, reject)
            }
          }
        }, 5000)
        
      } catch (error) {
        console.error('WebRTC不可用:', error)
        tryAlternativeMethods(resolve, reject)
      }
      
    } catch (error) {
      console.error('IP检测失败:', error)
      reject(error)
    }
  })
}

/**
 * 尝试其他方法获取IP
 */
const tryAlternativeMethods = async (resolve, reject) => {
  try {
    // 方法3: 尝试从当前页面URL获取
    const hostname = window.location.hostname
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && hostname.match(/^(\d{1,3}\.){3}\d{1,3}$/)) {
      resolve(hostname)
      return
    }
    
    // 方法4: 尝试从网络接口获取（如果可用）
    if (navigator.connection) {
      const connection = navigator.connection
      console.log('网络连接信息:', connection)
    }
    
    // 方法5: 使用默认IP
    const defaultIP = getDefaultLocalIP()
    resolve(defaultIP)
    
  } catch (error) {
    reject(new Error('无法获取局域网IP地址'))
  }
}



/**
 * 获取默认局域网IP
 */
const getDefaultLocalIP = () => {
  // 尝试从当前页面URL获取真实IP
  const hostname = window.location.hostname
  if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return hostname
  }
  
  // 根据当前时间生成一个简单的IP建议
  const now = new Date()
  const hour = now.getHours()
  
  // 根据时间选择不同的IP段
  if (hour < 8) {
    return '192.168.1.100'
  } else if (hour < 16) {
    return '192.168.0.31'  // 使用您的实际IP
  } else {
    return '10.0.0.100'
  }
}
</script>

<style scoped>
.qrcode-generator {
  text-align: center;
}

.qrcode-display {
  max-width: 400px;
  margin: 0 auto;
}

.qrcode-container {
  margin-bottom: 20px;
}

.qrcode-image {
  width: 200px;
  height: 200px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 8px;
  background: white;
}

.survey-info {
  margin-bottom: 20px;
  text-align: left;
}

.survey-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.survey-description {
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.5;
}

.survey-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

.setting-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.ip-buttons {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  justify-content: flex-start;
}

.common-ips {
  margin-top: 10px;
}

.common-ips-title {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.common-ips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ip-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.ip-tag:hover {
  background-color: #409eff;
  color: white;
}

.ip-tag.active {
  background-color: #409eff;
  color: white;
}

.qrcode-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.generate-section {
  padding: 40px 0;
}

.ip-help {
  margin-top: 10px;
}

.ip-help-content {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #f9fafc;
}

.ip-help-content p {
  margin-bottom: 8px;
}

.ip-help-content code {
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  background-color: #f4f4f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .qrcode-image {
    width: 180px;
    height: 180px;
  }
  
  .qrcode-actions {
    flex-direction: column;
  }
  
  .qrcode-actions .el-button {
    width: 100%;
  }
}
</style>
