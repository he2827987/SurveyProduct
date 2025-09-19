/**
 * @fileoverview 二维码工具模块
 * @description 提供二维码生成、下载、分享等功能的工具函数
 * @author Survey System Team
 * @version 1.0.0
 * @since 2024-01-01
 */

import QRCode from 'qrcode'
import html2canvas from 'html2canvas'

// ===== 基础二维码生成 =====

/**
 * 生成基础二维码
 * @param {string} text - 要编码的文本内容
 * @param {Object} options - 二维码选项
 * @param {number} options.width - 二维码宽度
 * @param {number} options.height - 二维码高度
 * @param {string} options.color - 二维码颜色
 * @param {string} options.backgroundColor - 背景颜色
 * @returns {Promise<string>} 二维码图片的Data URL
 */
export async function generateQRCode(text, options = {}) {
  const defaultOptions = {
    width: 200,
    height: 200,
    color: '#000000',
    backgroundColor: '#FFFFFF',
    errorCorrectionLevel: 'M',
    margin: 1
  }

  const qrOptions = { ...defaultOptions, ...options }
  
  try {
    const dataURL = await QRCode.toDataURL(text, qrOptions)
    return dataURL
  } catch (error) {
    console.error('生成二维码失败:', error)
    throw new Error('二维码生成失败')
  }
}

/**
 * 获取本机局域网IP地址
 * @returns {Promise<string>} 局域网IP地址
 */
async function getLocalIPAddress() {
  try {
    // 使用WebRTC来获取本机IP地址
    const rtc = new RTCPeerConnection({ iceServers: [] })
    const ips = []
    
    const promise = new Promise((resolve) => {
      rtc.onicecandidate = (event) => {
        if (event.candidate) {
          const candidate = event.candidate.candidate
          const ipMatch = candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/)
          if (ipMatch) {
            const ip = ipMatch[1]
            // 过滤掉本地回环地址，只保留局域网IP
            if (ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.')) {
              ips.push(ip)
            }
          }
        }
      }
    })
    
    rtc.createDataChannel('')
    rtc.createOffer().then(offer => rtc.setLocalDescription(offer))
    
    // 等待3秒或直到找到IP
    await Promise.race([
      promise,
      new Promise((_, reject) => setTimeout(() => reject(new Error('获取IP超时')), 3000))
    ])
    
    rtc.close()
    
    if (ips.length > 0) {
      console.log('检测到的局域网IP:', ips)
      return ips[0] // 返回第一个找到的局域网IP
    } else {
      throw new Error('未找到局域网IP地址')
    }
  } catch (error) {
    console.warn('无法自动获取局域网IP:', error)
    // 返回默认IP或环境变量中的IP
    return import.meta.env.VITE_LOCAL_NETWORK_IP || '192.168.1.100'
  }
}

/**
 * 获取局域网访问地址
 * @param {string} customIP - 自定义局域网IP地址
 * @returns {string} 局域网访问地址
 */
async function getLocalNetworkUrl(customIP = null) {
  // 获取当前页面的协议和端口
  const protocol = window.location.protocol
  const port = window.location.port
  
  let localNetworkIP
  if (customIP) {
    localNetworkIP = customIP
  } else {
    // 尝试自动获取本机IP
    localNetworkIP = await getLocalIPAddress()
  }
  
  return `${protocol}//${localNetworkIP}:${port}`
}

/**
 * 生成调研专用二维码
 * @param {number} surveyId - 调研ID
 * @param {Object} options - 二维码选项
 * @param {number} options.width - 二维码宽度
 * @param {number} options.height - 二维码高度
 * @param {string} options.color - 二维码颜色
 * @param {string} options.backgroundColor - 背景颜色
 * @param {boolean} options.useLocalNetwork - 是否使用局域网地址
 * @param {string} options.localNetworkIP - 自定义局域网IP地址
 * @returns {Promise<string>} 调研二维码的Data URL
 */
export async function generateSurveyQRCode(surveyId, options = {}) {
  const { useLocalNetwork = true, localNetworkIP = '', ...qrOptions } = options
  
  let baseUrl
  if (useLocalNetwork) {
    baseUrl = await getLocalNetworkUrl(localNetworkIP)
  } else {
    baseUrl = window.location.origin
  }
  
  const surveyUrl = `${baseUrl}/survey/fill/${surveyId}`
  console.log('生成的调研URL:', surveyUrl)
  
  return generateQRCode(surveyUrl, qrOptions)
}

// ===== 二维码下载功能 =====

/**
 * 下载二维码图片
 * @param {string} qrCodeUrl - 二维码图片URL
 * @param {string} filename - 文件名
 * @returns {Promise<void>}
 */
export async function downloadQRCode(qrCodeUrl, filename = 'qrcode.png') {
  try {
    const link = document.createElement('a')
    link.href = qrCodeUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('下载二维码失败:', error)
    throw new Error('二维码下载失败')
  }
}

/**
 * 将DOM元素转换为图片并下载
 * @param {HTMLElement} element - 要转换的DOM元素
 * @param {string} filename - 文件名
 * @param {Object} options - html2canvas选项
 * @returns {Promise<void>}
 */
export async function downloadElementAsImage(element, filename = 'image.png', options = {}) {
  try {
    const canvas = await html2canvas(element, {
      backgroundColor: '#FFFFFF',
      scale: 2,
      ...options
    })
    
    const dataURL = canvas.toDataURL('image/png')
    await downloadQRCode(dataURL, filename)
  } catch (error) {
    console.error('转换DOM为图片失败:', error)
    throw new Error('图片转换失败')
  }
}

// ===== 组合功能 =====

/**
 * 生成并下载二维码
 * @param {string} text - 要编码的文本
 * @param {string} filename - 文件名
 * @param {Object} options - 二维码选项
 * @returns {Promise<void>}
 */
export async function generateAndDownloadQRCode(text, filename, options = {}) {
  const qrCodeUrl = await generateQRCode(text, options)
  await downloadQRCode(qrCodeUrl, filename)
}

/**
 * 生成并下载调研二维码
 * @param {number} surveyId - 调研ID
 * @param {string} filename - 文件名
 * @param {Object} options - 二维码选项
 * @returns {Promise<void>}
 */
export async function generateAndDownloadSurveyQRCode(surveyId, filename, options = {}) {
  const qrCodeUrl = await generateSurveyQRCode(surveyId, options)
  await downloadQRCode(qrCodeUrl, filename)
}

// ===== 二维码验证 =====

/**
 * 验证调研二维码URL
 * @param {string} url - 要验证的URL
 * @returns {boolean} 是否为有效的调研二维码URL
 */
export function validateSurveyQRCode(url) {
  try {
    const urlObj = new URL(url)
    const pathParts = urlObj.pathname.split('/')
    return pathParts.includes('survey') && pathParts.includes('fill')
  } catch (error) {
    return false
  }
}
