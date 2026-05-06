import logging
from app.config import settings

logger = logging.getLogger(__name__)

RESEND_API_KEY = settings.RESEND_API_KEY
SITE_URL = settings.SITE_URL


async def send_forgot_password_email(to_email: str, code: str, reset_link: str) -> bool:
    if not RESEND_API_KEY:
        logger.warning(f"[EMAIL MOCK] 邮件未发送（Resend未配置）。收件人: {to_email}, 验证码: {code}, 重置链接: {reset_link}")
        return True

    try:
        import resend
        resend.api_key = RESEND_API_KEY

        html = f"""
        <div style="max-width:480px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#333;">
          <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:32px 24px;border-radius:12px 12px 0 0;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:24px;">密码重置请求</h1>
          </div>
          <div style="background:#fff;padding:32px 24px;border:1px solid #e8e8e8;border-top:none;border-radius:0 0 12px 12px;">
            <p style="font-size:16px;line-height:1.6;">您好，</p>
            <p style="font-size:16px;line-height:1.6;">我们收到了您的密码重置请求。请使用以下验证码完成重置：</p>
            <div style="background:#f7f7f7;border-radius:8px;padding:20px;text-align:center;margin:20px 0;">
              <span style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#667eea;">{code}</span>
            </div>
            <p style="font-size:16px;line-height:1.6;">或者点击下方按钮直接重置密码：</p>
            <div style="text-align:center;margin:24px 0;">
              <a href="{reset_link}" style="display:inline-block;background:#667eea;color:#fff;text-decoration:none;padding:12px 32px;border-radius:6px;font-size:16px;font-weight:500;">
                重置密码
              </a>
            </div>
            <p style="font-size:14px;color:#999;line-height:1.6;">链接有效期为 {settings.RESET_CODE_EXPIRE_MINUTES} 分钟。如非本人操作，请忽略此邮件。</p>
          </div>
        </div>
        """

        resend.Emails.send({
            "from": f"调研系统 <{settings.SMTP_FROM}>",
            "to": [to_email],
            "subject": "调研系统 - 密码重置",
            "html": html,
        })

        logger.info(f"密码重置邮件已发送至 {to_email}")
        return True
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False
