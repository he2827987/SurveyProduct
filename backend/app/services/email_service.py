import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


async def send_verification_code_email(to_email: str, code: str) -> bool:
    subject = "问卷调查系统 - 密码重置验证码"
    body = f"您的验证码为：{code}\n\n验证码有效期为 {settings.RESET_CODE_EXPIRE_MINUTES} 分钟。\n如非本人操作，请忽略此邮件。"

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(f"[EMAIL MOCK] 验证码邮件未发送（SMTP未配置）。收件人: {to_email}, 验证码: {code}")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())

        logger.info(f"验证码邮件已发送至 {to_email}")
        return True
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False
