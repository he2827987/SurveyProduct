<template>
  <div class="qrcode-generator">
    <div class="qrcode-display" v-if="qrCodeUrl">
      <div class="qrcode-container">
        <img :src="qrCodeUrl" alt="调研二维码" class="qrcode-image" />
      </div>
      
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
        <div class="survey-url">
          <el-icon><Link /></el-icon>
          <span>{{ surveyFillUrl }}</span>
        </div>
      </div>
      
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
    
    <div v-else class="generate-section">
      <el-button type="primary" size="large" @click="generateQRCode" :loading="generating">
        <el-icon><Document /></el-icon>
        生成调研二维码
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as surveyApi from '@/api/survey'
import { Calendar, User, Download, CopyDocument, Share, Document, Link } from '@element-plus/icons-vue'
import { generateSurveyQRCode, downloadQRCode as downloadQRCodeUtil, getSurveyFillUrl } from '@/utils/qrcode'

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

const qrCodeUrl = ref('')
const generating = ref(false)
const downloading = ref(false)
const copying = ref(false)

const surveyFillUrl = computed(() => getSurveyFillUrl(props.surveyId))

const expireTime = computed(() => {
  return '永久有效'
})

const generateQRCode = async () => {
  try {
    generating.value = true
    await surveyApi.updateSurveyStatus(props.surveyId, {
      status: 'active'
    })
    const url = await generateSurveyQRCode(props.surveyId)
    qrCodeUrl.value = url
    ElMessage.success('二维码生成成功')
  } catch (error) {
    console.error('生成二维码失败:', error)
    ElMessage.error('生成二维码失败')
  } finally {
    generating.value = false
  }
}

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

const copyLink = async () => {
  try {
    copying.value = true
    await navigator.clipboard.writeText(surveyFillUrl.value)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制链接失败:', error)
    ElMessage.error('复制链接失败')
  } finally {
    copying.value = false
  }
}

const shareQRCode = async () => {
  try {
    if (navigator.share) {
      await navigator.share({
        title: props.surveyTitle,
        text: props.surveyDescription,
        url: surveyFillUrl.value
      })
    } else {
      await copyLink()
    }
  } catch (error) {
    console.error('分享失败:', error)
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

.survey-url {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #409EFF;
  word-break: break-all;
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
