import QRCode from 'qrcode'
import html2canvas from 'html2canvas'

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

export async function generateSurveyQRCode(surveyId, options = {}) {
  const { ...qrOptions } = options
  const baseUrl = window.location.origin
  const surveyUrl = `${baseUrl}/survey/fill/${surveyId}`
  console.log('生成的调研URL:', surveyUrl)
  return generateQRCode(surveyUrl, qrOptions)
}

export function getSurveyFillUrl(surveyId) {
  return `${window.location.origin}/survey/fill/${surveyId}`
}

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

export async function generateAndDownloadQRCode(text, filename, options = {}) {
  const qrCodeUrl = await generateQRCode(text, options)
  await downloadQRCode(qrCodeUrl, filename)
}

export async function generateAndDownloadSurveyQRCode(surveyId, filename, options = {}) {
  const qrCodeUrl = await generateSurveyQRCode(surveyId, options)
  await downloadQRCode(qrCodeUrl, filename)
}

export function validateSurveyQRCode(url) {
  try {
    const urlObj = new URL(url)
    const pathParts = urlObj.pathname.split('/')
    return pathParts.includes('survey') && pathParts.includes('fill')
  } catch (error) {
    return false
  }
}
